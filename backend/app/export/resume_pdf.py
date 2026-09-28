"""
Generates a downloadable PDF of the resume with validated bullet
rewrites applied.

This is a reconstruction, not a copy of the original file's layout —
documented MVP limitation. It rebuilds a clean, ATS-friendly single-
column layout (no tables, no columns, no images) using the resume's
own parsed content, which is itself a formatting improvement over
resumes that failed the ATS check for those exact reasons.
"""
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

from app.feedback.prompt_builder import collect_bullets_with_ids


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="NameHeader", fontSize=18, leading=22, spaceAfter=2, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="ContactLine", fontSize=9.5, leading=13, textColor="#444444", spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", fontSize=12, leading=16, spaceBefore=12, spaceAfter=4,
        textColor="#1B2430", borderColor="#DADFE3",
    ))
    styles.add(ParagraphStyle(
        name="EntryHeader", fontSize=10.5, leading=14, spaceBefore=6, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="BulletText", fontSize=10, leading=13.5, spaceAfter=2,
    ))
    return styles


def build_resume_pdf(parsed_json: dict, bullet_rewrites: list) -> bytes:
    """
    parsed_json: the resume's stored parsed_json (contact, skills, experience, education)
    bullet_rewrites: list of {bullet_id, improved} from a validated /feedback response —
                      only rewrites the user has already seen and approved get applied.
    """
    rewrite_map = {r["bullet_id"]: r["improved"] for r in bullet_rewrites if r.get("bullet_id")}
    known_bullets = collect_bullets_with_ids(parsed_json.get("experience", []))
    # Map each bullet's original text -> its id, so we can substitute
    # improved text back into the right spot when rebuilding entries.
    bullet_id_by_text = {b["text"]: b["id"] for b in known_bullets}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
    )
    styles = _build_styles()
    story = []

    contact = parsed_json.get("contact", {})
    if contact.get("name"):
        story.append(Paragraph(contact["name"], styles["NameHeader"]))
    contact_bits = [v for v in [contact.get("email"), contact.get("phone"),
                                 contact.get("linkedin"), contact.get("github")] if v]
    if contact_bits:
        story.append(Paragraph(" | ".join(contact_bits), styles["ContactLine"]))

    skills = parsed_json.get("skills", [])
    if skills:
        story.append(Paragraph("SKILLS", styles["SectionHeading"]))
        story.append(Paragraph(", ".join(skills), styles["BulletText"]))

    experience = parsed_json.get("experience", [])
    if experience:
        story.append(Paragraph("EXPERIENCE", styles["SectionHeading"]))
        for entry in experience:
            header = entry.get("header", "")
            if header:
                story.append(Paragraph(header, styles["EntryHeader"]))
            for bullet_text in entry.get("bullets", []):
                bullet_id = bullet_id_by_text.get(bullet_text)
                final_text = rewrite_map.get(bullet_id, bullet_text)
                story.append(Paragraph(f"•&nbsp;&nbsp;{final_text}", styles["BulletText"]))

    education = parsed_json.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", styles["SectionHeading"]))
        for entry in education:
            header = entry.get("header", "")
            if header:
                story.append(Paragraph(header, styles["EntryHeader"]))
            for bullet_text in entry.get("bullets", []):
                story.append(Paragraph(bullet_text, styles["BulletText"]))

    doc.build(story)
    return buffer.getvalue()
