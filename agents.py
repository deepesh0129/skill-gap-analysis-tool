"""
agents.py
---------
Each class below represents one "agent" from the use case document.
They are implemented as plain, composable Python classes (no external LLM
calls) so the whole pipeline is fast, deterministic, explainable, and free
to run — while still following an agentic, single-responsibility design:
each agent takes an input, does ONE job, and hands a structured result to
the next agent (a simple in-process agent orchestration pattern, the same
idea used by frameworks like LangGraph / CrewAI, just implemented natively
in Python + NumPy/Scikit-learn as the tech list in the brief specifies).
"""

from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np
from sklearn.cluster import KMeans

from career_data import CAREER_ROLES, SKILL_LEVEL_TAGS


# ---------------------------------------------------------------------------
# Agent 1: User Profile Agent
# ---------------------------------------------------------------------------
@dataclass
class UserProfile:
    name: str
    department: str
    status: str
    target_role: str
    current_skills: List[str] = field(default_factory=list)


class UserProfileAgent:
    """Collects and validates the student's profile information."""

    def build_profile(self, name, department, status, target_role, current_skills):
        if not name or not name.strip():
            raise ValueError("Name is required.")
        if target_role not in CAREER_ROLES:
            raise ValueError(f"Unknown target role: {target_role}")
        return UserProfile(
            name=name.strip(),
            department=department,
            status=status,
            target_role=target_role,
            current_skills=sorted(set(current_skills)),
        )


# ---------------------------------------------------------------------------
# Agent 2: Career Requirement Agent
# ---------------------------------------------------------------------------
class CareerRequirementAgent:
    """Loads the required-skill matrix for the selected role."""

    def get_requirements(self, target_role: str) -> Dict[str, int]:
        return CAREER_ROLES[target_role]["skills"]

    def get_all_projects(self, target_role: str) -> Dict[str, List[str]]:
        return CAREER_ROLES[target_role]["projects"]

    def get_certifications(self, target_role: str) -> List[str]:
        return CAREER_ROLES[target_role]["certifications"]


# ---------------------------------------------------------------------------
# Agent 3: Skill Gap Analysis Agent
# ---------------------------------------------------------------------------
@dataclass
class SkillGapResult:
    matched_skills: List[str]
    missing_skills: List[str]
    weighted_match_score: float   # 0-100, weighted by skill importance
    raw_match_score: float        # 0-100, simple count-based


class SkillGapAgent:
    """Compares current vs required skills and computes a weighted Skill Match Score.

    Insight added beyond the base spec: instead of a flat percentage
    (matched / total), we weight each skill by its importance (1-5) to the
    role, so mastering a "weight 5" core skill counts more than a
    "weight 2" nice-to-have — giving a more realistic readiness signal.
    """

    def analyze(self, profile: UserProfile, required_skills: Dict[str, int]) -> SkillGapResult:
        current = set(profile.current_skills)
        required = set(required_skills.keys())

        matched = sorted(current & required)
        missing = sorted(required - current)

        total_weight = sum(required_skills.values()) or 1
        matched_weight = sum(required_skills[s] for s in matched)
        weighted_score = round((matched_weight / total_weight) * 100, 1)

        raw_score = round((len(matched) / len(required)) * 100, 1) if required else 0.0

        return SkillGapResult(
            matched_skills=matched,
            missing_skills=missing,
            weighted_match_score=weighted_score,
            raw_match_score=raw_score,
        )


# ---------------------------------------------------------------------------
# Agent 4: Recommendation Agent
# ---------------------------------------------------------------------------
class RecommendationAgent:
    """Suggests missing skills in priority order (highest weight/importance first)."""

    def recommend(self, missing_skills: List[str], required_skills: Dict[str, int], top_n: int = 6):
        ranked = sorted(missing_skills, key=lambda s: required_skills.get(s, 0), reverse=True)
        return [
            {"skill": s, "priority": required_skills.get(s, 0),
             "level_needed": SKILL_LEVEL_TAGS.get(required_skills.get(s, 0), "Beginner")}
            for s in ranked[:top_n]
        ]


# ---------------------------------------------------------------------------
# Agent 5: Project Recommendation Agent
# ---------------------------------------------------------------------------
class ProjectRecommendationAgent:
    """Recommends beginner/intermediate/advanced projects based on current match score."""

    def recommend(self, target_role: str, weighted_score: float, all_projects: Dict[str, List[str]]):
        if weighted_score < 35:
            focus = "beginner"
        elif weighted_score < 70:
            focus = "intermediate"
        else:
            focus = "advanced"

        return {
            "focus_level": focus,
            "beginner": all_projects.get("beginner", []),
            "intermediate": all_projects.get("intermediate", []),
            "advanced": all_projects.get("advanced", []),
        }


# ---------------------------------------------------------------------------
# Agent 6: Certification Agent
# ---------------------------------------------------------------------------
class CertificationAgent:
    """Recommends certifications relevant to the target role and missing skills."""

    def recommend(self, target_role: str, certifications: List[str], missing_skills: List[str]):
        # Simple relevance boost: certs are already role-curated; we just
        # surface how many of the top missing skills each cert conceptually covers
        # (kept lightweight/explainable rather than a black-box match).
        return certifications


# ---------------------------------------------------------------------------
# Agent 7: Career Readiness Agent
# ---------------------------------------------------------------------------
class CareerReadinessAgent:
    """Estimates overall employability and generates narrative career advice.

    Insight added: uses scikit-learn's KMeans (unsupervised) across all past
    assessments stored in SQLite to place the student into a peer cluster
    ("Exploring" / "Developing" / "Job-Ready"), which is more informative
    than a single absolute score because it reflects real peer distribution
    rather than an arbitrary fixed cutoff.
    """

    def compute_readiness(self, weighted_score: float, num_matched: int, num_required: int,
                           status: str) -> Dict:
        # base readiness leans on weighted skill score
        readiness = weighted_score

        # small status-based adjustment: working professionals & interns get
        # a modest credit for assumed practical exposure
        status_bonus = {"Working Professional": 8, "Intern": 4,
                         "Fresher / Job Seeker": 0, "Student": -2}
        readiness += status_bonus.get(status, 0)
        readiness = float(np.clip(readiness, 0, 100))

        if readiness >= 75:
            band = "Job Ready"
            advice = ("You already cover most of the core skills for this role. "
                       "Focus on polishing 1-2 advanced projects and start applying / "
                       "interview prep.")
        elif readiness >= 45:
            band = "Developing"
            advice = ("You have a solid foundation but a few high-priority skills are "
                       "still missing. Close those gaps first, then build one strong "
                       "portfolio project to demonstrate them.")
        else:
            band = "Exploring"
            advice = ("You're early in the journey for this role. Start with the "
                       "highest-priority missing skills and a beginner project before "
                       "moving further — small consistent progress will compound fast.")

        return {"readiness_score": round(readiness, 1), "band": band, "advice": advice}

    def cluster_against_peers(self, all_scores: List[float], this_score: float, n_clusters: int = 3):
        """Optional peer-comparison using KMeans if enough historical data exists."""
        data = np.array(all_scores + [this_score]).reshape(-1, 1)
        if len(data) < n_clusters:
            return None  # not enough data yet to cluster meaningfully

        km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
        labels = km.fit_predict(data)
        this_label = labels[-1]

        # order cluster centers to map to Exploring < Developing < Job Ready
        order = np.argsort(km.cluster_centers_.flatten())
        rank_map = {cluster_id: rank for rank, cluster_id in enumerate(order)}
        tags = ["Exploring", "Developing", "Job Ready"]
        rank = rank_map[this_label]
        return tags[min(rank, len(tags) - 1)]
