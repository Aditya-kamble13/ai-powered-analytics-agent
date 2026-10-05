import os
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(df: pd.DataFrame, filename: str = "Anomaly_Report.pdf") -> str:
    """Generates a perfectly auto-fitted, clean PDF report from dataset."""
    # Page dimensions for landscape orientation
    doc = SimpleDocTemplate(
        filename, 
        pagesize=landscape(letter),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=1 # Center
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#334155'),
        alignment=1
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1E293B'),
        alignment=0 # Left align
    )

    header_cell_style = ParagraphStyle(
        'HeaderCellStyle',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.whitesmoke,
        alignment=0
    )

    # 1. Header & Title
    elements.append(Paragraph("📊 AI Business Intelligence - Anomaly Detection Report", title_style))
    elements.append(Spacer(1, 10))
    
    # 2. Key Metrics Summary
    total_rows = len(df)
    anomaly_col = 'anomaly' if 'anomaly' in df.columns else ('Is_Anomaly' if 'Is_Anomaly' in df.columns else None)
    anomaly_count = df[anomaly_col].sum() if anomaly_col else 0
    
    summary_text = f"<b>Total Records:</b> {total_rows} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Anomalies Detected:</b> <font color='#DC2626'><b>{anomaly_count}</b></font>"
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 12))

    # 3. Clean up Unnamed Columns & Limit Columns if needed
    cleaned_df = df.copy()
    # Filter out empty or 'Unnamed' columns for cleaner layout
    valid_cols = [c for c in cleaned_df.columns if not str(c).startswith('Unnamed')]
    if valid_cols:
        cleaned_df = cleaned_df[valid_cols]
    
    # Limit to top 10 columns for a perfect PDF wrap if dataset is ultra-wide
    max_cols = 10
    if len(cleaned_df.columns) > max_cols:
        cleaned_df = cleaned_df.iloc[:, :max_cols]
    
    # Preview top 25 rows
    preview_df = cleaned_df.head(25).fillna("-")
    
    # Wrap text in Paragraphs so cells auto-wrap instead of clipping/overflowing
    formatted_data = []
    
    # Headers
    headers = [Paragraph(str(c), header_cell_style) for c in preview_df.columns]
    formatted_data.append(headers)
    
    # Rows
    for _, row in preview_df.iterrows():
        formatted_row = [Paragraph(str(val), cell_style) for val in row.values]
        formatted_data.append(formatted_row)
    
    # Calculate available table width (792 printable width - 40 margins = 752)
    available_width = 752
    col_count = len(preview_df.columns)
    col_width = available_width / col_count if col_count > 0 else available_width

    table = Table(formatted_data, colWidths=[col_width] * col_count)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')), # Dark slate blue header
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')), # Light grey border
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]), # Zebra striping
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return filename