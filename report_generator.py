import io
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(df: pd.DataFrame, summary_text: str = "") -> io.BytesIO():
    buffer = io.BytesIO()
    
    # Page layout set to Landscape for wide data tables
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1, # Center
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#374151")
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        wordWrap='CJK'
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )

    # 1. Title
    story.append(Paragraph("<b>AI Business Intelligence Audit Report</b>", title_style))
    
    # 2. Overview / Summary
    if not summary_text:
        summary_text = f"Dataset contains {len(df)} rows and {len(df.columns)} columns."
    story.append(Paragraph(f"<b>Overview:</b> {summary_text}", body_style))
    story.append(Spacer(1, 15))
    
    # 3. Table Header & Data Preparation
    story.append(Paragraph("<b>Data Sample (Top Rows):</b>", body_style))
    story.append(Spacer(1, 8))
    
    # Prepare top 10 sample rows
    sample_df = df.head(10).copy()
    
    # Clean datetime strings if any (removes 00:00:00)
    for col in sample_df.columns:
        if pd.api.types.is_datetime64_any_dtype(sample_df[col]):
            sample_df[col] = sample_df[col].dt.strftime('%Y-%m-%d')
        else:
            sample_df[col] = sample_df[col].astype(str).str.replace(" 00:00:00", "")

    headers = [Paragraph(f"<b>{str(col)}</b>", table_header_style) for col in sample_df.columns]
    
    table_data = [headers]
    for _, row in sample_df.iterrows():
        formatted_row = [Paragraph(str(val), table_cell_style) for val in row]
        table_data.append(formatted_row)

    # Dynamic Column Width calculation based on available width (~720 points for landscape)
    num_cols = len(sample_df.columns)
    col_width = 720 / max(num_cols, 1)
    
    pdf_table = Table(table_data, colWidths=[col_width] * num_cols, repeatRows=1)
    
    # Table Styling
    pdf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    
    story.append(pdf_table)
    
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer