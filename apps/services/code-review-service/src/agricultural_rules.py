"""
Agricultural Domain-Specific Rules for SAHOOL
قواعد خاصة بالمجال الزراعي لمنصة سهول

This module provides specialized code review rules for agricultural software,
including NDVI calculations, IoT sensor data, irrigation systems, and more.
"""

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgriculturalIssue:
    """Represents an agricultural domain issue"""

    category: str  # ndvi, lai, sensor, irrigation, etc.
    severity: str  # critical, warning, info
    message_en: str
    message_ar: str
    line_number: int | None = None
    code_snippet: str | None = None

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity,
            "message": f"{self.message_en} / {self.message_ar}",
            "line": self.line_number,
            "snippet": self.code_snippet,
        }


@dataclass
class AgriculturalAnalysis:
    """Results of agricultural code analysis"""

    issues: list[AgriculturalIssue] = field(default_factory=list)
    score_modifier: int = 0  # Adjustment to base score
    is_agricultural_code: bool = False
    detected_domains: list[str] = field(default_factory=list)

    def add_issue(self, issue: AgriculturalIssue):
        """Add an issue and adjust score"""
        self.issues.append(issue)
        if issue.severity == "critical":
            self.score_modifier -= 15
        elif issue.severity == "warning":
            self.score_modifier -= 5
        else:
            self.score_modifier -= 1

    def get_issue_messages(self) -> list[str]:
        """Get formatted issue messages"""
        return [issue.to_dict()["message"] for issue in self.issues]


class AgriculturalRulesEngine:
    """Engine for applying agricultural domain rules"""

    def __init__(self, settings=None):
        self.settings = settings
        self._init_patterns()

    def _init_patterns(self):
        """Initialize regex patterns for detection"""
        # NDVI patterns
        self.ndvi_patterns = [
            re.compile(r"\bndvi\b", re.IGNORECASE),
            re.compile(r"normalized\s*difference\s*vegetation\s*index", re.IGNORECASE),
            re.compile(r"\(nir\s*[-−]\s*red\)\s*/\s*\(nir\s*[+]\s*red\)", re.IGNORECASE),
        ]

        # LAI patterns
        self.lai_patterns = [
            re.compile(r"\blai\b", re.IGNORECASE),
            re.compile(r"leaf\s*area\s*index", re.IGNORECASE),
        ]

        # Sensor/IoT patterns
        self.sensor_patterns = [
            re.compile(r"soil_moisture|soilmoisture", re.IGNORECASE),
            re.compile(r"temperature_sensor|temp_sensor", re.IGNORECASE),
            re.compile(r"humidity_sensor|hum_sensor", re.IGNORECASE),
            re.compile(r"sensor_reading|reading_sensor", re.IGNORECASE),
            re.compile(r"mqtt|nats|iot", re.IGNORECASE),
        ]

        # Irrigation patterns
        self.irrigation_patterns = [
            re.compile(r"irrigation|irrigate", re.IGNORECASE),
            re.compile(r"water_flow|waterflow", re.IGNORECASE),
            re.compile(r"drip|sprinkler", re.IGNORECASE),
            re.compile(r"evapotranspiration|et0|etc", re.IGNORECASE),
        ]

        # Crop/yield patterns
        self.crop_patterns = [
            re.compile(r"crop_health|crophealth", re.IGNORECASE),
            re.compile(r"yield_prediction|yieldprediction", re.IGNORECASE),
            re.compile(r"harvest|planting", re.IGNORECASE),
            re.compile(r"fertilizer|pesticide", re.IGNORECASE),
        ]

        # Value range patterns (for detecting hardcoded values)
        self.value_patterns = {
            "ndvi": re.compile(r"ndvi\s*[=<>]+\s*(-?\d+\.?\d*)", re.IGNORECASE),
            "lai": re.compile(r"lai\s*[=<>]+\s*(\d+\.?\d*)", re.IGNORECASE),
            "soil_moisture": re.compile(r"soil_moisture\s*[=<>]+\s*(\d+\.?\d*)", re.IGNORECASE),
            "temperature": re.compile(r"temperature\s*[=<>]+\s*(-?\d+\.?\d*)", re.IGNORECASE),
        }

    def analyze(self, code: str, filename: str = None) -> AgriculturalAnalysis:
        """Analyze code for agricultural domain issues"""
        analysis = AgriculturalAnalysis()

        # Detect domains
        analysis.detected_domains = self._detect_domains(code)
        analysis.is_agricultural_code = bool(analysis.detected_domains)

        if not analysis.is_agricultural_code:
            return analysis

        # Run domain-specific checks
        lines = code.split("\n")

        if "ndvi" in analysis.detected_domains:
            self._check_ndvi_rules(code, lines, analysis)

        if "lai" in analysis.detected_domains:
            self._check_lai_rules(code, lines, analysis)

        if "sensor" in analysis.detected_domains:
            self._check_sensor_rules(code, lines, analysis)

        if "irrigation" in analysis.detected_domains:
            self._check_irrigation_rules(code, lines, analysis)

        if "crop" in analysis.detected_domains:
            self._check_crop_rules(code, lines, analysis)

        # General agricultural best practices
        self._check_general_agricultural_practices(code, lines, analysis)

        return analysis

    def _detect_domains(self, code: str) -> list[str]:
        """Detect which agricultural domains are present in the code"""
        domains = []

        if any(p.search(code) for p in self.ndvi_patterns):
            domains.append("ndvi")

        if any(p.search(code) for p in self.lai_patterns):
            domains.append("lai")

        if any(p.search(code) for p in self.sensor_patterns):
            domains.append("sensor")

        if any(p.search(code) for p in self.irrigation_patterns):
            domains.append("irrigation")

        if any(p.search(code) for p in self.crop_patterns):
            domains.append("crop")

        return domains

    def _check_ndvi_rules(self, code: str, lines: list[str], analysis: AgriculturalAnalysis):
        """Check NDVI-specific rules"""

        # Rule 1: NDVI values should be in range [-1, 1]
        for i, line in enumerate(lines, 1):
            match = self.value_patterns["ndvi"].search(line)
            if match:
                value = float(match.group(1))
                if value < -1 or value > 1:
                    analysis.add_issue(
                        AgriculturalIssue(
                            category="ndvi",
                            severity="critical",
                            message_en=f"NDVI value {value} is out of valid range [-1, 1]",
                            message_ar=f"قيمة NDVI {value} خارج النطاق الصالح [-1, 1]",
                            line_number=i,
                            code_snippet=line.strip(),
                        )
                    )

        # Rule 2: Check for division by zero protection in NDVI formula
        ndvi_formula_pattern = re.compile(
            r"\(.*nir.*[-−].*red.*\)\s*/\s*\(.*nir.*[+].*red.*\)", re.IGNORECASE
        )
        for i, line in enumerate(lines, 1):
            if ndvi_formula_pattern.search(line):
                # Check if there's division by zero protection nearby
                context_start = max(0, i - 3)
                context_end = min(len(lines), i + 3)
                context = "\n".join(lines[context_start:context_end])
                if not re.search(r"if.*[!=]=\s*0|denominator|divisor|zero", context, re.IGNORECASE):
                    analysis.add_issue(
                        AgriculturalIssue(
                            category="ndvi",
                            severity="warning",
                            message_en="NDVI calculation may lack division by zero protection",
                            message_ar="حساب NDVI قد يفتقر إلى حماية من القسمة على صفر",
                            line_number=i,
                            code_snippet=line.strip(),
                        )
                    )

        # Rule 3: NDVI interpretation thresholds
        if re.search(r"ndvi\s*[<>]=?\s*0\.8", code, re.IGNORECASE):
            # Check if dense vegetation classification is correct
            pass  # Valid threshold

        # Rule 4: Warn about magic numbers in NDVI thresholds
        ndvi_threshold_pattern = re.compile(r"ndvi\s*[<>]=?\s*(-?0\.\d+)", re.IGNORECASE)
        threshold_comments = re.compile(
            r"#.*vegetation|#.*healthy|#.*sparse|//.*vegetation", re.IGNORECASE
        )
        for i, line in enumerate(lines, 1):
            if ndvi_threshold_pattern.search(line) and not threshold_comments.search(line):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="ndvi",
                        severity="info",
                        message_en="NDVI threshold should have a comment explaining its meaning",
                        message_ar="يجب أن يحتوي حد NDVI على تعليق يوضح معناه",
                        line_number=i,
                        code_snippet=line.strip(),
                    )
                )

    def _check_lai_rules(self, code: str, lines: list[str], analysis: AgriculturalAnalysis):
        """Check LAI-specific rules"""

        # Rule 1: LAI values should be in range [0, 10]
        for i, line in enumerate(lines, 1):
            match = self.value_patterns["lai"].search(line)
            if match:
                value = float(match.group(1))
                if value < 0 or value > 10:
                    analysis.add_issue(
                        AgriculturalIssue(
                            category="lai",
                            severity="warning",
                            message_en=f"LAI value {value} is outside typical range [0, 10]",
                            message_ar=f"قيمة LAI {value} خارج النطاق النموذجي [0, 10]",
                            line_number=i,
                            code_snippet=line.strip(),
                        )
                    )

        # Rule 2: LAI should never be negative
        if re.search(r"lai\s*=\s*-\d", code, re.IGNORECASE):
            analysis.add_issue(
                AgriculturalIssue(
                    category="lai",
                    severity="critical",
                    message_en="LAI cannot be negative",
                    message_ar="لا يمكن أن تكون قيمة LAI سالبة",
                )
            )

    def _check_sensor_rules(self, code: str, lines: list[str], analysis: AgriculturalAnalysis):
        """Check IoT sensor rules"""

        # Rule 1: Soil moisture should be 0-100%
        for i, line in enumerate(lines, 1):
            match = self.value_patterns["soil_moisture"].search(line)
            if match:
                value = float(match.group(1))
                if value < 0 or value > 100:
                    analysis.add_issue(
                        AgriculturalIssue(
                            category="sensor",
                            severity="warning",
                            message_en=f"Soil moisture {value}% is outside valid range [0, 100]",
                            message_ar=f"رطوبة التربة {value}% خارج النطاق الصالح [0, 100]",
                            line_number=i,
                            code_snippet=line.strip(),
                        )
                    )

        # Rule 2: Check for sensor data validation
        if re.search(r"sensor.*read|read.*sensor", code, re.IGNORECASE):
            if not re.search(r"valid|check|verify|range|bounds", code, re.IGNORECASE):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="sensor",
                        severity="warning",
                        message_en="Sensor readings should be validated before use",
                        message_ar="يجب التحقق من قراءات الحساسات قبل الاستخدام",
                    )
                )

        # Rule 3: Check for sensor timeout handling
        if re.search(r"sensor|mqtt|nats", code, re.IGNORECASE):
            if not re.search(r"timeout|retry|fallback|default", code, re.IGNORECASE):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="sensor",
                        severity="info",
                        message_en="Consider adding timeout/retry logic for sensor communication",
                        message_ar="يُنصح بإضافة منطق المهلة/إعادة المحاولة لاتصال الحساسات",
                    )
                )

        # Rule 4: Temperature sanity check
        for i, line in enumerate(lines, 1):
            match = self.value_patterns["temperature"].search(line)
            if match:
                value = float(match.group(1))
                # Agricultural temperature typically -40 to 60°C
                if value < -50 or value > 70:
                    analysis.add_issue(
                        AgriculturalIssue(
                            category="sensor",
                            severity="warning",
                            message_en=f"Temperature {value}°C seems unrealistic for agricultural context",
                            message_ar=f"درجة الحرارة {value}°م تبدو غير واقعية للسياق الزراعي",
                            line_number=i,
                            code_snippet=line.strip(),
                        )
                    )

    def _check_irrigation_rules(self, code: str, lines: list[str], analysis: AgriculturalAnalysis):
        """Check irrigation system rules"""

        # Rule 1: ET0 calculation should consider multiple factors
        if re.search(r"et0|evapotranspiration", code, re.IGNORECASE):
            factors = ["temperature", "humidity", "wind", "radiation", "solar"]
            found_factors = sum(1 for f in factors if re.search(f, code, re.IGNORECASE))
            if found_factors < 2:
                analysis.add_issue(
                    AgriculturalIssue(
                        category="irrigation",
                        severity="info",
                        message_en="ET0 calculation typically requires multiple climate factors",
                        message_ar="يتطلب حساب ET0 عادةً عدة عوامل مناخية",
                    )
                )

        # Rule 2: Water flow rates should be positive
        flow_pattern = re.compile(r"water_flow\s*=\s*(-\d+)", re.IGNORECASE)
        for i, line in enumerate(lines, 1):
            if flow_pattern.search(line):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="irrigation",
                        severity="critical",
                        message_en="Water flow rate cannot be negative",
                        message_ar="لا يمكن أن يكون معدل تدفق المياه سالباً",
                        line_number=i,
                        code_snippet=line.strip(),
                    )
                )

        # Rule 3: Irrigation decisions should consider soil moisture
        if re.search(r"irrigat", code, re.IGNORECASE):
            if not re.search(r"soil_moisture|moisture|threshold", code, re.IGNORECASE):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="irrigation",
                        severity="warning",
                        message_en="Irrigation decisions should consider soil moisture levels",
                        message_ar="يجب أن تأخذ قرارات الري في الاعتبار مستويات رطوبة التربة",
                    )
                )

    def _check_crop_rules(self, code: str, lines: list[str], analysis: AgriculturalAnalysis):
        """Check crop/yield rules"""

        # Rule 1: Yield predictions should have confidence intervals
        if re.search(r"yield.*predict|predict.*yield", code, re.IGNORECASE):
            if not re.search(r"confidence|uncertainty|range|error", code, re.IGNORECASE):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="crop",
                        severity="info",
                        message_en="Yield predictions should include confidence/uncertainty measures",
                        message_ar="يجب أن تتضمن توقعات المحصول مقاييس الثقة/عدم اليقين",
                    )
                )

        # Rule 2: Crop health should consider multiple indices
        if re.search(r"crop_health|crophealth", code, re.IGNORECASE):
            indices = ["ndvi", "lai", "ndwi", "evi", "savi"]
            found_indices = sum(1 for idx in indices if re.search(idx, code, re.IGNORECASE))
            if found_indices < 2:
                analysis.add_issue(
                    AgriculturalIssue(
                        category="crop",
                        severity="info",
                        message_en="Consider using multiple vegetation indices for crop health assessment",
                        message_ar="يُنصح باستخدام مؤشرات نباتية متعددة لتقييم صحة المحصول",
                    )
                )

    def _check_general_agricultural_practices(
        self, code: str, lines: list[str], analysis: AgriculturalAnalysis
    ):
        """Check general agricultural coding best practices"""

        # Rule 1: Date/time handling for agricultural data
        if re.search(r"datetime|timestamp|date", code, re.IGNORECASE):
            if not re.search(r"timezone|utc|tz", code, re.IGNORECASE):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="general",
                        severity="info",
                        message_en="Agricultural timestamps should handle timezones explicitly",
                        message_ar="يجب أن تتعامل الطوابع الزمنية الزراعية مع المناطق الزمنية بشكل صريح",
                    )
                )

        # Rule 2: Units should be documented
        unit_vars = ["area", "weight", "volume", "distance", "flow", "rate"]
        for var in unit_vars:
            if re.search(rf"\b{var}\b", code, re.IGNORECASE):
                if not re.search(
                    rf"{var}.*#.*\b(ha|m2|kg|ton|liter|mm|cm|m)\b|{var}_\w+", code, re.IGNORECASE
                ):
                    analysis.add_issue(
                        AgriculturalIssue(
                            category="general",
                            severity="info",
                            message_en=f"Variable '{var}' should document its unit (ha, m², kg, etc.)",
                            message_ar=f"يجب توثيق وحدة المتغير '{var}' (هكتار، م²، كجم، إلخ)",
                        )
                    )
                    break  # Only report once

        # Rule 3: Coordinate validation for field boundaries
        if re.search(r"lat|lon|coordinate|geom|polygon|boundary", code, re.IGNORECASE):
            if not re.search(r"valid|check|bounds|range", code, re.IGNORECASE):
                analysis.add_issue(
                    AgriculturalIssue(
                        category="general",
                        severity="warning",
                        message_en="Geographic coordinates should be validated",
                        message_ar="يجب التحقق من صحة الإحداثيات الجغرافية",
                    )
                )

    def get_enhanced_prompt(self, analysis: AgriculturalAnalysis) -> str:
        """Generate enhanced prompt with agricultural context"""
        if not analysis.is_agricultural_code:
            return ""

        domains = ", ".join(analysis.detected_domains)
        prompt_additions = f"""

IMPORTANT: This code appears to be agricultural/farming related, specifically involving: {domains}

Additional review criteria for agricultural software:
1. NDVI values must be in range [-1, 1] (Normalized Difference Vegetation Index)
2. LAI (Leaf Area Index) values typically range from 0 to 10
3. Soil moisture percentages must be 0-100%
4. IoT sensor readings should be validated before use
5. Irrigation decisions should consider soil moisture thresholds
6. Geographic coordinates for fields should be validated
7. Timestamps should handle timezones for multi-region farming
8. Yield predictions should include confidence intervals
9. ET0 (evapotranspiration) calculations need multiple climate factors
10. Unit documentation is critical (hectares, kg/ha, mm, etc.)

معايير مراجعة إضافية للبرمجيات الزراعية:
1. قيم NDVI يجب أن تكون في النطاق [-1, 1]
2. قيم LAI تتراوح عادةً من 0 إلى 10
3. نسبة رطوبة التربة يجب أن تكون 0-100%
4. يجب التحقق من قراءات حساسات IoT قبل الاستخدام
5. قرارات الري يجب أن تراعي حدود رطوبة التربة
"""
        return prompt_additions
