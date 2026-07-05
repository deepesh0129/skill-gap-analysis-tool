"""
pdf_report.py
--------------
Generates a downloadable, personalized "Career Roadmap Report" PDF using
ReportLab, as specified in the brief's tech stack.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime


def build_report(path, profile, gap_result, readiness, recommended_skills,
                  project_recs, certifications, peer_position=None):
    doc = SimpleDocTemplate(path, pagesize=A4,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#1f2937"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#2563eb"))
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("Personalized Career Roadmap Report", title_style))
    story.append(Paragraph(datetime.now().strftime("Generated on %d %b %Y"), body))
    story.append(Spacer(1, 0.6 * cm))

    # Profile table
    profile_data = [
        ["Name", profile.name],
        ["Department", profile.department],
        ["Status", profile.status],
        ["Target Role", profile.target_role],
    ]
    t = Table(profile_data, colWidths=[4 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e5e7eb")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph("Skill Match Summary", h2))
    story.append(Paragraph(
        f"Weighted Skill Match Score: <b>{gap_result.weighted_match_score}%</b> "
        f"(simple match: {gap_result.raw_match_score}%)", body))
    story.append(Paragraph(
        f"Career Readiness Score: <b>{readiness['readiness_score']}%</b> "
        f"&mdash; Band: <b>{readiness['band']}</b>", body))
    if peer_position:
        story.append(Paragraph(f"Peer comparison: <b>{peer_position}</b> relative to other assessed students.", body))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Matched Skills", h2))
    story.append(Paragraph(", ".join(gap_result.matched_skills) or "None yet", body))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Missing Skills", h2))
    story.append(Paragraph(", ".join(gap_result.missing_skills) or "None — great job!", body))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Recommended Skills to Learn (priority order)", h2))
    items = [ListItem(Paragraph(f"{r['skill']} — priority weight {r['priority']}/5 "
                                 f"({r['level_needed']} level)", body)) for r in recommended_skills]
    if items:
        story.append(ListFlowable(items, bulletType="1"))
    else:
        story.append(Paragraph("No missing high-priority skills detected.", body))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(f"Recommended Projects (suggested focus: {project_recs['focus_level'].title()})", h2))
    for level in ["beginner", "intermediate", "advanced"]:
        story.append(Paragraph(f"<b>{level.title()}</b>", body))
        items = [ListItem(Paragraph(p, body)) for p in project_recs[level]]
        story.append(ListFlowable(items, bulletType="bullet"))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Recommended Certifications", h2))
    items = [ListItem(Paragraph(c, body)) for c in certifications]
    story.append(ListFlowable(items, bulletType="bullet"))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("AI-Generated Career Advice", h2))
    story.append(Paragraph(readiness["advice"], body))

    doc.build(story)
    return path
