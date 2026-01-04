"""
GlobalGAP IFA v6 Checklist Data
بيانات قائمة التحقق GlobalGAP IFA v6

Complete IFA v6 (Integrated Farm Assurance) control points checklist
for Fruit & Vegetables certification.

قائمة التحقق الكاملة لنقاط التحكم IFA v6 (ضمان المزرعة المتكامل)
لشهادة الفواكه والخضروات.
"""


from .constants import ComplianceLevel
from .models import ChecklistCategory, ChecklistItem

# =============================================================================
# IFA v6 CHECKLIST CATEGORIES
# فئات قائمة التحقق IFA v6
# =============================================================================

# -----------------------------------------------------------------------------
# SITE HISTORY AND MANAGEMENT
# تاريخ الموقع والإدارة
# -----------------------------------------------------------------------------
SITE_HISTORY_ITEMS = [
    ChecklistItem(
        id="AF.1.1.1",
        category_code="SITE_HISTORY",
        subcategory="Site History",
        title_en="Site history and risk assessment",
        title_ar="تاريخ الموقع وتقييم المخاطر",
        description_en="Has a documented risk assessment of the site history been conducted, covering previous use and potential contamination risks?",
        description_ar="هل تم إجراء تقييم موثق للمخاطر لتاريخ الموقع، يغطي الاستخدام السابق ومخاطر التلوث المحتملة؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Maintain records of previous land use, identify potential contamination sources (industrial sites, flooding areas, waste dumps)",
        guidance_ar="احتفظ بسجلات الاستخدام السابق للأرض، وحدد مصادر التلوث المحتملة (المواقع الصناعية، مناطق الفيضانات، مكبات النفايات)",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.1.1.2",
        category_code="SITE_HISTORY",
        subcategory="Site History",
        title_en="Soil analysis for new sites",
        title_ar="تحليل التربة للمواقع الجديدة",
        description_en="For new production sites or sites with identified risks, has soil analysis been conducted to verify suitability for food production?",
        description_ar="للمواقع الإنتاجية الجديدة أو المواقع ذات المخاطر المحددة، هل تم إجراء تحليل التربة للتحقق من ملاءمتها لإنتاج الغذاء؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["TEST_RESULT", "DOCUMENT"],
        guidance_en="Test for heavy metals (Cd, Pb, Hg, As) and persistent organic pollutants if risk identified",
        guidance_ar="اختبر المعادن الثقيلة (الكادميوم، الرصاص، الزئبق، الزرنيخ) والملوثات العضوية الثابتة إذا تم تحديد المخاطر",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=2,
    ),
    ChecklistItem(
        id="AF.1.2.1",
        category_code="SITE_HISTORY",
        subcategory="Farm Management Plan",
        title_en="Farm management plan exists",
        title_ar="وجود خطة إدارة المزرعة",
        description_en="Is there a documented farm management plan covering all production activities and compliance requirements?",
        description_ar="هل توجد خطة موثقة لإدارة المزرعة تغطي جميع أنشطة الإنتاج ومتطلبات الامتثال؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Plan should include production areas, crops grown, rotation plans, and key processes",
        guidance_ar="يجب أن تتضمن الخطة مناطق الإنتاج والمحاصيل المزروعة وخطط الدورة الزراعية والعمليات الرئيسية",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=3,
    ),
]

# -----------------------------------------------------------------------------
# RECORD KEEPING AND DOCUMENTATION
# حفظ السجلات والتوثيق
# -----------------------------------------------------------------------------
RECORD_KEEPING_ITEMS = [
    ChecklistItem(
        id="AF.2.1.1",
        category_code="RECORD_KEEPING",
        subcategory="Records Management",
        title_en="Record keeping system",
        title_ar="نظام حفظ السجلات",
        description_en="Is there a comprehensive record keeping system that maintains all required documentation for at least 2 years?",
        description_ar="هل يوجد نظام شامل لحفظ السجلات يحتفظ بجميع الوثائق المطلوبة لمدة سنتين على الأقل؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Records must be accessible, organized, and include production, harvest, inputs, training, and audit records",
        guidance_ar="يجب أن تكون السجلات متاحة ومنظمة وتشمل الإنتاج والحصاد والمدخلات والتدريب وسجلات التدقيق",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.2.1.2",
        category_code="RECORD_KEEPING",
        subcategory="Records Management",
        title_en="Document control and version management",
        title_ar="التحكم في المستندات وإدارة الإصدارات",
        description_en="Are procedures and work instructions version controlled with clear identification of current versions?",
        description_ar="هل يتم التحكم في إصدارات الإجراءات وتعليمات العمل مع تحديد واضح للإصدارات الحالية؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Use version numbers, dates, and approval signatures; maintain obsolete versions separately",
        guidance_ar="استخدم أرقام الإصدارات والتواريخ وتوقيعات الموافقة؛ احتفظ بالإصدارات القديمة بشكل منفصل",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.2.2.1",
        category_code="RECORD_KEEPING",
        subcategory="Internal Audits",
        title_en="Internal self-assessment",
        title_ar="التقييم الذاتي الداخلي",
        description_en="Has an internal self-assessment against all applicable control points been conducted in the last 12 months?",
        description_ar="هل تم إجراء تقييم ذاتي داخلي مقابل جميع نقاط التحكم المعمول بها خلال الـ 12 شهراً الماضية؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Document findings, corrective actions, and evidence of implementation",
        guidance_ar="وثق النتائج والإجراءات التصحيحية وأدلة التنفيذ",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=3,
    ),
    ChecklistItem(
        id="AF.2.3.1",
        category_code="RECORD_KEEPING",
        subcategory="Complaints",
        title_en="Complaints handling procedure",
        title_ar="إجراء معالجة الشكاوى",
        description_en="Is there a documented procedure for receiving, recording, and responding to customer complaints?",
        description_ar="هل يوجد إجراء موثق لاستقبال وتسجيل والرد على شكاوى العملاء؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Include complaint registration, investigation, corrective action, and customer communication",
        guidance_ar="تضمين تسجيل الشكاوى والتحقيق والإجراءات التصحيحية والتواصل مع العملاء",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=4,
    ),
]

# -----------------------------------------------------------------------------
# WORKERS HEALTH, SAFETY AND WELFARE (GRASP)
# صحة وسلامة ورفاهية العمال
# -----------------------------------------------------------------------------
WORKERS_HEALTH_ITEMS = [
    ChecklistItem(
        id="AF.3.1.1",
        category_code="WORKERS_HEALTH",
        subcategory="Risk Assessment",
        title_en="Occupational health and safety risk assessment",
        title_ar="تقييم مخاطر الصحة والسلامة المهنية",
        description_en="Has a documented risk assessment been conducted covering all work activities and potential hazards?",
        description_ar="هل تم إجراء تقييم موثق للمخاطر يغطي جميع أنشطة العمل والمخاطر المحتملة؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Identify chemical, physical, biological hazards; assess likelihood and severity; implement controls",
        guidance_ar="حدد المخاطر الكيميائية والفيزيائية والبيولوجية؛ قيّم الاحتمالية والخطورة؛ نفذ الضوابط",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.3.2.1",
        category_code="WORKERS_HEALTH",
        subcategory="Training",
        title_en="Worker training program",
        title_ar="برنامج تدريب العمال",
        description_en="Are all workers trained on health, safety, and hygiene requirements relevant to their work activities?",
        description_ar="هل تم تدريب جميع العمال على متطلبات الصحة والسلامة والنظافة ذات الصلة بأنشطة عملهم؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "INTERVIEW", "OBSERVATION"],
        guidance_en="Maintain training records with dates, topics, trainer, attendees; verify understanding through competence assessment",
        guidance_ar="احتفظ بسجلات التدريب مع التواريخ والموضوعات والمدرب والحضور؛ تحقق من الفهم من خلال تقييم الكفاءة",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.3.3.1",
        category_code="WORKERS_HEALTH",
        subcategory="PPE",
        title_en="Personal protective equipment provision",
        title_ar="توفير معدات الحماية الشخصية",
        description_en="Is appropriate personal protective equipment (PPE) provided free of charge to all workers who need it?",
        description_ar="هل يتم توفير معدات الحماية الشخصية (PPE) المناسبة مجاناً لجميع العمال الذين يحتاجون إليها؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["OBSERVATION", "DOCUMENT", "INTERVIEW"],
        guidance_en="PPE must include gloves, masks, goggles, boots as required; maintain records of distribution",
        guidance_ar="يجب أن تشمل معدات الحماية القفازات والأقنعة والنظارات والأحذية حسب الحاجة؛ احتفظ بسجلات التوزيع",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=3,
    ),
    ChecklistItem(
        id="AF.3.4.1",
        category_code="WORKERS_HEALTH",
        subcategory="Welfare",
        title_en="Welfare facilities - drinking water",
        title_ar="مرافق الرفاهية - مياه الشرب",
        description_en="Is clean drinking water available and accessible to all workers at all times during work?",
        description_ar="هل تتوفر مياه الشرب النظيفة ويمكن الوصول إليها لجميع العمال في جميع الأوقات أثناء العمل؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["OBSERVATION"],
        guidance_en="Provide potable water in sufficient quantity; protect from contamination; accessible in all work areas",
        guidance_ar="وفر المياه الصالحة للشرب بكمية كافية؛ احمها من التلوث؛ متاحة في جميع مناطق العمل",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=4,
    ),
    ChecklistItem(
        id="AF.3.4.2",
        category_code="WORKERS_HEALTH",
        subcategory="Welfare",
        title_en="Welfare facilities - toilets and handwashing",
        title_ar="مرافق الرفاهية - المراحيض وغسل اليدين",
        description_en="Are clean toilets with handwashing facilities available in sufficient numbers near work areas?",
        description_ar="هل تتوفر مراحيض نظيفة مع مرافق غسل اليدين بأعداد كافية بالقرب من مناطق العمل؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["OBSERVATION"],
        guidance_en="Ratio 1:20 workers; provide soap and drying facilities; maintain cleanliness; ensure privacy",
        guidance_ar="النسبة 1:20 عامل؛ وفر الصابون ومرافق التجفيف؛ حافظ على النظافة؛ ضمن الخصوصية",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=5,
    ),
    ChecklistItem(
        id="AF.3.5.1",
        category_code="WORKERS_HEALTH",
        subcategory="First Aid",
        title_en="First aid facilities and trained personnel",
        title_ar="مرافق الإسعافات الأولية والموظفين المدربين",
        description_en="Are first aid facilities available and is there at least one trained first aider on site during work hours?",
        description_ar="هل تتوفر مرافق الإسعافات الأولية وهل يوجد على الأقل مسعف مدرب واحد في الموقع أثناء ساعات العمل؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["OBSERVATION", "DOCUMENT", "INTERVIEW"],
        guidance_en="Maintain stocked first aid kit; train personnel in first aid; display emergency contact numbers",
        guidance_ar="احتفظ بمجموعة إسعافات أولية مجهزة؛ درب الموظفين على الإسعافات الأولية؛ اعرض أرقام الاتصال الطارئة",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=6,
    ),
    ChecklistItem(
        id="AF.3.6.1",
        category_code="WORKERS_HEALTH",
        subcategory="Child Labor",
        title_en="No child labor",
        title_ar="عدم عمالة الأطفال",
        description_en="Are there procedures to ensure no workers under minimum working age are employed in any capacity?",
        description_ar="هل توجد إجراءات لضمان عدم توظيف عمال دون الحد الأدنى لسن العمل بأي صفة؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION", "INTERVIEW"],
        guidance_en="Verify age through documentation; minimum age 15 years (or as per local law if higher)",
        guidance_ar="تحقق من العمر من خلال الوثائق؛ الحد الأدنى للسن 15 سنة (أو حسب القانون المحلي إذا كان أعلى)",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=7,
    ),
]

# -----------------------------------------------------------------------------
# TRACEABILITY AND SEGREGATION
# التتبع والفصل
# -----------------------------------------------------------------------------
TRACEABILITY_ITEMS = [
    ChecklistItem(
        id="AF.4.1.1",
        category_code="TRACEABILITY",
        subcategory="Product Traceability",
        title_en="Traceability system - one step forward, one step back",
        title_ar="نظام التتبع - خطوة للأمام وخطوة للخلف",
        description_en="Is there a traceability system that allows tracking products one step forward (to customers) and one step back (to suppliers/fields)?",
        description_ar="هل يوجد نظام تتبع يسمح بتتبع المنتجات خطوة واحدة للأمام (للعملاء) وخطوة واحدة للخلف (للموردين/الحقول)؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Link products to production batches, fields, harvest dates, packing dates, and customers",
        guidance_ar="ربط المنتجات بدفعات الإنتاج والحقول وتواريخ الحصاد وتواريخ التعبئة والعملاء",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.4.1.2",
        category_code="TRACEABILITY",
        subcategory="Product Traceability",
        title_en="Traceability test and mass balance",
        title_ar="اختبار التتبع والتوازن الكتلي",
        description_en="Has a documented traceability test been conducted in the last 12 months, including mass balance verification?",
        description_ar="هل تم إجراء اختبار تتبع موثق في آخر 12 شهراً، بما في ذلك التحقق من التوازن الكتلي؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Select a product batch, trace forward and backward, verify quantities match within tolerance (±5%)",
        guidance_ar="اختر دفعة منتج، تتبع للأمام والخلف، تحقق من تطابق الكميات ضمن التفاوت (±5%)",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.4.2.1",
        category_code="TRACEABILITY",
        subcategory="Segregation",
        title_en="Certified and non-certified product segregation",
        title_ar="فصل المنتجات المعتمدة وغير المعتمدة",
        description_en="Where certified and non-certified products are handled, are adequate segregation procedures in place?",
        description_ar="عندما يتم التعامل مع المنتجات المعتمدة وغير المعتمدة، هل توجد إجراءات فصل كافية؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Physical or temporal separation; clear identification; separate records; prevent mixing",
        guidance_ar="فصل فيزيائي أو زمني؛ تحديد واضح؛ سجلات منفصلة؛ منع الاختلاط",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=3,
    ),
    ChecklistItem(
        id="AF.4.3.1",
        category_code="TRACEABILITY",
        subcategory="GGN Marking",
        title_en="GGN marking on products",
        title_ar="وضع علامة GGN على المنتجات",
        description_en="Are GlobalGAP certified products clearly marked with the GGN or product label?",
        description_ar="هل المنتجات المعتمدة من GlobalGAP موسومة بوضوح برقم GGN أو ملصق المنتج؟",
        compliance_level=ComplianceLevel.RECOMMENDATION,
        evidence_required=["OBSERVATION", "DOCUMENT"],
        guidance_en="Apply GGN to packaging, invoices, or delivery documents to facilitate customer verification",
        guidance_ar="طبق رقم GGN على التعبئة أو الفواتير أو مستندات التسليم لتسهيل التحقق من العملاء",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=4,
    ),
]

# -----------------------------------------------------------------------------
# PLANT PROPAGATION MATERIAL
# مواد التكاثر النباتي
# -----------------------------------------------------------------------------
PLANT_PROPAGATION_ITEMS = [
    ChecklistItem(
        id="AF.5.1.1",
        category_code="PLANT_PROPAGATION",
        subcategory="Seed and Planting Material",
        title_en="Source of propagation material",
        title_ar="مصدر مواد التكاثر",
        description_en="Are records maintained for all seeds and planting material sources, including supplier details?",
        description_ar="هل يتم الاحتفاظ بسجلات لجميع مصادر البذور ومواد الزراعة، بما في ذلك تفاصيل الموردين؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Record variety, supplier, batch/lot number, purchase date, certificates if available",
        guidance_ar="سجل الصنف والمورد ورقم الدفعة/اللوت وتاريخ الشراء والشهادات إن وجدت",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.5.2.1",
        category_code="PLANT_PROPAGATION",
        subcategory="GMO",
        title_en="GMO status awareness",
        title_ar="الوعي بحالة الكائنات المعدلة وراثياً",
        description_en="Is the GMO status of propagation material known and documented?",
        description_ar="هل حالة الكائنات المعدلة وراثياً لمواد التكاثر معروفة وموثقة؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Obtain supplier declarations; document GMO or non-GMO status; comply with local regulations",
        guidance_ar="احصل على إقرارات الموردين؛ وثق حالة الكائنات المعدلة وراثياً أو غير المعدلة؛ الامتثال للوائح المحلية",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
]

# -----------------------------------------------------------------------------
# SOIL MANAGEMENT
# إدارة التربة
# -----------------------------------------------------------------------------
SOIL_MANAGEMENT_ITEMS = [
    ChecklistItem(
        id="AF.6.1.1",
        category_code="SOIL_MANAGEMENT",
        subcategory="Soil Conservation",
        title_en="Soil erosion prevention",
        title_ar="منع تآكل التربة",
        description_en="Are soil conservation practices implemented to prevent erosion where risk exists?",
        description_ar="هل يتم تنفيذ ممارسات حفظ التربة لمنع التآكل حيث يوجد خطر؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["OBSERVATION", "DOCUMENT"],
        guidance_en="Implement terracing, contour plowing, cover crops, mulching, or other erosion control measures",
        guidance_ar="نفذ المدرجات أو الحراثة الكنتورية أو المحاصيل الغطائية أو التغطية أو غيرها من تدابير مكافحة التآكل",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=1,
    ),
    ChecklistItem(
        id="AF.6.2.1",
        category_code="SOIL_MANAGEMENT",
        subcategory="Soil Analysis",
        title_en="Soil fertility analysis",
        title_ar="تحليل خصوبة التربة",
        description_en="Has soil analysis for fertility been conducted at least once every 4 years or as recommended?",
        description_ar="هل تم إجراء تحليل التربة للخصوبة مرة واحدة على الأقل كل 4 سنوات أو حسب التوصية؟",
        compliance_level=ComplianceLevel.RECOMMENDATION,
        evidence_required=["TEST_RESULT", "DOCUMENT"],
        guidance_en="Test for pH, organic matter, N-P-K, and micronutrients; use results for fertilization planning",
        guidance_ar="اختبر الرقم الهيدروجيني والمادة العضوية وN-P-K والعناصر الدقيقة؛ استخدم النتائج لتخطيط التسميد",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.6.3.1",
        category_code="SOIL_MANAGEMENT",
        subcategory="Substrates",
        title_en="Growing substrate quality for containerized production",
        title_ar="جودة الركيزة النامية للإنتاج في الحاويات",
        description_en="For containerized or substrate-grown crops, is substrate source documented and free from contaminants?",
        description_ar="للمحاصيل المزروعة في الحاويات أو الركائز، هل مصدر الركيزة موثق وخالٍ من الملوثات؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Record substrate source, composition; ensure no sewage sludge or contaminated materials used",
        guidance_ar="سجل مصدر الركيزة والتركيب؛ تأكد من عدم استخدام حمأة الصرف الصحي أو المواد الملوثة",
        applicable_to=["FV"],
        not_applicable_allowed=True,
        order=3,
    ),
]

# -----------------------------------------------------------------------------
# FERTILIZER APPLICATION
# تطبيق الأسمدة
# -----------------------------------------------------------------------------
FERTILIZER_ITEMS = [
    ChecklistItem(
        id="AF.7.1.1",
        category_code="FERTILIZER",
        subcategory="Fertilizer Records",
        title_en="Fertilizer application records",
        title_ar="سجلات تطبيق الأسمدة",
        description_en="Are detailed records maintained for all fertilizer applications, including type, quantity, date, and location?",
        description_ar="هل يتم الاحتفاظ بسجلات مفصلة لجميع تطبيقات الأسمدة، بما في ذلك النوع والكمية والتاريخ والموقع؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Record for each application: field/plot, crop, fertilizer type, rate (kg/ha), date, operator",
        guidance_ar="سجل لكل تطبيق: الحقل/القطعة، المحصول، نوع السماد، المعدل (كجم/هكتار)، التاريخ، المشغل",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.7.2.1",
        category_code="FERTILIZER",
        subcategory="Organic Fertilizers",
        title_en="Organic fertilizer risk assessment",
        title_ar="تقييم مخاطر الأسمدة العضوية",
        description_en="For organic fertilizers (manure, compost), has a risk assessment been conducted and controls implemented?",
        description_ar="للأسمدة العضوية (السماد الطبيعي، الكمبوست)، هل تم إجراء تقييم للمخاطر وتنفيذ الضوابط؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Assess microbial risks, contamination sources; implement composting, timing restrictions, or incorporation",
        guidance_ar="قيّم المخاطر الميكروبية ومصادر التلوث؛ نفذ التحويل إلى سماد أو قيود التوقيت أو الدمج",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=2,
    ),
    ChecklistItem(
        id="AF.7.2.2",
        category_code="FERTILIZER",
        subcategory="Organic Fertilizers",
        title_en="Organic fertilizer source and treatment",
        title_ar="مصدر ومعالجة الأسمدة العضوية",
        description_en="Is the source of organic fertilizers documented, and have they been adequately treated or composted?",
        description_ar="هل مصدر الأسمدة العضوية موثق، وهل تمت معالجتها أو تحويلها إلى سماد بشكل كافٍ؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "TEST_RESULT"],
        guidance_en="Document origin; compost to reach 55°C for 15 days or equivalent treatment; test for pathogens if risk exists",
        guidance_ar="وثق المنشأ؛ حوّل إلى سماد للوصول إلى 55 درجة مئوية لمدة 15 يوماً أو معالجة مكافئة؛ اختبر الممرضات إذا كان هناك خطر",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=3,
    ),
    ChecklistItem(
        id="AF.7.3.1",
        category_code="FERTILIZER",
        subcategory="Inorganic Fertilizers",
        title_en="Inorganic fertilizer storage",
        title_ar="تخزين الأسمدة غير العضوية",
        description_en="Are inorganic fertilizers stored in a designated area, protected from weather, and separated from other materials?",
        description_ar="هل يتم تخزين الأسمدة غير العضوية في منطقة مخصصة ومحمية من الطقس ومفصولة عن المواد الأخرى؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["OBSERVATION"],
        guidance_en="Store in dry, ventilated area; keep in original packaging or labeled containers; separate from PPP and food",
        guidance_ar="خزن في منطقة جافة ومهواة؛ احتفظ في التعبئة الأصلية أو حاويات موسومة؛ افصل عن المبيدات والطعام",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=4,
    ),
]

# -----------------------------------------------------------------------------
# IRRIGATION AND WATER MANAGEMENT (SPRING)
# الري وإدارة المياه
# -----------------------------------------------------------------------------
IRRIGATION_ITEMS = [
    ChecklistItem(
        id="AF.8.1.1",
        category_code="IRRIGATION",
        subcategory="Water Source",
        title_en="Water source risk assessment",
        title_ar="تقييم مخاطر مصدر المياه",
        description_en="Has a documented risk assessment of all water sources been conducted, identifying potential contamination risks?",
        description_ar="هل تم إجراء تقييم موثق للمخاطر لجميع مصادر المياه، وتحديد مخاطر التلوث المحتملة؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Identify source types (well, river, municipal); assess upstream activities, flooding, animal access, cross-connections",
        guidance_ar="حدد أنواع المصادر (بئر، نهر، بلدي)؛ قيّم الأنشطة المنبعية والفيضانات ووصول الحيوانات والتوصيلات المتقاطعة",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.8.2.1",
        category_code="IRRIGATION",
        subcategory="Water Quality",
        title_en="Irrigation water quality testing",
        title_ar="اختبار جودة مياه الري",
        description_en="Is irrigation water tested annually for microbiological and chemical parameters according to risk assessment?",
        description_ar="هل يتم اختبار مياه الري سنوياً للمعايير الميكروبيولوجية والكيميائية وفقاً لتقييم المخاطر؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["TEST_RESULT", "DOCUMENT"],
        guidance_en="Test for E. coli, heavy metals if risk identified; increase frequency if high-risk source or product contact",
        guidance_ar="اختبر الإيكولاي والمعادن الثقيلة إذا تم تحديد المخاطر؛ زد التكرار إذا كان المصدر عالي المخاطر أو ملامس للمنتج",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.8.3.1",
        category_code="IRRIGATION",
        subcategory="Water Treatment",
        title_en="Water treatment when needed",
        title_ar="معالجة المياه عند الحاجة",
        description_en="Where water quality testing shows contamination, are appropriate treatment measures implemented?",
        description_ar="عندما يُظهر اختبار جودة المياه تلوثاً، هل يتم تنفيذ تدابير معالجة مناسبة؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION", "TEST_RESULT"],
        guidance_en="Implement filtration, UV treatment, chlorination, or other methods; verify effectiveness through testing",
        guidance_ar="نفذ الترشيح أو معالجة الأشعة فوق البنفسجية أو الكلورة أو طرق أخرى؛ تحقق من الفعالية من خلال الاختبار",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=3,
    ),
    ChecklistItem(
        id="AF.8.4.1",
        category_code="IRRIGATION",
        subcategory="Water Conservation",
        title_en="Water use efficiency measures",
        title_ar="تدابير كفاءة استخدام المياه",
        description_en="Are water conservation practices implemented to reduce water use and prevent waste?",
        description_ar="هل يتم تنفيذ ممارسات حفظ المياه للحد من استخدام المياه ومنع الهدر؟",
        compliance_level=ComplianceLevel.RECOMMENDATION,
        evidence_required=["OBSERVATION", "DOCUMENT"],
        guidance_en="Use drip irrigation, soil moisture monitoring, irrigation scheduling, mulching, or rainwater collection",
        guidance_ar="استخدم الري بالتنقيط أو مراقبة رطوبة التربة أو جدولة الري أو التغطية أو جمع مياه الأمطار",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=4,
    ),
]

# -----------------------------------------------------------------------------
# INTEGRATED PEST MANAGEMENT (IPM)
# الإدارة المتكاملة للآفات
# -----------------------------------------------------------------------------
IPM_ITEMS = [
    ChecklistItem(
        id="AF.9.1.1",
        category_code="IPM",
        subcategory="IPM Strategy",
        title_en="Documented IPM plan",
        title_ar="خطة موثقة للإدارة المتكاملة للآفات",
        description_en="Is there a documented Integrated Pest Management plan prioritizing non-chemical control methods?",
        description_ar="هل توجد خطة موثقة للإدارة المتكاملة للآفات تعطي الأولوية لطرق المكافحة غير الكيميائية؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Document pest monitoring, thresholds, preventive measures, biological controls, and chemical use as last resort",
        guidance_ar="وثق مراقبة الآفات والعتبات والتدابير الوقائية والضوابط البيولوجية والاستخدام الكيميائي كملاذ أخير",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.9.2.1",
        category_code="IPM",
        subcategory="Monitoring",
        title_en="Pest monitoring and scouting",
        title_ar="مراقبة وكشف الآفات",
        description_en="Is regular pest monitoring and scouting conducted and documented?",
        description_ar="هل يتم إجراء وتوثيق مراقبة وكشف منتظم للآفات؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Record inspection date, location, pest species, severity, and action taken; use traps or visual inspection",
        guidance_ar="سجل تاريخ الفحص والموقع وأنواع الآفات والخطورة والإجراء المتخذ؛ استخدم المصائد أو الفحص البصري",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.9.3.1",
        category_code="IPM",
        subcategory="Non-Chemical Methods",
        title_en="Use of non-chemical pest control",
        title_ar="استخدام مكافحة الآفات غير الكيميائية",
        description_en="Are non-chemical pest control methods (cultural, physical, biological) used where feasible?",
        description_ar="هل يتم استخدام طرق مكافحة الآفات غير الكيميائية (الثقافية، الفيزيائية، البيولوجية) حيثما كان ذلك ممكناً؟",
        compliance_level=ComplianceLevel.RECOMMENDATION,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Implement crop rotation, resistant varieties, beneficial insects, traps, barriers, or mechanical removal",
        guidance_ar="نفذ دورة المحاصيل أو الأصناف المقاومة أو الحشرات المفيدة أو المصائد أو الحواجز أو الإزالة الميكانيكية",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=3,
    ),
]

# -----------------------------------------------------------------------------
# PLANT PROTECTION PRODUCTS (PPP)
# منتجات وقاية النباتات
# -----------------------------------------------------------------------------
PLANT_PROTECTION_ITEMS = [
    ChecklistItem(
        id="AF.10.1.1",
        category_code="PLANT_PROTECTION",
        subcategory="PPP Authorization",
        title_en="Only authorized PPP used",
        title_ar="استخدام منتجات وقاية النباتات المصرح بها فقط",
        description_en="Are only plant protection products authorized in the country of use and for the target crop being applied?",
        description_ar="هل يتم تطبيق منتجات وقاية النباتات المصرح بها فقط في بلد الاستخدام وللمحصول المستهدف؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Verify registration status; check approved crop on label; maintain list of authorized products",
        guidance_ar="تحقق من حالة التسجيل؛ تحقق من المحصول المعتمد على الملصق؛ احتفظ بقائمة المنتجات المصرح بها",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.10.2.1",
        category_code="PLANT_PROTECTION",
        subcategory="PPP Records",
        title_en="Complete PPP application records",
        title_ar="سجلات تطبيق منتجات وقاية النباتات الكاملة",
        description_en="Are complete records maintained for all PPP applications including product, rate, date, operator, and PHI?",
        description_ar="هل يتم الاحتفاظ بسجلات كاملة لجميع تطبيقات منتجات وقاية النباتات بما في ذلك المنتج والمعدل والتاريخ والمشغل وفترة ما قبل الحصاد؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Record: field, crop, pest, product name, active ingredient, rate, water volume, date, operator, PHI, harvest date",
        guidance_ar="سجل: الحقل، المحصول، الآفة، اسم المنتج، المادة الفعالة، المعدل، حجم الماء، التاريخ، المشغل، فترة ما قبل الحصاد، تاريخ الحصاد",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.10.3.1",
        category_code="PLANT_PROTECTION",
        subcategory="PPP Storage",
        title_en="Safe PPP storage facility",
        title_ar="مرفق تخزين آمن لمنتجات وقاية النباتات",
        description_en="Are PPP stored in a dedicated, locked, well-ventilated facility with restricted access?",
        description_ar="هل يتم تخزين منتجات وقاية النباتات في مرفق مخصص ومقفل وجيد التهوية مع وصول مقيد؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["OBSERVATION"],
        guidance_en="Lockable room/cabinet; solid floor; ventilation; warning signs; fire extinguisher; spill kit; away from food/feed",
        guidance_ar="غرفة/خزانة قابلة للقفل؛ أرضية صلبة؛ تهوية؛ علامات تحذير؛ طفاية حريق؛ مجموعة للانسكابات؛ بعيداً عن الطعام/العلف",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=3,
    ),
    ChecklistItem(
        id="AF.10.4.1",
        category_code="PLANT_PROTECTION",
        subcategory="PPP Application",
        title_en="Calibrated application equipment",
        title_ar="معدات التطبيق المعايرة",
        description_en="Is all PPP application equipment calibrated at least annually and records maintained?",
        description_ar="هل يتم معايرة جميع معدات تطبيق منتجات وقاية النباتات سنوياً على الأقل والاحتفاظ بالسجلات؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Calibrate sprayers to ensure accurate application rates; record calibration date, method, and results",
        guidance_ar="عاير الرشاشات لضمان معدلات تطبيق دقيقة؛ سجل تاريخ المعايرة والطريقة والنتائج",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=4,
    ),
    ChecklistItem(
        id="AF.10.5.1",
        category_code="PLANT_PROTECTION",
        subcategory="Operator Safety",
        title_en="PPP operator training",
        title_ar="تدريب مشغلي منتجات وقاية النباتات",
        description_en="Are all PPP applicators trained in safe handling, application, and emergency procedures?",
        description_ar="هل تم تدريب جميع مطبقي منتجات وقاية النباتات على المعالجة الآمنة والتطبيق وإجراءات الطوارئ؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "INTERVIEW"],
        guidance_en="Train on label reading, PPE use, mixing, application, disposal, first aid; maintain training records",
        guidance_ar="درب على قراءة الملصقات واستخدام معدات الحماية والخلط والتطبيق والتخلص والإسعافات الأولية؛ احتفظ بسجلات التدريب",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=5,
    ),
    ChecklistItem(
        id="AF.10.6.1",
        category_code="PLANT_PROTECTION",
        subcategory="PHI Compliance",
        title_en="Pre-harvest interval compliance",
        title_ar="الامتثال لفترة ما قبل الحصاد",
        description_en="Are pre-harvest intervals (PHI) for all PPP applications verified and documented before harvest?",
        description_ar="هل يتم التحقق من فترات ما قبل الحصاد (PHI) لجميع تطبيقات منتجات وقاية النباتات وتوثيقها قبل الحصاد؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Check label PHI; calculate harvest eligibility date; do not harvest before PHI expires",
        guidance_ar="تحقق من فترة ما قبل الحصاد على الملصق؛ احسب تاريخ أهلية الحصاد؛ لا تحصد قبل انتهاء فترة ما قبل الحصاد",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=6,
    ),
]

# -----------------------------------------------------------------------------
# HARVEST AND HARVESTING PROCEDURES
# الحصاد وإجراءات الحصاد
# -----------------------------------------------------------------------------
HARVEST_ITEMS = [
    ChecklistItem(
        id="AF.11.1.1",
        category_code="HARVEST",
        subcategory="Harvest Procedures",
        title_en="Documented harvest procedures",
        title_ar="إجراءات الحصاد الموثقة",
        description_en="Are documented harvest procedures in place covering hygiene, equipment, and product handling?",
        description_ar="هل توجد إجراءات موثقة للحصاد تغطي النظافة والمعدات ومعالجة المنتجات؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Document harvest timing, hygiene requirements, container cleanliness, field sorting, transport to packhouse",
        guidance_ar="وثق توقيت الحصاد ومتطلبات النظافة ونظافة الحاويات والفرز الميداني والنقل إلى محطة التعبئة",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.11.2.1",
        category_code="HARVEST",
        subcategory="Harvest Hygiene",
        title_en="Harvester hygiene training",
        title_ar="تدريب على نظافة الحاصدين",
        description_en="Are harvest workers trained on personal hygiene requirements and food safety practices?",
        description_ar="هل تم تدريب عمال الحصاد على متطلبات النظافة الشخصية وممارسات سلامة الغذاء؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "INTERVIEW", "OBSERVATION"],
        guidance_en="Train on handwashing, illness reporting, clean clothing, no smoking/eating in fields, wound covering",
        guidance_ar="درب على غسل اليدين والإبلاغ عن المرض والملابس النظيفة وعدم التدخين/الأكل في الحقول وتغطية الجروح",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.11.3.1",
        category_code="HARVEST",
        subcategory="Harvest Equipment",
        title_en="Clean harvest equipment and containers",
        title_ar="معدات وحاويات الحصاد النظيفة",
        description_en="Are all harvest equipment and containers cleaned and maintained in sanitary condition?",
        description_ar="هل يتم تنظيف جميع معدات وحاويات الحصاد والاحتفاظ بها في حالة صحية؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["OBSERVATION"],
        guidance_en="Clean harvest bins, knives, tools before use; inspect for damage; sanitize where appropriate",
        guidance_ar="نظف صناديق الحصاد والسكاكين والأدوات قبل الاستخدام؛ افحص الأضرار؛ عقم حيثما كان ذلك مناسباً",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=3,
    ),
    ChecklistItem(
        id="AF.11.4.1",
        category_code="HARVEST",
        subcategory="Harvest Records",
        title_en="Harvest traceability records",
        title_ar="سجلات تتبع الحصاد",
        description_en="Are harvest records maintained linking product to field, date, and harvest team?",
        description_ar="هل يتم الاحتفاظ بسجلات الحصاد التي تربط المنتج بالحقل والتاريخ وفريق الحصاد؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT"],
        guidance_en="Record for each harvest: field/plot ID, crop/variety, harvest date, quantity, team/operator",
        guidance_ar="سجل لكل حصاد: معرف الحقل/القطعة، المحصول/الصنف، تاريخ الحصاد، الكمية، الفريق/المشغل",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=4,
    ),
]

# -----------------------------------------------------------------------------
# PRODUCE HANDLING AND POST-HARVEST
# معالجة المنتجات وما بعد الحصاد
# -----------------------------------------------------------------------------
PRODUCE_HANDLING_ITEMS = [
    ChecklistItem(
        id="AF.12.1.1",
        category_code="PRODUCE_HANDLING",
        subcategory="Packhouse Hygiene",
        title_en="Packhouse cleaning and sanitation",
        title_ar="تنظيف وتعقيم محطة التعبئة",
        description_en="Is the packhouse cleaned and sanitized according to a documented schedule?",
        description_ar="هل يتم تنظيف وتعقيم محطة التعبئة وفقاً لجدول موثق؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Maintain cleaning schedule, procedures, responsible persons; verify effectiveness; record completion",
        guidance_ar="احتفظ بجدول التنظيف والإجراءات والأشخاص المسؤولين؛ تحقق من الفعالية؛ سجل الإنجاز",
        applicable_to=["FV"],
        not_applicable_allowed=True,
        order=1,
    ),
    ChecklistItem(
        id="AF.12.2.1",
        category_code="PRODUCE_HANDLING",
        subcategory="Water Quality",
        title_en="Post-harvest water quality",
        title_ar="جودة المياه بعد الحصاد",
        description_en="Is water used for washing, cooling, or ice making tested regularly and meets microbiological standards?",
        description_ar="هل يتم اختبار المياه المستخدمة للغسيل أو التبريد أو صنع الثلج بانتظام وتلبي المعايير الميكروبيولوجية؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["TEST_RESULT", "DOCUMENT"],
        guidance_en="Test for E. coli, total coliforms; sanitize wash water; change water regularly; monitor sanitizer levels",
        guidance_ar="اختبر الإيكولاي والقولونيات الكلية؛ عقم مياه الغسيل؛ غيّر الماء بانتظام؛ راقب مستويات المعقم",
        applicable_to=["FV"],
        not_applicable_allowed=True,
        order=2,
    ),
    ChecklistItem(
        id="AF.12.3.1",
        category_code="PRODUCE_HANDLING",
        subcategory="Temperature Control",
        title_en="Cold chain temperature monitoring",
        title_ar="مراقبة درجة حرارة سلسلة التبريد",
        description_en="Are temperature controls in place and monitored for pre-cooling, cold storage, and transport?",
        description_ar="هل توجد ضوابط درجة الحرارة ويتم مراقبتها للتبريد المسبق والتخزين البارد والنقل؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Monitor and record temperatures; set alarms; take corrective action if out of range",
        guidance_ar="راقب وسجل درجات الحرارة؛ اضبط التنبيهات؛ اتخذ إجراءات تصحيحية إذا كانت خارج النطاق",
        applicable_to=["FV"],
        not_applicable_allowed=True,
        order=3,
    ),
    ChecklistItem(
        id="AF.12.4.1",
        category_code="PRODUCE_HANDLING",
        subcategory="Packaging",
        title_en="Food-grade packaging materials",
        title_ar="مواد التعبئة من الدرجة الغذائية",
        description_en="Are all packaging materials in contact with produce food-grade and stored to prevent contamination?",
        description_ar="هل جميع مواد التعبئة الملامسة للمنتجات من الدرجة الغذائية ومخزنة لمنع التلوث؟",
        compliance_level=ComplianceLevel.MAJOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Obtain supplier declarations; store packaging off floor, protected from pests, away from chemicals",
        guidance_ar="احصل على إقرارات الموردين؛ خزن التعبئة عن الأرض، محمية من الآفات، بعيداً عن المواد الكيميائية",
        applicable_to=["FV"],
        not_applicable_allowed=True,
        order=4,
    ),
]

# -----------------------------------------------------------------------------
# ENVIRONMENTAL MANAGEMENT
# الإدارة البيئية
# -----------------------------------------------------------------------------
ENVIRONMENT_ITEMS = [
    ChecklistItem(
        id="AF.13.1.1",
        category_code="ENVIRONMENT",
        subcategory="Waste Management",
        title_en="Waste management plan",
        title_ar="خطة إدارة النفايات",
        description_en="Is there a documented waste management plan covering collection, segregation, and disposal?",
        description_ar="هل توجد خطة موثقة لإدارة النفايات تغطي الجمع والفصل والتخلص؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Separate organic, recyclable, hazardous waste; use authorized disposal methods; prevent environmental pollution",
        guidance_ar="افصل النفايات العضوية والقابلة لإعادة التدوير والخطرة؛ استخدم طرق التخلص المصرح بها؛ امنع التلوث البيئي",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=1,
    ),
    ChecklistItem(
        id="AF.13.2.1",
        category_code="ENVIRONMENT",
        subcategory="Energy Conservation",
        title_en="Energy efficiency measures",
        title_ar="تدابير كفاءة الطاقة",
        description_en="Are energy conservation practices implemented to reduce consumption where feasible?",
        description_ar="هل يتم تنفيذ ممارسات حفظ الطاقة للحد من الاستهلاك حيثما كان ذلك ممكناً؟",
        compliance_level=ComplianceLevel.RECOMMENDATION,
        evidence_required=["OBSERVATION", "DOCUMENT"],
        guidance_en="Use efficient lighting, equipment maintenance, renewable energy, insulation, or energy monitoring",
        guidance_ar="استخدم الإضاءة الفعالة وصيانة المعدات والطاقة المتجددة والعزل أو مراقبة الطاقة",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=2,
    ),
    ChecklistItem(
        id="AF.13.3.1",
        category_code="ENVIRONMENT",
        subcategory="Biodiversity",
        title_en="Biodiversity conservation areas",
        title_ar="مناطق حفظ التنوع البيولوجي",
        description_en="Are areas of ecological importance (wetlands, natural habitats) identified and protected from agricultural impact?",
        description_ar="هل يتم تحديد المناطق ذات الأهمية البيئية (الأراضي الرطبة، الموائل الطبيعية) وحمايتها من التأثير الزراعي؟",
        compliance_level=ComplianceLevel.RECOMMENDATION,
        evidence_required=["DOCUMENT", "OBSERVATION"],
        guidance_en="Map sensitive areas; implement buffer zones; avoid pesticide drift; preserve natural vegetation",
        guidance_ar="ارسم خريطة للمناطق الحساسة؛ نفذ مناطق عازلة؛ تجنب انجراف المبيدات؛ احفظ النباتات الطبيعية",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=True,
        order=3,
    ),
    ChecklistItem(
        id="AF.13.4.1",
        category_code="ENVIRONMENT",
        subcategory="Pollution Prevention",
        title_en="Prevention of environmental pollution",
        title_ar="منع التلوث البيئي",
        description_en="Are measures in place to prevent soil, water, and air pollution from farm activities?",
        description_ar="هل توجد تدابير لمنع تلوث التربة والمياه والهواء من أنشطة المزرعة؟",
        compliance_level=ComplianceLevel.MINOR_MUST,
        evidence_required=["OBSERVATION", "DOCUMENT"],
        guidance_en="Prevent chemical spills, manage runoff, proper waste disposal, control emissions, secondary containment",
        guidance_ar="امنع انسكاب المواد الكيميائية، أدر الجريان السطحي، تخلص صحيح من النفايات، تحكم في الانبعاثات، احتواء ثانوي",
        applicable_to=["FV", "CROPS_BASE"],
        not_applicable_allowed=False,
        order=4,
    ),
]

# =============================================================================
# CHECKLIST CATEGORY DEFINITIONS
# تعريفات فئات قائمة التحقق
# =============================================================================

CHECKLIST_CATEGORIES_DETAIL = [
    ChecklistCategory(
        code="SITE_HISTORY",
        name_en="Site History and Management",
        name_ar="تاريخ الموقع والإدارة",
        description_en="Site history risk assessment and farm management planning",
        description_ar="تقييم مخاطر تاريخ الموقع وتخطيط إدارة المزرعة",
        items=SITE_HISTORY_ITEMS,
        order=1,
    ),
    ChecklistCategory(
        code="RECORD_KEEPING",
        name_en="Record Keeping and Documentation",
        name_ar="حفظ السجلات والتوثيق",
        description_en="Documentation requirements, internal audits, and complaints handling",
        description_ar="متطلبات التوثيق والتدقيق الداخلي ومعالجة الشكاوى",
        items=RECORD_KEEPING_ITEMS,
        order=2,
    ),
    ChecklistCategory(
        code="WORKERS_HEALTH",
        name_en="Workers Health, Safety and Welfare",
        name_ar="صحة وسلامة ورفاهية العمال",
        description_en="Occupational health and safety, training, welfare facilities (GRASP compliance)",
        description_ar="الصحة والسلامة المهنية، التدريب، مرافق الرفاهية (امتثال GRASP)",
        items=WORKERS_HEALTH_ITEMS,
        order=3,
    ),
    ChecklistCategory(
        code="TRACEABILITY",
        name_en="Product Traceability and Segregation",
        name_ar="تتبع المنتجات والفصل",
        description_en="Traceability systems, mass balance, and product segregation",
        description_ar="أنظمة التتبع، التوازن الكتلي، وفصل المنتجات",
        items=TRACEABILITY_ITEMS,
        order=4,
    ),
    ChecklistCategory(
        code="PLANT_PROPAGATION",
        name_en="Plant Propagation Material",
        name_ar="مواد التكاثر النباتي",
        description_en="Seeds and planting material sourcing and documentation",
        description_ar="مصادر البذور ومواد الزراعة والتوثيق",
        items=PLANT_PROPAGATION_ITEMS,
        order=5,
    ),
    ChecklistCategory(
        code="SOIL_MANAGEMENT",
        name_en="Soil and Substrate Management",
        name_ar="إدارة التربة والركيزة",
        description_en="Soil conservation, fertility analysis, and substrate quality",
        description_ar="حفظ التربة، تحليل الخصوبة، وجودة الركيزة",
        items=SOIL_MANAGEMENT_ITEMS,
        order=6,
    ),
    ChecklistCategory(
        code="FERTILIZER",
        name_en="Fertilizer Application",
        name_ar="تطبيق الأسمدة",
        description_en="Fertilizer records, organic fertilizer management, and storage",
        description_ar="سجلات الأسمدة، إدارة الأسمدة العضوية، والتخزين",
        items=FERTILIZER_ITEMS,
        order=7,
    ),
    ChecklistCategory(
        code="IRRIGATION",
        name_en="Irrigation and Water Management",
        name_ar="الري وإدارة المياه",
        description_en="Water source assessment, quality testing, and conservation (SPRING module)",
        description_ar="تقييم مصدر المياه، اختبار الجودة، والحفظ (وحدة SPRING)",
        items=IRRIGATION_ITEMS,
        order=8,
    ),
    ChecklistCategory(
        code="IPM",
        name_en="Integrated Pest Management",
        name_ar="الإدارة المتكاملة للآفات",
        description_en="IPM strategy, pest monitoring, and non-chemical control methods",
        description_ar="استراتيجية الإدارة المتكاملة للآفات، مراقبة الآفات، وطرق المكافحة غير الكيميائية",
        items=IPM_ITEMS,
        order=9,
    ),
    ChecklistCategory(
        code="PLANT_PROTECTION",
        name_en="Plant Protection Products",
        name_ar="منتجات وقاية النباتات",
        description_en="PPP authorization, records, storage, application, and safety",
        description_ar="ترخيص منتجات وقاية النباتات، السجلات، التخزين، التطبيق، والسلامة",
        items=PLANT_PROTECTION_ITEMS,
        order=10,
    ),
    ChecklistCategory(
        code="HARVEST",
        name_en="Harvesting Procedures",
        name_ar="إجراءات الحصاد",
        description_en="Harvest procedures, hygiene, equipment, and traceability",
        description_ar="إجراءات الحصاد، النظافة، المعدات، والتتبع",
        items=HARVEST_ITEMS,
        order=11,
    ),
    ChecklistCategory(
        code="PRODUCE_HANDLING",
        name_en="Produce Handling and Post-Harvest",
        name_ar="معالجة المنتجات وما بعد الحصاد",
        description_en="Packhouse operations, water quality, temperature control, and packaging",
        description_ar="عمليات محطة التعبئة، جودة المياه، التحكم في درجة الحرارة، والتعبئة",
        items=PRODUCE_HANDLING_ITEMS,
        order=12,
    ),
    ChecklistCategory(
        code="ENVIRONMENT",
        name_en="Environmental Management",
        name_ar="الإدارة البيئية",
        description_en="Waste management, energy conservation, biodiversity, and pollution prevention",
        description_ar="إدارة النفايات، حفظ الطاقة، التنوع البيولوجي، ومنع التلوث",
        items=ENVIRONMENT_ITEMS,
        order=13,
    ),
]

# =============================================================================
# COMPLETE CHECKLIST
# قائمة التحقق الكاملة
# =============================================================================

IFA_V6_CHECKLIST: dict[str, ChecklistCategory] = {
    category.code: category for category in CHECKLIST_CATEGORIES_DETAIL
}

# =============================================================================
# HELPER FUNCTIONS
# الدوال المساعدة
# =============================================================================


def get_category(category_code: str) -> ChecklistCategory | None:
    """
    Get a checklist category by code
    احصل على فئة قائمة التحقق بالرمز

    Args:
        category_code: Category code (e.g., "SITE_HISTORY")

    Returns:
        ChecklistCategory or None if not found
    """
    return IFA_V6_CHECKLIST.get(category_code)


def get_checklist_item(item_id: str) -> ChecklistItem | None:
    """
    Get a specific checklist item by ID
    احصل على عنصر قائمة تحقق محدد بالمعرف

    Args:
        item_id: Control point ID (e.g., "AF.1.1.1")

    Returns:
        ChecklistItem or None if not found
    """
    for category in IFA_V6_CHECKLIST.values():
        item = category.get_item_by_id(item_id)
        if item:
            return item
    return None


def get_items_by_compliance_level(
    compliance_level: ComplianceLevel, category_code: str | None = None
) -> list[ChecklistItem]:
    """
    Get all checklist items by compliance level
    احصل على جميع عناصر قائمة التحقق حسب مستوى الامتثال

    Args:
        compliance_level: Compliance level to filter by
        category_code: Optional category code to filter by

    Returns:
        List of ChecklistItem objects
    """
    items = []

    categories_to_search = (
        [IFA_V6_CHECKLIST[category_code]]
        if category_code
        else IFA_V6_CHECKLIST.values()
    )

    for category in categories_to_search:
        for item in category.items:
            if item.compliance_level == compliance_level:
                items.append(item)

    return items


def calculate_compliance_score(findings: list[dict[str, any]]) -> dict[str, any]:
    """
    Calculate compliance score from audit findings
    احسب درجة الامتثال من نتائج التدقيق

    Args:
        findings: List of audit findings with structure:
            {
                "checklist_item_id": str,
                "is_compliant": bool,
                "is_not_applicable": bool
            }

    Returns:
        Dictionary with compliance statistics and pass/fail status
    """
    from .constants import COMPLIANCE_THRESHOLDS

    # Initialize counters
    stats = {
        ComplianceLevel.MAJOR_MUST: {"total": 0, "compliant": 0, "na": 0},
        ComplianceLevel.MINOR_MUST: {"total": 0, "compliant": 0, "na": 0},
        ComplianceLevel.RECOMMENDATION: {"total": 0, "compliant": 0, "na": 0},
    }

    # Count all items and findings
    for finding in findings:
        item = get_checklist_item(finding["checklist_item_id"])
        if not item:
            continue

        level = item.compliance_level
        stats[level]["total"] += 1

        if finding.get("is_not_applicable", False):
            stats[level]["na"] += 1
        elif finding.get("is_compliant", False):
            stats[level]["compliant"] += 1

    # Calculate percentages
    results = {}
    for level, counts in stats.items():
        applicable = counts["total"] - counts["na"]
        percentage = (
            (counts["compliant"] / applicable * 100) if applicable > 0 else 100.0
        )

        results[level.value] = {
            "total_items": counts["total"],
            "compliant": counts["compliant"],
            "not_applicable": counts["na"],
            "applicable": applicable,
            "compliance_percentage": round(percentage, 2),
            "threshold": COMPLIANCE_THRESHOLDS.get(
                level.value.lower().replace("_", "_"), 0
            ),
            "passes": (
                percentage
                >= COMPLIANCE_THRESHOLDS.get(level.value.lower().replace("_", "_"), 0)
                if level != ComplianceLevel.RECOMMENDATION
                else True
            ),
        }

    # Overall pass/fail
    overall_pass = (
        results[ComplianceLevel.MAJOR_MUST.value]["passes"]
        and results[ComplianceLevel.MINOR_MUST.value]["passes"]
    )

    return {
        "by_level": results,
        "overall_pass": overall_pass,
        "certification_recommendation": "APPROVE" if overall_pass else "REJECT",
        "total_items": sum(s["total"] for s in stats.values()),
        "total_compliant": sum(s["compliant"] for s in stats.values()),
    }


def get_all_items() -> list[ChecklistItem]:
    """
    Get all checklist items across all categories
    احصل على جميع عناصر قائمة التحقق عبر جميع الفئات

    Returns:
        List of all ChecklistItem objects
    """
    items = []
    for category in sorted(IFA_V6_CHECKLIST.values(), key=lambda c: c.order):
        items.extend(sorted(category.items, key=lambda i: i.order))
    return items


def get_statistics() -> dict[str, any]:
    """
    Get statistics about the checklist
    احصل على إحصائيات حول قائمة التحقق

    Returns:
        Dictionary with checklist statistics
    """
    all_items = get_all_items()

    return {
        "total_categories": len(IFA_V6_CHECKLIST),
        "total_items": len(all_items),
        "by_compliance_level": {
            ComplianceLevel.MAJOR_MUST.value: len(
                get_items_by_compliance_level(ComplianceLevel.MAJOR_MUST)
            ),
            ComplianceLevel.MINOR_MUST.value: len(
                get_items_by_compliance_level(ComplianceLevel.MINOR_MUST)
            ),
            ComplianceLevel.RECOMMENDATION.value: len(
                get_items_by_compliance_level(ComplianceLevel.RECOMMENDATION)
            ),
        },
        "categories": [
            {
                "code": cat.code,
                "name_en": cat.name_en,
                "name_ar": cat.name_ar,
                "item_count": len(cat.items),
            }
            for cat in sorted(IFA_V6_CHECKLIST.values(), key=lambda c: c.order)
        ],
    }
