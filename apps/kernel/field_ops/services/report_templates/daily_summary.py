"""
تقرير يومي - Daily Summary Report Template
===========================================
قالب التقرير اليومي لحقول SAHOOL

Daily summary report template with Arabic/English bilingual support
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import io

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, PageBreak, Image, KeepTogether
    )
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    # Create dummy classes for type hints
    if TYPE_CHECKING:
        from reportlab.platypus import Table, TableStyle
    else:
        Table = None
        TableStyle = None


class DailySummaryReport:
    """
    تقرير يومي شامل
    Comprehensive daily summary report

    Includes:
    - Field status overview
    - Today's readings (NDVI, sensors, weather)
    - Recommendations received
    - Actions taken
    - Visual charts and graphs
    """

    def __init__(self, exporter):
        """
        Initialize daily summary report

        Args:
            exporter: DataExporter instance
        """
        self.exporter = exporter
        self.styles = self._create_styles()

    def _create_styles(self):
        """Create custom styles for the report"""
        if not REPORTLAB_AVAILABLE:
            return None

        styles = getSampleStyleSheet()

        # Title style - bilingual
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#366092'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Arabic heading
        styles.add(ParagraphStyle(
            name='ArabicHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=12,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))

        # English heading
        styles.add(ParagraphStyle(
            name='EnglishHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=10,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Bilingual heading (centered)
        styles.add(ParagraphStyle(
            name='BilingualHeading',
            parent=styles['Heading2'],
            fontSize=15,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Normal text
        styles.add(ParagraphStyle(
            name='NormalArabic',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
        ))

        styles.add(ParagraphStyle(
            name='NormalEnglish',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
        ))

        # Status indicators
        styles.add(ParagraphStyle(
            name='StatusGood',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.green,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='StatusWarning',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.orange,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='StatusCritical',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))

        return styles

    def generate(self, field_id: str, report_date: date) -> 'ExportResult':
        """
        Generate daily summary report

        Args:
            field_id: Field identifier
            report_date: Date for the report

        Returns:
            ExportResult with PDF report
        """
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("reportlab is required for PDF reports")

        # Collect data for the day
        data = self._collect_daily_data(field_id, report_date)

        # Generate PDF
        pdf_data = self._create_pdf(data)

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sahool_daily_summary_{field_id}_{report_date.strftime('%Y%m%d')}_{timestamp}.pdf"

        from ..data_exporter import ExportResult, ExportFormat

        return ExportResult(
            format=ExportFormat.PDF,
            filename=filename,
            content_type="application/pdf",
            data=pdf_data,
            size_bytes=len(pdf_data),
            generated_at=datetime.now(),
            metadata={
                "field_id": field_id,
                "report_type": "daily_summary",
                "report_date": report_date.isoformat()
            }
        )

    def _collect_daily_data(self, field_id: str, report_date: date) -> Dict[str, Any]:
        """Collect all data needed for daily report"""
        date_range = (report_date, report_date)

        return {
            "field_id": field_id,
            "report_date": report_date,
            "generated_at": datetime.now(),
            "metadata": self.exporter._get_field_metadata(field_id),
            "ndvi_today": self._get_today_ndvi(field_id, report_date),
            "ndvi_week": self._get_week_ndvi(field_id, report_date),
            "sensors_today": self.exporter._get_sensor_readings(field_id, date_range),
            "weather_today": self._get_today_weather(field_id, report_date),
            "weather_forecast": self._get_weather_forecast(field_id, report_date),
            "recommendations": self.exporter._get_recommendations(field_id, date_range),
            "actions": self.exporter._get_actions_taken(field_id, date_range),
            "alerts": self._get_alerts(field_id, report_date),
            "summary": self._generate_summary(field_id, report_date),
        }

    def _get_today_ndvi(self, field_id: str, report_date: date) -> Optional[Dict]:
        """Get NDVI for today"""
        history = self.exporter._get_ndvi_history(field_id, (report_date, report_date))
        return history[0] if history else None

    def _get_week_ndvi(self, field_id: str, report_date: date) -> List[Dict]:
        """Get NDVI for past week"""
        start_date = report_date - timedelta(days=7)
        return self.exporter._get_ndvi_history(field_id, (start_date, report_date))

    def _get_today_weather(self, field_id: str, report_date: date) -> Optional[Dict]:
        """Get weather for today"""
        weather = self.exporter._get_weather_data(field_id, (report_date, report_date))
        return weather[0] if weather else None

    def _get_weather_forecast(self, field_id: str, report_date: date) -> List[Dict]:
        """Get weather forecast for next 3 days"""
        # Placeholder - in production, fetch from weather API
        forecast = []
        for i in range(1, 4):
            forecast_date = report_date + timedelta(days=i)
            forecast.append({
                "date": forecast_date.isoformat(),
                "temp_max": 30.0,
                "temp_min": 18.0,
                "rainfall_prob": 10.0,
                "conditions": "مشمس جزئياً"
            })
        return forecast

    def _get_alerts(self, field_id: str, report_date: date) -> List[Dict]:
        """Get active alerts"""
        # Placeholder - fetch from alerts service
        return [
            {
                "type": "irrigation",
                "severity": "warning",
                "message_ar": "رطوبة التربة منخفضة - يُنصح بالري",
                "message_en": "Low soil moisture - irrigation recommended"
            }
        ]

    def _generate_summary(self, field_id: str, report_date: date) -> Dict[str, str]:
        """Generate executive summary"""
        return {
            "status": "good",  # good, warning, critical
            "status_ar": "جيدة",
            "status_en": "Good",
            "summary_ar": "الحقل في حالة جيدة. جميع المؤشرات ضمن النطاق الطبيعي.",
            "summary_en": "Field is in good condition. All indicators within normal range.",
            "action_needed": False
        }

    def _create_pdf(self, data: Dict[str, Any]) -> bytes:
        """Create PDF document"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Add header
        story.extend(self._create_header(data))

        # Add executive summary
        story.extend(self._create_executive_summary(data))

        # Add field information
        story.extend(self._create_field_info(data))

        # Add NDVI section
        story.extend(self._create_ndvi_section(data))

        # Add sensor readings
        story.extend(self._create_sensors_section(data))

        # Add weather section
        story.extend(self._create_weather_section(data))

        # Add recommendations
        story.extend(self._create_recommendations_section(data))

        # Add actions taken
        story.extend(self._create_actions_section(data))

        # Add footer
        story.extend(self._create_footer(data))

        # Build PDF
        doc.build(story)
        return buffer.getvalue()

    def _create_header(self, data: Dict) -> List:
        """Create report header"""
        elements = []

        # SAHOOL Logo placeholder
        # In production, add actual logo image
        # elements.append(Image("path/to/sahool_logo.png", width=2*inch, height=0.8*inch))
        # elements.append(Spacer(1, 0.2*inch))

        # Title - Bilingual
        title = Paragraph(
            "تقرير يومي - Daily Summary Report<br/><font size=14>SAHOOL Agricultural Platform</font>",
            self.styles['ReportTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.1*inch))

        # Report info
        report_info = f"""
        <para align=center>
        <b>التاريخ - Date:</b> {data['report_date'].strftime('%Y-%m-%d')}<br/>
        <b>الحقل - Field:</b> {data['field_id']}<br/>
        <b>تم الإنشاء - Generated:</b> {data['generated_at'].strftime('%Y-%m-%d %H:%M')}
        </para>
        """
        elements.append(Paragraph(report_info, self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Separator line
        elements.append(self._create_separator())
        elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_executive_summary(self, data: Dict) -> List:
        """Create executive summary section"""
        elements = []
        summary = data['summary']

        # Section title
        elements.append(Paragraph(
            "الملخص التنفيذي - Executive Summary",
            self.styles['BilingualHeading']
        ))

        # Status indicator
        status_style = {
            'good': self.styles['StatusGood'],
            'warning': self.styles['StatusWarning'],
            'critical': self.styles['StatusCritical']
        }.get(summary['status'], self.styles['Normal'])

        status_text = f"<b>الحالة - Status:</b> {summary['status_ar']} / {summary['status_en']}"
        elements.append(Paragraph(status_text, status_style))
        elements.append(Spacer(1, 0.1*inch))

        # Summary text
        summary_table_data = [
            ["عربي", summary['summary_ar']],
            ["English", summary['summary_en']]
        ]
        summary_table = Table(summary_table_data, colWidths=[1.5*cm, 14*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))

        # Alerts if any
        if data.get('alerts'):
            elements.append(Paragraph(
                "تنبيهات - Alerts",
                self.styles['BilingualHeading']
            ))
            for alert in data['alerts']:
                alert_text = f"⚠ {alert['message_ar']} / {alert['message_en']}"
                elements.append(Paragraph(alert_text, self.styles['StatusWarning']))
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_field_info(self, data: Dict) -> List:
        """Create field information section"""
        elements = []
        metadata = data['metadata']

        elements.append(Paragraph(
            "معلومات الحقل - Field Information",
            self.styles['BilingualHeading']
        ))

        # Field info table
        field_data = [
            ["Field", "القيمة / Value"],
            ["الاسم / Name", f"{metadata.get('name', '')} / {metadata.get('name_en', '')}"],
            ["المساحة / Area", f"{metadata.get('area_hectares', 0):.2f} هكتار / hectares"],
            ["المحصول / Crop", f"{metadata.get('crop_type', '')} / {metadata.get('crop_type_en', '')}"],
            ["نوع التربة / Soil", metadata.get('soil_type', 'N/A')],
            ["الموقع / Location", f"{metadata.get('location', {}).get('region', '')} - {metadata.get('location', {}).get('district', '')}"],
        ]

        field_table = Table(field_data, colWidths=[5*cm, 10*cm])
        field_table.setStyle(self._get_table_style())
        elements.append(field_table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_ndvi_section(self, data: Dict) -> List:
        """Create NDVI section with trend analysis"""
        elements = []

        elements.append(Paragraph(
            "تحليل NDVI - Vegetation Health Analysis",
            self.styles['BilingualHeading']
        ))

        # Today's NDVI
        if data.get('ndvi_today'):
            ndvi = data['ndvi_today']
            ndvi_data = [
                ["المؤشر / Metric", "القيمة / Value"],
                ["المتوسط / Mean", f"{ndvi.get('mean', 0):.3f}"],
                ["الحد الأدنى / Min", f"{ndvi.get('min', 0):.3f}"],
                ["الحد الأقصى / Max", f"{ndvi.get('max', 0):.3f}"],
                ["الغطاء السحابي / Cloud Cover", f"{ndvi.get('cloud_cover', 0):.1f}%"],
            ]

            ndvi_table = Table(ndvi_data, colWidths=[7*cm, 8*cm])
            ndvi_table.setStyle(self._get_table_style())
            elements.append(ndvi_table)
            elements.append(Spacer(1, 0.2*inch))

            # NDVI interpretation
            mean_ndvi = ndvi.get('mean', 0)
            if mean_ndvi > 0.6:
                interpretation = "صحة نباتية ممتازة / Excellent vegetation health"
                interp_style = self.styles['StatusGood']
            elif mean_ndvi > 0.4:
                interpretation = "صحة نباتية جيدة / Good vegetation health"
                interp_style = self.styles['StatusGood']
            elif mean_ndvi > 0.2:
                interpretation = "صحة نباتية متوسطة / Moderate vegetation health"
                interp_style = self.styles['StatusWarning']
            else:
                interpretation = "صحة نباتية ضعيفة / Poor vegetation health"
                interp_style = self.styles['StatusCritical']

            elements.append(Paragraph(f"<b>التفسير / Interpretation:</b> {interpretation}", interp_style))
            elements.append(Spacer(1, 0.2*inch))

        # Weekly trend
        if data.get('ndvi_week') and len(data['ndvi_week']) > 1:
            elements.append(Paragraph(
                "اتجاه أسبوعي / Weekly Trend",
                self.styles['EnglishHeading']
            ))

            trend_data = [["التاريخ / Date", "NDVI"]]
            for record in data['ndvi_week'][-7:]:
                trend_data.append([record['date'], f"{record.get('mean', 0):.3f}"])

            trend_table = Table(trend_data, colWidths=[7*cm, 8*cm])
            trend_table.setStyle(self._get_table_style())
            elements.append(trend_table)

        elements.append(Spacer(1, 0.3*inch))
        return elements

    def _create_sensors_section(self, data: Dict) -> List:
        """Create sensor readings section"""
        elements = []
        sensors = data.get('sensors_today', [])

        if not sensors:
            return elements

        elements.append(Paragraph(
            "قراءات المستشعرات - Sensor Readings",
            self.styles['BilingualHeading']
        ))

        sensor_data = [["النوع / Type", "القيمة / Value", "الوحدة / Unit", "الموقع / Location"]]

        for sensor in sensors:
            sensor_data.append([
                f"{sensor.get('sensor_type', '')} / {sensor.get('sensor_type_en', '')}",
                f"{sensor.get('value', 0):.2f}",
                sensor.get('unit', ''),
                sensor.get('location', 'N/A')
            ])

        sensor_table = Table(sensor_data, colWidths=[5*cm, 3*cm, 3*cm, 4*cm])
        sensor_table.setStyle(self._get_table_style())
        elements.append(sensor_table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_weather_section(self, data: Dict) -> List:
        """Create weather section"""
        elements = []

        elements.append(Paragraph(
            "الطقس - Weather",
            self.styles['BilingualHeading']
        ))

        # Today's weather
        if data.get('weather_today'):
            weather = data['weather_today']
            weather_data = [
                ["المؤشر / Metric", "القيمة / Value"],
                ["الحرارة القصوى / Max Temp", f"{weather.get('temp_max', 0):.1f}°C"],
                ["الحرارة الدنيا / Min Temp", f"{weather.get('temp_min', 0):.1f}°C"],
                ["الرطوبة / Humidity", f"{weather.get('humidity', 0):.1f}%"],
                ["الأمطار / Rainfall", f"{weather.get('rainfall', 0):.1f} mm"],
                ["سرعة الرياح / Wind Speed", f"{weather.get('wind_speed', 0):.1f} m/s"],
            ]

            weather_table = Table(weather_data, colWidths=[7*cm, 8*cm])
            weather_table.setStyle(self._get_table_style())
            elements.append(weather_table)
            elements.append(Spacer(1, 0.2*inch))

        # Forecast
        if data.get('weather_forecast'):
            elements.append(Paragraph(
                "توقعات الطقس / Weather Forecast (3 days)",
                self.styles['EnglishHeading']
            ))

            forecast_data = [["التاريخ / Date", "الحرارة / Temp", "احتمال المطر / Rain %", "الحالة / Conditions"]]

            for forecast in data['weather_forecast']:
                forecast_data.append([
                    forecast['date'],
                    f"{forecast['temp_max']:.0f}°/{forecast['temp_min']:.0f}°",
                    f"{forecast['rainfall_prob']:.0f}%",
                    forecast['conditions']
                ])

            forecast_table = Table(forecast_data, colWidths=[3.5*cm, 3.5*cm, 4*cm, 4*cm])
            forecast_table.setStyle(self._get_table_style())
            elements.append(forecast_table)

        elements.append(Spacer(1, 0.3*inch))
        return elements

    def _create_recommendations_section(self, data: Dict) -> List:
        """Create recommendations section"""
        elements = []
        recommendations = data.get('recommendations', [])

        if not recommendations:
            return elements

        elements.append(Paragraph(
            "التوصيات - Recommendations",
            self.styles['BilingualHeading']
        ))

        rec_data = [["النوع / Type", "التوصية / Recommendation", "الأولوية / Priority"]]

        for rec in recommendations:
            rec_data.append([
                f"{rec.get('type_ar', '')} / {rec.get('type', '')}",
                rec.get('recommendation', ''),
                rec.get('priority', 'medium')
            ])

        rec_table = Table(rec_data, colWidths=[4*cm, 8*cm, 3*cm])
        rec_table.setStyle(self._get_table_style())
        elements.append(rec_table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_actions_section(self, data: Dict) -> List:
        """Create actions taken section"""
        elements = []
        actions = data.get('actions', [])

        if not actions:
            return elements

        elements.append(Paragraph(
            "الإجراءات المتخذة - Actions Taken",
            self.styles['BilingualHeading']
        ))

        action_data = [["النوع / Type", "الوصف / Description", "الكمية / Amount"]]

        for action in actions:
            action_data.append([
                f"{action.get('action_type_ar', '')} / {action.get('action_type', '')}",
                f"{action.get('description', '')} / {action.get('description_en', '')}",
                action.get('amount', 'N/A')
            ])

        action_table = Table(action_data, colWidths=[4*cm, 8*cm, 3*cm])
        action_table.setStyle(self._get_table_style())
        elements.append(action_table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_footer(self, data: Dict) -> List:
        """Create report footer"""
        elements = []

        elements.append(self._create_separator())
        elements.append(Spacer(1, 0.1*inch))

        footer_text = f"""
        <para align=center>
        <font size=9>
        <b>SAHOOL Agricultural Platform</b> | منصة صحول الزراعية<br/>
        تقرير تم إنشاؤه آليًا - Automatically Generated Report<br/>
        {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}
        </font>
        </para>
        """
        elements.append(Paragraph(footer_text, self.styles['Normal']))

        return elements

    def _get_table_style(self):
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ])

    def _create_separator(self):
        """Create a horizontal separator line"""
        return Table([[""]], colWidths=[17*cm], rowHeights=[0.05*cm], style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#366092')),
        ]))
