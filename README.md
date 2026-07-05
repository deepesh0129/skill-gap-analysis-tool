# Agentic AI Skill Gap Analysis & Personalized Career Guidance System

A working implementation of the use case: a Streamlit app that walks a student
through a 7-step assessment, runs a 7-agent pipeline to compare their skills
against real industry requirements, and produces a personalized roadmap
(missing skills, projects, certifications, readiness score, PDF report) —
backed by SQLite and with a Plotly "Insights Dashboard" that mirrors the
Power BI dashboard from the brief.

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Project structure

```
agentic_career_ai/
├── app.py             # Streamlit UI — the full user flow + results + dashboard
├── agents.py          # The 7 agents (UserProfile, CareerRequirement, SkillGap,
│                       #   Recommendation, ProjectRecommendation, Certification,
│                       #   CareerReadiness)
├── career_data.py      # Knowledge base: 8 roles x weighted required skills,
│                       #   projects, certifications, departments
├── database.py         # SQLite persistence + CSV export for Power BI
├── pdf_report.py        # ReportLab personalized PDF roadmap generator
└── requirements.txt
```

## How the 7 agents map to the brief

| # | Agent | What it does here |
|---|-------|--------------------|
| 1 | User Profile Agent | Validates and packages name/department/status/role/skills |
| 2 | Career Requirement Agent | Looks up the required-skill matrix for the chosen role |
| 3 | Skill Gap Analysis Agent | Computes matched/missing skills + a **weighted** match score |
| 4 | Recommendation Agent | Ranks missing skills by importance (priority order) |
| 5 | Project Recommendation Agent | Picks beginner/intermediate/advanced projects based on current score |
| 6 | Certification Agent | Surfaces role-relevant certifications |
| 7 | Career Readiness Agent | Blends skill score + status into a readiness % and a peer-cluster comparison |

## Insights / design decisions added beyond the base brief

1. **Weighted skill matching, not just a headcount.** Each required skill has
   an importance weight (1–5). Two students missing the same *number* of
   skills can have very different real employability — missing "SQL" (weight
   5 for a Data Analyst) matters more than missing "A/B Testing" (weight 2).
   The dashboard shows both the weighted score and the simple raw score so
   the difference is visible and explainable, not a black box.

2. **Peer clustering with scikit-learn (KMeans).** Rather than a single
   arbitrary cutoff ("readiness ≥ 70 = job ready"), once enough historical
   assessments exist for a role, the app clusters all stored scores into
   3 groups (Exploring / Developing / Job Ready) and reports which cluster
   the student actually falls into. This scales with real data instead of a
   guessed threshold, and directly uses the Scikit-learn dependency called
   out in the brief's tech list.

3. **Status-aware readiness adjustment.** A working professional and a
   first-year student with an identical skill checklist don't have identical
   job readiness in practice, so a small, transparent bonus/penalty is
   applied by current status (documented in `agents.py`, not hidden).

4. **Project & certification recommendations react to current level**,
   instead of always showing the same static list — a student under 35%
   match is nudged toward beginner projects first; over 70% gets pointed at
   advanced/portfolio-grade work.

5. **Power BI, made practical inside a sandbox.** Since Power BI itself is a
   separate Windows/desktop BI tool and can't be built or hosted here, the
   app ships two things that make the brief's dashboard section real:
   - An in-app **Insights Dashboard** (Plotly) showing the exact metrics the
     brief lists (skill match, current vs required, missing skills, readiness
     gauge, distribution by role) so the reporting layer is genuinely usable
     today.
   - A **one-click CSV export** of every stored assessment (`assessments_export.csv`),
     which can be dropped straight into Power BI's *Get Data → Text/CSV* (or
     point Power BI at `career_assessments.db` via an ODBC SQLite driver) to
     rebuild the exact dashboard described in the brief with your own
     historical data.

6. **Everything is deterministic and explainable.** No external LLM calls are
   used for the core logic — every score, gap, and recommendation can be
   traced back to a simple, inspectable rule. This keeps the app free to run,
   fast, and easy to defend in a project demo/viva ("why did it recommend
   this?" always has a one-line answer). If you want to add generative
   "AI career advice" text using an actual LLM later, `CareerReadinessAgent.compute_readiness()`
   is the one place to swap in an API call — the rest of the pipeline is
   already decoupled from it.

## Extending it

- **Add a role:** add one entry to `CAREER_ROLES` in `career_data.py`
  (skills+weights, projects, certifications). Everything else (UI, agents,
  scoring, PDF, dashboard) picks it up automatically.
- **Add authentication / multi-user history:** the SQLite schema already
  stores every assessment with a timestamp; add a `user_id` column and a
  login step in `app.py` to support returning users tracking progress over
  time.
- **Swap the readiness narrative for a real LLM call:** replace the `advice`
  string logic in `CareerReadinessAgent` with a call to the Anthropic API
  (or any LLM), passing in the computed `readiness_score`, `matched_skills`,
  and `missing_skills` as context.
