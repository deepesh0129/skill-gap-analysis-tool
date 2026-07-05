"""
database.py
------------
Lightweight SQLite persistence layer.

Every completed assessment is stored as one row. This gives the app:
  1. A history screen per student.
  2. Aggregate data across all students, which is exactly what the
     Power BI dashboard mentioned in the brief needs (User Profile,
     Skill Match, Missing Skills, Readiness Gauge, etc). Since Power BI
     can't run inside this sandbox, this module also exposes an
     `export_to_csv()` helper — point Power BI's "Get Data > Text/CSV"
     (or an ODBC/SQLite connector) at the exported file / .db to rebuild
     the dashboard described in the brief.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "career_assessments.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            status TEXT,
            target_role TEXT,
            current_skills TEXT,       -- JSON list
            matched_skills TEXT,       -- JSON list
            missing_skills TEXT,       -- JSON list
            weighted_match_score REAL,
            raw_match_score REAL,
            readiness_score REAL,
            readiness_band TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_assessment(profile, gap_result, readiness):
    conn = get_connection()
    conn.execute(
        """INSERT INTO assessments
           (name, department, status, target_role, current_skills, matched_skills,
            missing_skills, weighted_match_score, raw_match_score, readiness_score,
            readiness_band, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            profile.name, profile.department, profile.status, profile.target_role,
            json.dumps(profile.current_skills), json.dumps(gap_result.matched_skills),
            json.dumps(gap_result.missing_skills), gap_result.weighted_match_score,
            gap_result.raw_match_score, readiness["readiness_score"], readiness["band"],
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def fetch_all_assessments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM assessments ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_scores_for_role(target_role):
    conn = get_connection()
    rows = conn.execute(
        "SELECT weighted_match_score FROM assessments WHERE target_role = ?",
        (target_role,),
    ).fetchall()
    conn.close()
    return [r["weighted_match_score"] for r in rows]


def export_to_csv(path=None):
    import pandas as pd
    path = path or os.path.join(os.path.dirname(__file__), "assessments_export.csv")
    data = fetch_all_assessments()
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return path
