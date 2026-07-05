"""
app.py
------
Streamlit front-end implementing the exact user flow from the brief:

  1. Welcome screen -> Start Assessment
  2. Enter Full Name
  3. Select Department
  4. Select Current Status
  5. Select Target Career Role
  6. Select Current Skills (checklist)
  7. Analyze My Skills -> runs the 7-agent pipeline -> Results screen

Plus an extra "Insights Dashboard" tab (Plotly, inside Streamlit) that acts
as a live substitute for the Power BI dashboard described in the brief,
and a CSV export button so the same data can be loaded straight into an
actual Power BI report.

Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os

from career_data import CAREER_ROLES, DEPARTMENTS, STATUS_OPTIONS
from agents import (
    UserProfileAgent, CareerRequirementAgent, SkillGapAgent,
    RecommendationAgent, ProjectRecommendationAgent, CertificationAgent,
    CareerReadinessAgent,
)
import database as db
from pdf_report import build_report

st.set_page_config(page_title="Agentic AI Career Guidance", page_icon="🎯", layout="wide")
db.init_db()

# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "form" not in st.session_state:
    st.session_state.form = {}
if "results" not in st.session_state:
    st.session_state.results = None

AGENTS = dict(
    profile=UserProfileAgent(),
    requirement=CareerRequirementAgent(),
    gap=SkillGapAgent(),
    recommend=RecommendationAgent(),
    project=ProjectRecommendationAgent(),
    cert=CertificationAgent(),
    readiness=CareerReadinessAgent(),
)


def go(step):
    st.session_state.step = step


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🎯 Career AI")
    st.caption("Agentic AI Skill Gap Analysis")
    page = st.radio("Navigate", ["Assessment", "Insights Dashboard"], index=0)
    st.divider()
    st.caption("7 agents run behind the scenes:")
    st.markdown(
        "1. User Profile Agent\n"
        "2. Career Requirement Agent\n"
        "3. Skill Gap Analysis Agent\n"
        "4. Recommendation Agent\n"
        "5. Project Recommendation Agent\n"
        "6. Certification Agent\n"
        "7. Career Readiness Agent"
    )

# ===========================================================================
# PAGE: Insights Dashboard  (Power BI stand-in)
# ===========================================================================
if page == "Insights Dashboard":
    st.header("📊 Insights Dashboard")
    st.caption("Live substitute for the Power BI dashboard in the brief — "
               "same underlying data, exportable to CSV for an actual Power BI report.")

    rows = db.fetch_all_assessments()
    if not rows:
        st.info("No assessments yet. Complete one under the **Assessment** tab first.")
    else:
        df = pd.DataFrame(rows)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Assessments", len(df))
        c2.metric("Avg. Skill Match", f"{df['weighted_match_score'].mean():.1f}%")
        c3.metric("Avg. Readiness", f"{df['readiness_score'].mean():.1f}%")
        c4.metric("Roles Explored", df["target_role"].nunique())

        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(df, x="target_role", color="readiness_band",
                                title="Assessments by Target Role & Readiness Band")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.box(df, x="target_role", y="weighted_match_score",
                           title="Skill Match Distribution by Role")
            st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.scatter(df, x="created_at", y="readiness_score", color="target_role",
                           hover_data=["name"], title="Readiness Score Over Time")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Raw Data")
        st.dataframe(df, use_container_width=True)

        csv_path = db.export_to_csv()
        with open(csv_path, "rb") as f:
            st.download_button("⬇️ Export CSV (for Power BI / Excel)", f,
                                file_name="assessments_export.csv", mime="text/csv")

# ===========================================================================
# PAGE: Assessment wizard
# ===========================================================================
else:
    step = st.session_state.step

    # --- Step 1: Welcome -----------------------------------------------
    if step == "welcome":
        st.title("🎯 Agentic AI Skill Gap Analysis & Career Guidance")
        st.write(
            "Find out exactly what's standing between you and your dream role. "
            "This assessment compares your current skills against real industry "
            "requirements and builds you a personalized learning roadmap — "
            "powered by a 7-agent AI workflow."
        )
        st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200",
                  use_container_width=True) if False else None
        if st.button("🚀 Start Assessment", type="primary"):
            go("name")
            st.rerun()

    # --- Step 2: Name -----------------------------------------------
    elif step == "name":
        st.subheader("Step 1 of 5 — About You")
        name = st.text_input("Full Name", value=st.session_state.form.get("name", ""))
        c1, c2 = st.columns([1, 5])
        if c1.button("← Back"):
            go("welcome"); st.rerun()
        if c2.button("Next →", type="primary"):
            if name.strip():
                st.session_state.form["name"] = name.strip()
                go("department"); st.rerun()
            else:
                st.warning("Please enter your name.")

    # --- Step 3: Department -----------------------------------------
    elif step == "department":
        st.subheader("Step 2 of 5 — Department")
        dept = st.selectbox("Select Department", DEPARTMENTS,
                             index=DEPARTMENTS.index(st.session_state.form["department"])
                             if "department" in st.session_state.form else 0)
        c1, c2 = st.columns([1, 5])
        if c1.button("← Back"):
            go("name"); st.rerun()
        if c2.button("Next →", type="primary"):
            st.session_state.form["department"] = dept
            go("status"); st.rerun()

    # --- Step 4: Status -----------------------------------------------
    elif step == "status":
        st.subheader("Step 3 of 5 — Current Status")
        status = st.selectbox("Select Current Status", STATUS_OPTIONS,
                               index=STATUS_OPTIONS.index(st.session_state.form["status"])
                               if "status" in st.session_state.form else 0)
        c1, c2 = st.columns([1, 5])
        if c1.button("← Back"):
            go("department"); st.rerun()
        if c2.button("Next →", type="primary"):
            st.session_state.form["status"] = status
            go("role"); st.rerun()

    # --- Step 5: Target Role -----------------------------------------
    elif step == "role":
        st.subheader("Step 4 of 5 — Target Career Role")
        roles = list(CAREER_ROLES.keys())
        role = st.selectbox("Select Target Career Role", roles,
                             index=roles.index(st.session_state.form["target_role"])
                             if "target_role" in st.session_state.form else 0)
        with st.expander("See required skills for this role"):
            skills = CAREER_ROLES[role]["skills"]
            st.write(", ".join(f"{s} (priority {w}/5)" for s, w in
                                sorted(skills.items(), key=lambda x: -x[1])))
        c1, c2 = st.columns([1, 5])
        if c1.button("← Back"):
            go("status"); st.rerun()
        if c2.button("Next →", type="primary"):
            st.session_state.form["target_role"] = role
            go("skills"); st.rerun()

    # --- Step 6: Skills checklist -----------------------------------
    elif step == "skills":
        st.subheader("Step 5 of 5 — Your Current Skills")
        role = st.session_state.form["target_role"]
        all_possible_skills = sorted(CAREER_ROLES[role]["skills"].keys())
        st.caption(f"Check everything you're already comfortable with for **{role}**.")

        prev_selected = set(st.session_state.form.get("current_skills", []))
        cols = st.columns(3)
        selected = []
        for i, skill in enumerate(all_possible_skills):
            with cols[i % 3]:
                if st.checkbox(skill, value=skill in prev_selected, key=f"skill_{skill}"):
                    selected.append(skill)

        extra = st.text_input("Other skills not listed above (comma-separated, optional)")
        if extra:
            selected += [s.strip() for s in extra.split(",") if s.strip()]

        c1, c2 = st.columns([1, 5])
        if c1.button("← Back"):
            go("role"); st.rerun()
        if c2.button("✅ Analyze My Skills", type="primary"):
            st.session_state.form["current_skills"] = selected
            go("analyze"); st.rerun()

    # --- Step 7: Run the agent pipeline ------------------------------
    elif step == "analyze":
        with st.spinner("Running the 7-agent analysis pipeline..."):
            f = st.session_state.form

            profile = AGENTS["profile"].build_profile(
                f["name"], f["department"], f["status"], f["target_role"], f["current_skills"]
            )
            required_skills = AGENTS["requirement"].get_requirements(profile.target_role)
            all_projects = AGENTS["requirement"].get_all_projects(profile.target_role)
            certifications = AGENTS["requirement"].get_certifications(profile.target_role)

            gap_result = AGENTS["gap"].analyze(profile, required_skills)
            recommended_skills = AGENTS["recommend"].recommend(
                gap_result.missing_skills, required_skills
            )
            project_recs = AGENTS["project"].recommend(
                profile.target_role, gap_result.weighted_match_score, all_projects
            )
            cert_recs = AGENTS["cert"].recommend(
                profile.target_role, certifications, gap_result.missing_skills
            )
            readiness = AGENTS["readiness"].compute_readiness(
                gap_result.weighted_match_score, len(gap_result.matched_skills),
                len(required_skills), profile.status
            )

            db.save_assessment(profile, gap_result, readiness)
            peer_scores = db.fetch_scores_for_role(profile.target_role)
            peer_position = AGENTS["readiness"].cluster_against_peers(
                peer_scores[:-1] if peer_scores else [], gap_result.weighted_match_score
            )

            st.session_state.results = dict(
                profile=profile, gap_result=gap_result, recommended_skills=recommended_skills,
                project_recs=project_recs, cert_recs=cert_recs, readiness=readiness,
                required_skills=required_skills, peer_position=peer_position,
            )
        go("results")
        st.rerun()

    # --- Results screen -----------------------------------------------
    elif step == "results":
        r = st.session_state.results
        profile, gap, readiness = r["profile"], r["gap_result"], r["readiness"]

        st.title(f"Results for {profile.name}")
        st.caption(f"{profile.department} · {profile.status} · Target: **{profile.target_role}**")

        c1, c2, c3 = st.columns(3)
        c1.metric("Weighted Skill Match", f"{gap.weighted_match_score}%")
        c2.metric("Simple Skill Match", f"{gap.raw_match_score}%")
        c3.metric("Career Readiness", f"{readiness['readiness_score']}%", readiness["band"])

        gcol, bcol = st.columns([1, 1])
        with gcol:
            raw_readiness = readiness.get("readiness_score")
            try:
                readiness_value = float(raw_readiness)
            except (TypeError, ValueError):
                readiness_value = 0.0

            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=readiness_value,
                title={"text": "Career Readiness"},
                gauge={"axis": {"range": [0, 100]},
                       "bar": {"color": "#2563eb"},
                       "steps": [
                           {"range": [0, 45], "color": "#fee2e2"},
                           {"range": [45, 75], "color": "#fef9c3"},
                           {"range": [75, 100], "color": "#dcfce7"},
                       ]}))
            st.plotly_chart(fig, use_container_width=True)
        with bcol:
            skills_df = pd.DataFrame({
                "Skill": list(r["required_skills"].keys()),
                "Status": ["Have" if s in gap.matched_skills else "Missing"
                           for s in r["required_skills"].keys()],
                "Priority": list(r["required_skills"].values()),
            })
            fig2 = px.bar(skills_df.sort_values("Priority", ascending=True),
                          x="Priority", y="Skill", color="Status", orientation="h",
                          color_discrete_map={"Have": "#22c55e", "Missing": "#ef4444"},
                          title="Current vs Required Skills")
            st.plotly_chart(fig2, use_container_width=True)

        if r["peer_position"]:
            st.info(f"📈 Peer comparison: relative to other students who assessed for "
                     f"**{profile.target_role}**, you fall in the **{r['peer_position']}** cluster.")

        st.subheader("✅ Matched Skills")
        st.write(", ".join(gap.matched_skills) or "None yet — that's okay, everyone starts somewhere!")

        st.subheader("🎯 Missing Skills (priority order)")
        for item in r["recommended_skills"]:
            st.write(f"- **{item['skill']}** — priority {item['priority']}/5 ({item['level_needed']} level)")

        st.subheader("🛠️ Recommended Projects")
        tabs = st.tabs(["Beginner", "Intermediate", "Advanced"])
        for tab, level in zip(tabs, ["beginner", "intermediate", "advanced"]):
            with tab:
                for p in r["project_recs"][level]:
                    st.write(f"- {p}")
        st.caption(f"Suggested current focus level: **{r['project_recs']['focus_level'].title()}**")

        st.subheader("📜 Recommended Certifications")
        for c in r["cert_recs"]:
            st.write(f"- {c}")

        st.subheader("🧭 AI-Generated Career Advice")
        st.success(readiness["advice"])

        # PDF export
        out_path = os.path.join(os.path.dirname(__file__), f"{profile.name.replace(' ', '_')}_career_report.pdf")
        build_report(out_path, profile, gap, readiness, r["recommended_skills"],
                     r["project_recs"], r["cert_recs"], r["peer_position"])
        with open(out_path, "rb") as f:
            st.download_button("⬇️ Download Career Roadmap PDF", f,
                                file_name=os.path.basename(out_path), mime="application/pdf")

        st.divider()
        if st.button("🔁 Run Another Assessment"):
            st.session_state.form = {}
            st.session_state.results = None
            go("welcome")
            st.rerun()
