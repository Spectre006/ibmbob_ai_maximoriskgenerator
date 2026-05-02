"""PDF report generation service using ReportLab."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import Optional
import os

from utils.logger import get_logger
from models.jha_report import JHAReport
from config.constants import REPORT_TITLE, REPORT_SUBTITLE, COMPANY_NAME, LABEL_TRANSLATIONS

logger = get_logger(__name__)

def _translate_label(key: str, language: str = "en") -> str:
    """Get translated label for given key and language."""
    return LABEL_TRANSLATIONS.get(language, {}).get(key, LABEL_TRANSLATIONS["en"].get(key, key))


def _s(value, default: str = "N/A") -> str:
    """Safely convert any value to a non-None string for ReportLab Paragraphs.

    dict.get(key, 'N/A') still returns None when the key exists but holds None.
    This helper covers that case: any falsy non-zero value becomes *default*.
    """
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default

# ── Unicode font registration ──────────────────────────────────────────────────
# Arial Unicode MS covers Latin Extended (French accents) AND Devanagari (Hindi).
# Registered once at module load; falls back gracefully if file not found.
_ARIAL_UNICODE_PATH = "/Library/Fonts/Arial Unicode.ttf"
_UNICODE_FONT_AVAILABLE = False

try:
    pdfmetrics.registerFont(TTFont("ArialUnicode", _ARIAL_UNICODE_PATH))
    # ReportLab needs a "bold" variant for <b> markup inside Paragraphs.
    # Arial Unicode has no separate bold file, so we register the same file
    # under the bold name — text weight is indistinguishable but glyphs render.
    pdfmetrics.registerFont(TTFont("ArialUnicode-Bold", _ARIAL_UNICODE_PATH))
    pdfmetrics.registerFontFamily(
        "ArialUnicode",
        normal="ArialUnicode",
        bold="ArialUnicode-Bold",
        italic="ArialUnicode",
        boldItalic="ArialUnicode-Bold",
    )
    _UNICODE_FONT_AVAILABLE = True
    logger.info("Arial Unicode font registered for multilingual PDF support")
except Exception as e:
    logger.warning(f"Arial Unicode font not found — Hindi PDF rendering may show boxes: {e}")

# Languages that require a Unicode font (non-Latin scripts)
_UNICODE_REQUIRED_LANGS = {"hi"}

# Languages that work with Helvetica (Latin Extended covers French accents)
_LATIN_EXTENDED_LANGS = {"en", "fr"}


def _font_for_lang(language: str) -> tuple[str, str]:
    """Return (normal_font, bold_font) for the given language code."""
    if language in _UNICODE_REQUIRED_LANGS and _UNICODE_FONT_AVAILABLE:
        return "ArialUnicode", "ArialUnicode-Bold"
    return "Helvetica", "Helvetica-Bold"


logger = get_logger(__name__)


class PDFGenerator:
    """Service for generating PDF reports."""

    def __init__(self):
        """Initialize PDF generator."""
        self.page_size = letter
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        logger.info("PDF Generator initialized")
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0f62fe'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#393939'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0f62fe'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Risk level styles
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#da1e28'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#8e6a00'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#0e6027'),
            fontName='Helvetica-Bold'
        ))
    
    def _build_lang_styles(self, font_normal: str, font_bold: str) -> dict:
        """
        Build a set of ParagraphStyle objects keyed by role,
        using the correct font family for the current language.
        These are created fresh per-call so concurrent requests
        with different languages don't interfere.
        """
        suffix = font_normal  # use font name as unique-enough suffix
        return {
            "Title": ParagraphStyle(
                f"DynTitle_{suffix}",
                parent=self.styles["Normal"],
                fontSize=24,
                textColor=colors.HexColor("#0f62fe"),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName=font_bold,
            ),
            "Subtitle": ParagraphStyle(
                f"DynSubtitle_{suffix}",
                parent=self.styles["Normal"],
                fontSize=14,
                textColor=colors.HexColor("#393939"),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName=font_normal,
            ),
            "SectionHeading": ParagraphStyle(
                f"DynSectionHeading_{suffix}",
                parent=self.styles["Normal"],
                fontSize=16,
                textColor=colors.HexColor("#0f62fe"),
                spaceAfter=10,
                spaceBefore=15,
                fontName=font_bold,
            ),
            "Normal": ParagraphStyle(
                f"DynNormal_{suffix}",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName=font_normal,
            ),
            "RiskHigh": ParagraphStyle(
                f"DynRiskHigh_{suffix}",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#da1e28"),
                fontName=font_bold,
            ),
            "RiskMedium": ParagraphStyle(
                f"DynRiskMedium_{suffix}",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#8e6a00"),
                fontName=font_bold,
            ),
            "RiskLow": ParagraphStyle(
                f"DynRiskLow_{suffix}",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#0e6027"),
                fontName=font_bold,
            ),
        }

    def generate_pdf(self, report: JHAReport, output_path: str) -> str:
        """
        Generate PDF report from JHA report data.

        Args:
            report: JHA report object
            output_path: Path to save PDF file

        Returns:
            Path to generated PDF file
        """
        language = report.report_metadata.get("language", "en") if report.report_metadata else "en"
        font_normal, font_bold = _font_for_lang(language)
        lang_styles = self._build_lang_styles(font_normal, font_bold)
        logger.info(f"Generating PDF report: {report.report_id} | lang={language} | font={font_normal}")

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            # Build content
            story = []

            # Add header
            story.extend(self._create_header(report, font_normal, font_bold, lang_styles))

            # Add work order details
            story.extend(self._create_work_order_section(report, font_normal, font_bold, lang_styles))

            # Add hazards section
            story.extend(self._create_hazards_section(report, font_normal, font_bold, lang_styles))

            # Add emergency contacts
            story.extend(self._create_emergency_contacts_section(report, font_normal, font_bold, lang_styles))

            # Add footer info
            story.extend(self._create_footer(report, font_normal, font_bold, lang_styles))

            # Build PDF
            doc.build(story)

            logger.info(f"PDF report generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _create_header(self, report: JHAReport,
                       font_normal: str = 'Helvetica',
                       font_bold: str = 'Helvetica-Bold',
                       lang_styles: dict = None) -> list:
        """Create report header."""
        elements = []
        ls = lang_styles or {}
        language = report.language if hasattr(report, 'language') else report.report_metadata.get("language", "en")

        # Use translated title and subtitle with language-correct fonts
        title_text = _translate_label('report_title', language)
        title = Paragraph(title_text, ls.get('Title', self.styles['CustomTitle']))
        elements.append(title)

        subtitle_text = _translate_label('report_subtitle', language)
        subtitle = Paragraph(subtitle_text, ls.get('Subtitle', self.styles['CustomSubtitle']))
        elements.append(subtitle)

        company = Paragraph(COMPANY_NAME, ls.get('Normal', self.styles['Normal']))
        elements.append(company)
        elements.append(Spacer(1, 0.3 * inch))

        # Status shows Maximo WO status — NOT the report lifecycle status
        wo_status = _s(report.work_order.get('status') if report.work_order else None)
        report_info = [
            [_translate_label('report_id', language) + ':',  _s(report.report_id)],
            [_translate_label('work_order', language) + ':', _s(report.work_order_id)],
            [_translate_label('generated', language) + ':',  report.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')],
            [_translate_label('status', language) + ':',     wo_status],
        ]

        info_table = Table(report_info, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME',      (0, 0), (0, -1), font_bold),
            ('FONTNAME',      (1, 0), (1, -1), font_normal),
            ('FONTSIZE',      (0, 0), (-1, -1), 10),
            ('TEXTCOLOR',     (0, 0), (0, -1), colors.HexColor('#393939')),
            ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))
        return elements

    def _create_work_order_section(self, report: JHAReport,
                                   font_normal: str = 'Helvetica',
                                   font_bold: str = 'Helvetica-Bold',
                                   lang_styles: dict = None) -> list:
        """Create work order details section."""
        elements = []
        ls = lang_styles or {}
        language = report.language if hasattr(report, 'language') else report.report_metadata.get("language", "en")

        heading = Paragraph(_translate_label('work_order_details', language), ls.get('SectionHeading', self.styles['SectionHeading']))
        elements.append(heading)

        header_label_style = ParagraphStyle(
            f'WOHeaderLabel_{font_normal}',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=font_bold,
            textColor=colors.white,
            leading=13,
        )
        label_style = ParagraphStyle(
            f'WOLabel_{font_normal}',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=font_bold,
            textColor=colors.HexColor('#393939'),
            leading=13,
        )
        value_style = ParagraphStyle(
            f'WOValue_{font_normal}',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=font_normal,
            textColor=colors.HexColor('#161616'),
            leading=13,
        )

        wo = report.work_order
        available_width = self.page_size[0] - 1.5 * inch
        col1 = 1.6 * inch
        col2 = available_width - col1

        header_row = [
            Paragraph(_translate_label('field', language), header_label_style),
            Paragraph(_translate_label('value', language), header_label_style),
        ]
        wo_rows = [
            [Paragraph(_translate_label('work_order_number', language), label_style), Paragraph(_s(wo.get('id')),          value_style)],
            [Paragraph(_translate_label('description', language),  label_style), Paragraph(_s(wo.get('description')),      value_style)],
            [Paragraph(_translate_label('location', language),     label_style), Paragraph(_s(wo.get('location')),         value_style)],
            [Paragraph(_translate_label('equipment', language),    label_style), Paragraph(_s(wo.get('equipment')),        value_style)],
            [Paragraph(_translate_label('priority', language),     label_style), Paragraph(_s(wo.get('priority')),         value_style)],
            [Paragraph(_translate_label('status', language),       label_style), Paragraph(_s(wo.get('status')),           value_style)],
            [Paragraph(_translate_label('assigned_to', language),  label_style), Paragraph(_s(wo.get('assigned_to')),      value_style)],
        ]

        table_data = [header_row] + wo_rows
        wo_table = Table(table_data, colWidths=[col1, col2])
        wo_table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0),  colors.HexColor('#0f62fe')),
            ('TEXTCOLOR',    (0, 0), (-1, 0),  colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f4f4')]),
            ('ALIGN',        (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING',   (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
            ('LEFTPADDING',  (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#c6c6c6')),
            ('LINEBELOW',    (0, 0), (-1, 0),  1.5, colors.HexColor('#0043ce')),
        ]))

        elements.append(wo_table)
        elements.append(Spacer(1, 0.2 * inch))
        return elements

    def _create_hazards_section(self, report: JHAReport,
                                font_normal: str = 'Helvetica',
                                font_bold: str = 'Helvetica-Bold',
                                lang_styles: dict = None) -> list:
        """Create hazards identification section."""
        elements = []
        ls = lang_styles or {}
        language = report.language if hasattr(report, 'language') else report.report_metadata.get("language", "en")

        heading = Paragraph(_translate_label('identified_hazards', language), ls.get('SectionHeading', self.styles['SectionHeading']))
        elements.append(heading)

        if not report.hazards:
            elements.append(Paragraph("No hazards identified.", ls.get('Normal', self.styles['Normal'])))
            return elements

        for hazard in report.hazards:
            elements.extend(self._create_hazard_table(hazard, report, font_normal, font_bold, lang_styles))
            elements.append(Spacer(1, 0.15 * inch))

        return elements

    def _create_hazard_table(self, hazard, report: JHAReport, font_normal: str = 'Helvetica',
                             font_bold: str = 'Helvetica-Bold', lang_styles: dict = None) -> list:
        """Create table for individual hazard."""
        elements = []
        ls = lang_styles or {}
        language = report.language if hasattr(report, 'language') else report.report_metadata.get("language", "en")

        risk_style = ls.get(f"Risk{hazard.risk_level.value}", ls.get('Normal', self.styles['Normal']))
        normal_style = ls.get('Normal', self.styles['Normal'])
        header_data = [[
            Paragraph(f"<b>{_translate_label('hazard', language)} #{hazard.id}</b>", normal_style),
            Paragraph(f"<b>{_translate_label('risk_level', language)}: {hazard.risk_level.value}</b>", risk_style)
        ]]

        header_table = Table(header_data, colWidths=[4 * inch, 2 * inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, -1), colors.HexColor('#f4f4f4')),
            ('ALIGN',        (0, 0), (0, 0),  'LEFT'),
            ('ALIGN',        (1, 0), (1, 0),  'RIGHT'),
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',   (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
            ('LEFTPADDING',  (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(header_table)

        cell_style = ParagraphStyle(
            f'CellText_{font_normal}',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName=font_normal,
            leading=12,
        )
        cell_bold_style = ParagraphStyle(
            f'CellBold_{font_bold}',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName=font_bold,
            leading=12,
        )

        controls_text = ', '.join(_s(c) for c in hazard.controls if c) if hazard.controls else 'N/A'
        ppe_text      = ', '.join(_s(p) for p in hazard.ppe      if p) if hazard.ppe      else 'Standard PPE'
        details_data = [
            [Paragraph(_translate_label('description', language) + ':',  cell_bold_style),
             Paragraph(_s(hazard.description), cell_style)],
            [Paragraph(_translate_label('controls', language) + ':',     cell_bold_style),
             Paragraph(controls_text, cell_style)],
            [Paragraph(_translate_label('required_ppe', language) + ':', cell_bold_style),
             Paragraph(ppe_text, cell_style)],
        ]

        details_table = Table(details_data, colWidths=[1.5 * inch, 4.5 * inch])
        details_table.setStyle(TableStyle([
            ('ALIGN',        (0, 0), (0, -1), 'LEFT'),
            ('ALIGN',        (1, 0), (1, -1), 'LEFT'),
            ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING',   (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
            ('LEFTPADDING',  (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID',         (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(details_table)
        return elements

    def _create_emergency_contacts_section(self, report: JHAReport,
                                           font_normal: str = 'Helvetica',
                                           font_bold: str = 'Helvetica-Bold',
                                           lang_styles: dict = None) -> list:
        """Create emergency contacts section."""
        elements = []
        ls = lang_styles or {}
        language = report.language if hasattr(report, 'language') else report.report_metadata.get("language", "en")

        heading = Paragraph(_translate_label('emergency_contacts', language), ls.get('SectionHeading', self.styles['SectionHeading']))
        elements.append(heading)

        if not report.emergency_contacts:
            elements.append(Paragraph("No emergency contacts specified.", ls.get('Normal', self.styles['Normal'])))
            return elements

        contacts = report.emergency_contacts
        contacts_data = []
        if contacts.supervisor:
            contacts_data.append([_translate_label('supervisor', language) + ':',         _s(contacts.supervisor)])
        if contacts.safety_officer:
            contacts_data.append([_translate_label('safety_officer', language) + ':',     _s(contacts.safety_officer)])
        if contacts.emergency:
            contacts_data.append([_translate_label('emergency_services', language) + ':', _s(contacts.emergency)])

        if contacts_data:
            contacts_table = Table(contacts_data, colWidths=[2 * inch, 4 * inch])
            contacts_table.setStyle(TableStyle([
                ('FONTNAME',      (0, 0), (0, -1), font_bold),
                ('FONTNAME',      (1, 0), (1, -1), font_normal),
                ('FONTSIZE',      (0, 0), (-1, -1), 10),
                ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor('#fff1f1')),
                ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#da1e28')),
            ]))
            elements.append(contacts_table)

        elements.append(Spacer(1, 0.2 * inch))
        return elements

    def _create_footer(self, report: JHAReport,
                       font_normal: str = 'Helvetica',
                       font_bold: str = 'Helvetica-Bold',
                       lang_styles: dict = None) -> list:
        """Create report footer."""
        elements = []
        ls = lang_styles or {}
        language = report.language if hasattr(report, 'language') else report.report_metadata.get("language", "en")

        if report.additional_notes:
            heading = Paragraph(
                _translate_label('additional_notes', language),
                ls.get('SectionHeading', self.styles['SectionHeading'])
            )
            elements.append(heading)
            notes_style = ParagraphStyle(
                f'NotesText_{font_normal}',
                parent=self.styles['Normal'],
                fontName=font_normal,
            )
            elements.append(Paragraph(_s(report.additional_notes), notes_style))
            elements.append(Spacer(1, 0.2 * inch))

        # Localised disclaimer
        disclaimers = {
            "hi": (
                "यह जॉब हैज़र्ड एनालिसिस रिपोर्ट AI-संचालित जोखिम मूल्यांकन का उपयोग करके तैयार की गई थी। "
                "इसे लागू करने से पहले एक योग्य सुरक्षा पेशेवर द्वारा समीक्षा की जानी चाहिए।"
            ),
            "fr": (
                "Ce rapport d'analyse des risques au travail a été généré à l'aide d'une évaluation des risques "
                "basée sur l'IA. Il doit être examiné par un professionnel de la sécurité qualifié avant mise en œuvre."
            ),
        }
        disclaimer_text = disclaimers.get(language, (
            "This Job Hazard Analysis report was generated using AI-powered risk assessment. "
            "It should be reviewed by a qualified safety professional before implementation. "
            "Always follow your organization's safety procedures and regulations."
        ))
        disc_style = ParagraphStyle(
            f'Disclaimer_{font_normal}',
            parent=self.styles['Normal'],
            fontName=font_normal,
            fontSize=8,
            textColor=colors.HexColor('#525252'),
        )
        elements.append(Paragraph(disclaimer_text, disc_style))
        return elements
    
    def _get_risk_style(self, risk_level: str):
        """Get paragraph style for risk level."""
        risk_map = {
            'High': 'RiskHigh',
            'Medium': 'RiskMedium',
            'Low': 'RiskLow'
        }
        return self.styles.get(risk_map.get(risk_level, 'Normal'))


# Global instance
pdf_generator = PDFGenerator()

# Made with Bob
