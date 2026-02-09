import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor
from .analytics import AnalyticsEngine


class ReportGenerator:
    """Class for generating PDF reports from equipment data"""
    
    def __init__(self):
        self.analytics = AnalyticsEngine()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the report"""
        # Only add styles if they don't already exist
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            ))
        
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue,
                borderWidth=1,
                borderColor=colors.darkblue,
                borderPadding=5
            ))
        
        if 'ReportBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportBodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                leading=14
            ))
    
    def generate_report(self, upload_id=None, include_charts=True):
        """
        Generate a comprehensive PDF report
        
        Args:
            upload_id: Specific upload to generate report for (None for latest)
            include_charts: Whether to include charts in the report
            
        Returns:
            BytesIO object containing the PDF data
        """
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build report content
        story = []
        
        # Get analytics data
        if upload_id:
            summary = self.analytics.get_upload_summary(upload_id)
        else:
            summary = self.analytics.get_latest_upload_summary()
        
        if summary.total_equipment == 0:
            raise ValueError("No equipment data available for report generation")
        
        # Title
        story.append(Paragraph("Chemical Equipment Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Report metadata
        story.append(Paragraph("Report Information", self.styles['SectionHeader']))
        report_info = [
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Equipment:', str(summary.total_equipment)],
            ['Equipment Types:', str(len(summary.type_distribution or {}))],
        ]
        
        report_table = Table(report_info, colWidths=[2*inch, 3*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(report_table)
        story.append(Spacer(1, 20))
        
        # Summary Statistics
        story.append(Paragraph("Summary Statistics", self.styles['SectionHeader']))
        
        summary_data = [
            ['Metric', 'Value', 'Unit'],
            ['Total Equipment Count', f"{summary.total_equipment:,}", 'units'],
            ['Average Flowrate', f"{summary.average_flowrate:.2f}", 'L/min'],
            ['Average Pressure', f"{summary.average_pressure:.2f}", 'bar'],
            ['Average Temperature', f"{summary.average_temperature:.1f}", '°C'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Equipment Type Distribution
        if summary.type_distribution:
            story.append(Paragraph("Equipment Type Distribution", self.styles['SectionHeader']))
            
            # Create distribution table
            dist_data = [['Equipment Type', 'Count', 'Percentage']]
            total = summary.total_equipment
            
            for eq_type, count in summary.type_distribution.items():
                percentage = (count / total) * 100
                dist_data.append([eq_type, str(count), f"{percentage:.1f}%"])
            
            dist_table = Table(dist_data, colWidths=[2*inch, 1*inch, 1*inch])
            dist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(dist_table)
            story.append(Spacer(1, 20))
        
        # Add charts if requested
        if include_charts and summary.type_distribution:
            story.append(PageBreak())
            story.append(Paragraph("Data Visualizations", self.styles['SectionHeader']))
            
            # Pie chart for equipment type distribution
            pie_chart = self._create_pie_chart(summary.type_distribution)
            story.append(pie_chart)
            story.append(Spacer(1, 20))
            
            # Bar chart for average values
            bar_chart = self._create_bar_chart(summary)
            story.append(bar_chart)
        
        # Analysis and Insights
        story.append(PageBreak())
        story.append(Paragraph("Analysis & Insights", self.styles['SectionHeader']))
        
        insights = self._generate_insights(summary)
        for insight in insights:
            story.append(Paragraph(f"• {insight}", self.styles['ReportBodyText']))
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(
            "This report was automatically generated by the Chemical Equipment Parameter Visualizer.",
            self.styles['ReportBodyText']
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def _create_pie_chart(self, distribution_data):
        """Create a pie chart for equipment type distribution"""
        drawing = Drawing(400, 300)
        
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 200
        pie.height = 200
        
        # Prepare data
        labels = list(distribution_data.keys())
        values = list(distribution_data.values())
        
        pie.data = values
        pie.labels = labels
        
        # Set colors
        colors_list = [
            HexColor('#FF6384'),
            HexColor('#36A2EB'),
            HexColor('#FFCE56'),
            HexColor('#4BC0C0'),
            HexColor('#9966FF'),
            HexColor('#FF9F40'),
        ]
        
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 2
        
        for i, color in enumerate(colors_list[:len(values)]):
            pie.slices[i].fillColor = color
        
        drawing.add(pie)
        
        # Add title
        from reportlab.graphics.shapes import String
        title = String(200, 280, 'Equipment Type Distribution', textAnchor='middle')
        title.fontSize = 14
        title.fontName = 'Helvetica-Bold'
        drawing.add(title)
        
        return drawing
    
    def _create_bar_chart(self, summary):
        """Create a bar chart for average parameter values"""
        drawing = Drawing(400, 300)
        
        bar_chart = VerticalBarChart()
        bar_chart.x = 50
        bar_chart.y = 50
        bar_chart.height = 200
        bar_chart.width = 300
        
        # Prepare data
        bar_chart.data = [[
            summary.average_flowrate,
            summary.average_pressure * 10,  # Scale pressure for visibility
            summary.average_temperature
        ]]
        
        bar_chart.categoryAxis.categoryNames = ['Flowrate\n(L/min)', 'Pressure\n(bar x10)', 'Temperature\n(°C)']
        bar_chart.valueAxis.valueMin = 0
        bar_chart.valueAxis.valueMax = max(
            summary.average_flowrate,
            summary.average_pressure * 10,
            summary.average_temperature
        ) * 1.1
        
        # Styling
        bar_chart.bars[0].fillColor = HexColor('#36A2EB')
        bar_chart.bars[0].strokeColor = colors.black
        bar_chart.bars[0].strokeWidth = 1
        
        drawing.add(bar_chart)
        
        # Add title
        from reportlab.graphics.shapes import String
        title = String(200, 280, 'Average Parameter Values', textAnchor='middle')
        title.fontSize = 14
        title.fontName = 'Helvetica-Bold'
        drawing.add(title)
        
        return drawing
    
    def _generate_insights(self, summary):
        """Generate analytical insights from the data"""
        insights = []
        
        # Equipment count insight
        if summary.total_equipment > 100:
            insights.append("Large equipment inventory detected - consider implementing automated monitoring systems.")
        elif summary.total_equipment < 10:
            insights.append("Small equipment inventory - suitable for manual monitoring and maintenance.")
        
        # Temperature analysis
        if summary.average_temperature > 200:
            insights.append("High average operating temperature detected - ensure proper thermal management and safety protocols.")
        elif summary.average_temperature < 50:
            insights.append("Low average operating temperature - suitable for standard materials and components.")
        
        # Pressure analysis
        if summary.average_pressure > 15:
            insights.append("High pressure operations detected - verify pressure vessel certifications and safety systems.")
        elif summary.average_pressure < 2:
            insights.append("Low pressure operations - consider energy efficiency optimizations.")
        
        # Equipment diversity
        if summary.type_distribution:
            type_count = len(summary.type_distribution)
            if type_count > 5:
                insights.append("High equipment diversity - implement standardized maintenance procedures across equipment types.")
            elif type_count == 1:
                insights.append("Single equipment type operation - opportunity for specialized optimization and expertise.")
        
        # Flowrate analysis
        if summary.average_flowrate > 500:
            insights.append("High throughput operations - monitor for flow optimization opportunities.")
        
        if not insights:
            insights.append("Equipment parameters are within normal operating ranges.")
        
        return insights
    
    def save_report_to_file(self, filepath, upload_id=None, include_charts=True):
        """
        Save report directly to a file
        
        Args:
            filepath: Path where to save the PDF file
            upload_id: Specific upload to generate report for (None for latest)
            include_charts: Whether to include charts in the report
        """
        pdf_data = self.generate_report(upload_id, include_charts)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_data)
        
        return filepath