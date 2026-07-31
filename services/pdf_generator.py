import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_learned_words_pdf(user_name: str, learned_words: list, output_filename: str) -> str:
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    # Попытка подключить кириллический шрифт из системы macOS или использовать fallback
    font_name = 'Helvetica'
    try:
        # Проверяем наличие стандартного шрифта Arial в macOS
        arial_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        if os.path.exists(arial_path):
            pdfmetrics.registerFont(TTFont('Arial', arial_path))
            font_name = 'Arial'
    except Exception:
        pass

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#2C3E50"),
        alignment=1, # Center
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#7F8C8D"),
        alignment=1,
        spaceAfter=20
    )

    cell_head_style = ParagraphStyle(
        'CellHead',
        fontName=font_name,
        fontSize=10,
        leading=12,
        textColor=colors.white,
        alignment=0
    )

    cell_eng_style = ParagraphStyle(
        'CellEng',
        fontName=font_name,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#2980B9")
    )

    cell_tr_style = ParagraphStyle(
        'CellTr',
        fontName=font_name,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#2C3E50")
    )

    cell_pos_style = ParagraphStyle(
        'CellPos',
        fontName=font_name,
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#8E44AD")
    )

    elements = []

    # Заголовок
    elements.append(Paragraph(f"🎓 Мой личный словарь: {user_name}", title_style))
    elements.append(Paragraph(f"Всего изучено слов: <b>{len(learned_words)}</b> • Тренажер English Learn Bot", subtitle_style))
    elements.append(Spacer(1, 10))

    # Данные таблицы
    table_data = [
        [
            Paragraph("<b>#</b>", cell_head_style),
            Paragraph("<b>English Word</b>", cell_head_style),
            Paragraph("<b>Перевод на русский</b>", cell_head_style),
            Paragraph("<b>Часть речи</b>", cell_head_style)
        ]
    ]

    for idx, row in enumerate(learned_words, 1):
        table_data.append([
            Paragraph(str(idx), cell_tr_style),
            Paragraph(f"<b>{row['english_word'].capitalize()}</b>", cell_eng_style),
            Paragraph(row['translation'], cell_tr_style),
            Paragraph(row['part_of_speech'] if row['part_of_speech'] else 'noun', cell_pos_style)
        ])

    table = Table(table_data, colWidths=[30, 160, 240, 110])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980B9")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8F9F9"), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)
    return output_filename
