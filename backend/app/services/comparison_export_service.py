import os
import uuid
from datetime import datetime, UTC
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ComparisonExportService:
    async def export_comparison_report(self, doc_a_name: str, doc_b_name: str, comparison_result: dict) -> dict:
        EXPORT_DIR = "exports"
        os.makedirs(EXPORT_DIR, exist_ok=True)
        report_filename = f"comparison_{uuid.uuid4().hex}.pdf"
        report_path = os.path.join(EXPORT_DIR, report_filename)

        doc = SimpleDocTemplate(report_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = styles['Heading1']
        h2_style = styles['Heading2']
        h3_style = styles['Heading3']
        normal_style = styles['Normal']

        disclaimer = "ClauseIQ provides AI-assisted research support only and does not constitute legal, tax, compliance, accounting, or professional advice."
        story.append(Paragraph(f"<b>DISCLAIMER:</b> {disclaimer}", normal_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("ClauseIQ Comparison Report", title_style))
        story.append(Paragraph(f"<b>Original:</b> {doc_a_name}", normal_style))
        story.append(Paragraph(f"<b>New Version:</b> {doc_b_name}", normal_style))
        story.append(Paragraph(f"Generated on: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC", normal_style))
        story.append(Spacer(1, 12))

        # Added
        story.append(Paragraph("1. Added Clauses", h2_style))
        for c in comparison_result.get('added', []):
            story.append(Paragraph(f"<b>{c['clause_id']} - {c['title']}</b>", h3_style))
            story.append(Paragraph(c['content'], normal_style))
            story.append(Spacer(1, 6))

        # Removed
        story.append(Paragraph("2. Removed Clauses", h2_style))
        for c in comparison_result.get('removed', []):
            story.append(Paragraph(f"<b>{c['clause_id']} - {c['title']}</b>", h3_style))
            story.append(Paragraph(c['content'], normal_style))
            story.append(Spacer(1, 6))

        # Modified
        story.append(Paragraph("3. Modified Clauses", h2_style))
        for m in comparison_result.get('modified', []):
            old_c = m['old_clause']
            new_c = m['new_clause']
            analysis = m['analysis']
            story.append(Paragraph(f"<b>{old_c['clause_id']} - {old_c['title']}</b>", h3_style))
            story.append(Paragraph(f"<i>AI Analysis:</i> {analysis['what_changed']}", normal_style))
            story.append(Paragraph(f"<i>Compliance Impact:</i> {analysis['compliance_impact']}", normal_style))
            story.append(Paragraph(f"<i>Risk Impact:</i> {analysis['risk_impact']}", normal_style))
            story.append(Spacer(1, 6))

        doc.build(story)
        return {"download_url": f"/api/v1/export/download/{report_filename}"}
