"""
PDF Report Generator
Generates downloadable PDF reports from soil analysis data
"""
import logging
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import datetime

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generates PDF reports for soil analysis"""
    
    def __init__(self):
        """Initialize PDF generator"""
        # Try to register Hindi font (optional - will use default if not available)
        try:
            # You would need to add a Hindi font file for proper Hindi support
            # For now, we'll use default fonts
            pass
        except Exception as e:
            logger.warning(f"Could not load Hindi font: {e}")
    
    def generate_pdf(self, report_data: Dict[str, Any], language: str = "english") -> BytesIO:
        """
        Generate PDF report
        
        Args:
            report_data: Report data with english/hindi keys
            language: "english" or "hindi"
        
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Get report in selected language
        report = report_data.get(language, report_data.get("english", {}))
        metadata = report_data.get("metadata", {})
        
        # Build PDF content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        title_text = "मिट्टी विश्लेषण रिपोर्ट" if language == "hindi" else "Soil Analysis Report"
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        date_label = "तिथि:" if language == "hindi" else "Date:"
        location_label = "स्थान:" if language == "hindi" else "Location:"
        soil_type_label = "मिट्टी का प्रकार:" if language == "hindi" else "Soil Type:"
        
        meta_data = [
            [date_label, datetime.datetime.now().strftime("%B %d, %Y")],
            [location_label, metadata.get("location", "N/A")],
            [soil_type_label, metadata.get("soilType", "N/A")]
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Soil Analysis Section
        soil_analysis = report.get("soilAnalysis", {})
        if soil_analysis:
            section_title = "मिट्टी विश्लेषण" if language == "hindi" else "Soil Analysis"
            story.append(Paragraph(section_title, heading_style))
            
            # Assessment
            assessment = soil_analysis.get("assessment", "")
            if assessment:
                story.append(Paragraph(assessment, styles['BodyText']))
                story.append(Spacer(1, 0.15*inch))
            
            # Rating
            rating = soil_analysis.get("rating", "")
            if rating:
                rating_label = "रेटिंग:" if language == "hindi" else "Rating:"
                rating_text = f"<b>{rating_label}</b> {rating}"
                story.append(Paragraph(rating_text, styles['BodyText']))
                story.append(Spacer(1, 0.15*inch))
            
            # Pros
            pros = soil_analysis.get("pros", [])
            if pros:
                pros_label = "सकारात्मक पहलू:" if language == "hindi" else "Strengths:"
                story.append(Paragraph(f"<b>{pros_label}</b>", styles['BodyText']))
                for pro in pros:
                    story.append(Paragraph(f"• {pro}", styles['BodyText']))
                story.append(Spacer(1, 0.15*inch))
            
            # Cons
            cons = soil_analysis.get("cons", [])
            if cons:
                cons_label = "सुधार के क्षेत्र:" if language == "hindi" else "Areas for Improvement:"
                story.append(Paragraph(f"<b>{cons_label}</b>", styles['BodyText']))
                for con in cons:
                    story.append(Paragraph(f"• {con}", styles['BodyText']))
            
            story.append(Spacer(1, 0.3*inch))
        
        # Crop Recommendations Section
        crops = report.get("cropRecommendations", [])
        if crops:
            section_title = "फसल सिफारिशें" if language == "hindi" else "Crop Recommendations"
            story.append(Paragraph(section_title, heading_style))
            
            crop_label = "फसल" if language == "hindi" else "Crop"
            reason_label = "कारण" if language == "hindi" else "Reason"
            season_label = "मौसम" if language == "hindi" else "Season"
            
            crop_data = [[crop_label, reason_label, season_label]]
            for crop in crops:
                crop_data.append([
                    crop.get("crop", ""),
                    crop.get("reason", ""),
                    crop.get("season", "")
                ])
            
            crop_table = Table(crop_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
            crop_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(crop_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Fertilizer Recommendations Section
        fertilizers = report.get("fertilizerRecommendations", [])
        if fertilizers:
            section_title = "उर्वरक सिफारिशें" if language == "hindi" else "Fertilizer Recommendations"
            story.append(Paragraph(section_title, heading_style))
            
            fert_label = "उर्वरक" if language == "hindi" else "Fertilizer"
            type_label = "प्रकार" if language == "hindi" else "Type"
            app_label = "मात्रा" if language == "hindi" else "Application"
            time_label = "समय" if language == "hindi" else "Timing"
            
            fert_data = [[fert_label, type_label, app_label, time_label]]
            for fert in fertilizers:
                fert_data.append([
                    fert.get("fertilizer", ""),
                    fert.get("type", ""),
                    fert.get("application", ""),
                    fert.get("timing", "")
                ])
            
            fert_table = Table(fert_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
            fert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(fert_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = "यह रिपोर्ट AI द्वारा उत्पन्न की गई है। कृपया स्थानीय कृषि विशेषज्ञ से परामर्श लें।" if language == "hindi" else "This report is AI-generated. Please consult with local agricultural experts."
        story.append(Paragraph(footer_text, styles['Italic']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        logger.info(f"✓ Generated PDF report in {language}")
        return buffer


# Singleton instance
pdf_generator = PDFReportGenerator()
