from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

class FormBuilder:
    def __init__(self):
        pass

    def generate_1040_summary(self, tax_results, answers):
        """Generate a PDF summary of tax return (simplified 1040)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )

        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15
        )

        content = []

        # Title
        content.append(Paragraph("Tax Return Summary (Form 1040)", title_style))
        content.append(Spacer(1, 12))

        # Personal Information
        content.append(Paragraph("Personal Information", section_style))
        personal_info = [
            ["Name:", answers.get('full_name', 'N/A')],
            ["SSN:", answers.get('ssn', 'N/A')],
            ["Filing Status:", answers.get('filing_status', 'N/A')],
            ["Dependents:", str(answers.get('dependents', 0))]
        ]

        table = Table(personal_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))

        # Income Information
        content.append(Paragraph("Income Information", section_style))
        income_info = [
            ["Wages, salaries, tips:", f"${answers.get('wages', 0):,.2f}"],
            ["Interest income:", f"${answers.get('interest', 0):,.2f}"],
            ["Dividend income:", f"${answers.get('dividends', 0):,.2f}"],
            ["Total Income:", f"${answers.get('total_income', 0):,.2f}"]
        ]

        income_table = Table(income_info, colWidths=[3*inch, 3*inch])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(income_table)
        content.append(Spacer(1, 20))

        # Tax Calculation Results
        content.append(Paragraph("Tax Calculation Results", section_style))

        federal = tax_results.get('federal', {})
        state = tax_results.get('state', {})
        se_tax = tax_results.get('self_employment', {})

        tax_info = [
            ["Federal Tax Owed:", f"${federal.get('amount_due', 0):,.2f}"],
            ["Federal Refund:", f"${federal.get('refund', 0):,.2f}"],
            ["State Tax Owed:", f"${state.get('amount_due', 0):,.2f}"],
            ["State Refund:", f"${state.get('refund', 0):,.2f}"],
            ["Self-Employment Tax:", f"${se_tax.get('total_tax', 0):,.2f}"]
        ]

        tax_table = Table(tax_info, colWidths=[3*inch, 3*inch])
        tax_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(tax_table)
        content.append(Spacer(1, 20))

        # Disclaimer
        content.append(Paragraph("Disclaimer", section_style))
        content.append(Paragraph(
            "This is a simplified tax summary for informational purposes only. "
            "It is not a substitute for professional tax advice. Please consult a tax professional "
            "for accurate tax preparation and filing.",
            styles['Normal']
        ))

        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_benefits_summary(self, benefits):
        """Generate a PDF summary of potential benefits"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )

        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15
        )

        content = []

        # Title
        content.append(Paragraph("Potential Benefits Summary", title_style))
        content.append(Spacer(1, 12))

        if not benefits:
            content.append(Paragraph("No benefits programs were identified based on your information.", styles['Normal']))
        else:
            content.append(Paragraph(f"We found {len(benefits)} potential benefits programs you may qualify for:", styles['Normal']))
            content.append(Spacer(1, 12))

            # Benefits table
            benefit_data = [["Benefit Program", "Description", "Estimated Value"]]
            for benefit in benefits:
                benefit_data.append([
                    benefit.get('program', 'N/A'),
                    benefit.get('reason', 'N/A'),
                    f"${benefit.get('estimated_amount', 0) or 'N/A':,.2f}" if benefit.get('estimated_amount') else 'N/A'
                ])

            table = Table(benefit_data, colWidths=[2.5*inch, 3*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(table)
            content.append(Spacer(1, 20))

        # Next Steps
        content.append(Paragraph("Next Steps", section_style))
        content.append(Paragraph(
            "• Contact your local social services office for application assistance\n"
            "• Visit benefits.gov for more information\n"
            "• Consult with a benefits counselor for personalized guidance",
            styles['Normal']
        ))
        content.append(Spacer(1, 12))

        # Disclaimer
        content.append(Paragraph("Disclaimer", section_style))
        content.append(Paragraph(
            "This is an estimate based on the information provided. Actual eligibility "
            "and benefit amounts may vary. Please verify with the appropriate agency.",
            styles['Normal']
        ))

        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
