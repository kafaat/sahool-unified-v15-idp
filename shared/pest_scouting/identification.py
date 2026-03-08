"""
Pest Identification Database and Helpers - قاعدة بيانات تعريف الآفات
====================================================================

Comprehensive pest identification database for Middle East agricultural pests,
with bilingual support (Arabic/English) and local pest names.

Includes:
- Red Palm Weevil (سوسة النخيل الحمراء)
- Dubas Bug (دوباس النخيل)
- Aphids (المن)
- Whiteflies (الذبابة البيضاء)
- Spider Mites (العنكبوت الأحمر)
- Locusts (الجراد)
- Date Moth (فراشة التمر)
- Tomato Leafminer (Tuta absoluta)
- And more regional pests

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

from typing import Any

from .models import (
    CropType,
    InfestationLevel,
    PestCategory,
    PestIdentification,
    PestLifeStage,
    ScoutObservation,
)

# =============================================================================
# PEST DATABASE - قاعدة بيانات الآفات
# =============================================================================

PEST_DATABASE: dict[str, PestIdentification] = {
    # -------------------------------------------------------------------------
    # RED PALM WEEVIL - سوسة النخيل الحمراء
    # -------------------------------------------------------------------------
    "RPW001": PestIdentification(
        id="RPW001",
        scientific_name="Rhynchophorus ferrugineus",
        common_name="Red Palm Weevil",
        common_name_ar="سوسة النخيل الحمراء",
        local_names=["سوسة النخل", "ثاقبة النخيل", "الدودة الحمراء"],
        category=PestCategory.INSECT,
        family="Curculionidae",
        order="Coleoptera",
        description="The Red Palm Weevil is the most destructive pest of palm trees worldwide. "
        "Adults are large reddish-brown weevils that bore into palm trunks where larvae "
        "feed on internal tissues, often killing the tree.",
        description_ar="سوسة النخيل الحمراء هي أخطر آفة تصيب أشجار النخيل في العالم. "
        "الحشرات الكاملة كبيرة الحجم بنية محمرة تثقب جذوع النخيل حيث تتغذى "
        "اليرقات على الأنسجة الداخلية، مما يؤدي غالباً إلى موت الشجرة.",
        adult_description="Large weevil (35-40mm), reddish-brown to black with dark spots on thorax. "
        "Long curved snout (rostrum).",
        adult_description_ar="خنفساء كبيرة (35-40 مم)، بنية محمرة إلى سوداء مع بقع داكنة على الصدر. خرطوم طويل منحني.",
        larva_description="Cream-colored, legless grub up to 50mm long with brown head capsule.",
        larva_description_ar="يرقة بيضاء كريمية بدون أرجل يصل طولها إلى 50 مم برأس بني.",
        egg_description="Creamy white, elongated oval, 2-3mm long, laid in wounds in palm tissue.",
        egg_description_ar="بيضة بيضاء كريمية، بيضاوية مستطيلة، 2-3 مم، توضع في جروح أنسجة النخيل.",
        damage_symptoms=[
            "Brown oozing from trunk wounds",
            "Fermented odor from infested palms",
            "Yellowing and wilting of crown leaves",
            "Presence of cocoons in leaf bases",
            "Chewing sounds from inside trunk",
            "Crown collapse in severe cases",
        ],
        damage_symptoms_ar=[
            "سائل بني يخرج من جروح الجذع",
            "رائحة تخمر من النخيل المصاب",
            "اصفرار وذبول أوراق التاج",
            "وجود شرانق في قواعد الأوراق",
            "أصوات قضم من داخل الجذع",
            "انهيار التاج في الحالات الشديدة",
        ],
        adult_size_mm=(35.0, 42.0),
        adult_color="Reddish-brown to ferruginous",
        adult_color_ar="بني محمر إلى صدئي",
        distinguishing_features=[
            "Dark spots on pronotum",
            "Long curved snout",
            "Reddish-brown coloration",
            "Strong flyers (can fly several km)",
        ],
        distinguishing_features_ar=[
            "بقع داكنة على الصدر الأمامي",
            "خرطوم طويل منحني",
            "لون بني محمر",
            "طيران قوي (يمكن أن تطير عدة كم)",
        ],
        primary_hosts=[CropType.DATE_PALM],
        secondary_hosts=[],
        life_cycle_days=(60, 120),
        generations_per_year=3,
        overwintering_stage=PestLifeStage.LARVA,
        optimal_temperature_c=(25.0, 35.0),
        optimal_humidity_pct=(60.0, 80.0),
        is_quarantine_pest=True,
        economic_importance="very_high",
        economic_importance_ar="عالية جداً",
        potential_yield_loss_pct=(80.0, 100.0),
        distribution_regions=["Middle East", "North Africa", "Southeast Asia", "Southern Europe"],
        first_reported_saudi="1987",
        detection_difficulty="difficult",
        detection_notes="Often detected only when damage is severe. Acoustic detection and pheromone traps recommended.",
        detection_notes_ar="غالباً لا يُكتشف إلا عندما يكون الضرر شديداً. يُوصى بالكشف الصوتي والمصائد الفرمونية.",
    ),
    # -------------------------------------------------------------------------
    # DUBAS BUG - دوباس النخيل
    # -------------------------------------------------------------------------
    "DUBAS001": PestIdentification(
        id="DUBAS001",
        scientific_name="Ommatissus lybicus",
        common_name="Dubas Bug / Old World Date Bug",
        common_name_ar="دوباس النخيل",
        local_names=["الدوباس", "حشرة النخيل القافزة", "متق النخيل"],
        category=PestCategory.INSECT,
        family="Tropiduchidae",
        order="Hemiptera",
        description="The Dubas bug is a major pest of date palms in the Middle East. "
        "Both nymphs and adults suck sap from leaves, producing honeydew "
        "that leads to sooty mold growth.",
        description_ar="دوباس النخيل هو آفة رئيسية لأشجار النخيل في الشرق الأوسط. "
        "تمتص الحوريات والحشرات الكاملة العصارة من الأوراق وتفرز الندوة العسلية "
        "التي تؤدي إلى نمو العفن الهبابي.",
        adult_description="Small (5-6mm), greenish-yellow to brownish insect with transparent wings. Good jumpers.",
        adult_description_ar="حشرة صغيرة (5-6 مم)، خضراء مصفرة إلى بنية بأجنحة شفافة. قافزة جيدة.",
        larva_description="N/A - Hemimetabolous (nymphs, not larvae)",
        larva_description_ar="لا ينطبق - تطور ناقص (حوريات وليس يرقات)",
        egg_description="Elongated, inserted into leaf tissue, covered with waxy secretion.",
        egg_description_ar="مستطيلة، تُدخل في أنسجة الورقة، مغطاة بإفراز شمعي.",
        damage_symptoms=[
            "Sticky honeydew on leaves and fruit",
            "Black sooty mold on fronds",
            "Yellowing of leaflets",
            "Reduced fruit quality and yield",
            "Leaf scorching in severe infestations",
        ],
        damage_symptoms_ar=[
            "ندوة عسلية لزجة على الأوراق والثمار",
            "عفن هبابي أسود على السعف",
            "اصفرار الوريقات",
            "انخفاض جودة وإنتاج الثمار",
            "احتراق الأوراق في الإصابات الشديدة",
        ],
        adult_size_mm=(5.0, 6.0),
        adult_color="Greenish-yellow to brownish",
        adult_color_ar="أخضر مصفر إلى بني",
        distinguishing_features=[
            "Jumping behavior",
            "Transparent wings held roof-like",
            "Produces white waxy secretion",
        ],
        distinguishing_features_ar=[
            "سلوك القفز",
            "أجنحة شفافة تُحمل بشكل سقفي",
            "تفرز مادة شمعية بيضاء",
        ],
        primary_hosts=[CropType.DATE_PALM],
        secondary_hosts=[],
        life_cycle_days=(45, 60),
        generations_per_year=2,
        overwintering_stage=PestLifeStage.EGG,
        optimal_temperature_c=(25.0, 35.0),
        optimal_humidity_pct=(40.0, 60.0),
        is_quarantine_pest=False,
        economic_importance="high",
        economic_importance_ar="عالية",
        potential_yield_loss_pct=(20.0, 50.0),
        distribution_regions=["Middle East", "North Africa", "Pakistan", "India"],
        first_reported_saudi="Native",
        detection_difficulty="easy",
        detection_notes="Adults and nymphs visible on undersides of leaves. Honeydew and sooty mold easily observed.",
        detection_notes_ar="الحشرات الكاملة والحوريات مرئية على السطح السفلي للأوراق. الندوة العسلية والعفن الهبابي يُلاحظان بسهولة.",
    ),
    # -------------------------------------------------------------------------
    # APHIDS - المن
    # -------------------------------------------------------------------------
    "APHID001": PestIdentification(
        id="APHID001",
        scientific_name="Aphis gossypii",
        common_name="Cotton/Melon Aphid",
        common_name_ar="من القطن/الخضروات",
        local_names=["المن", "قملة النبات", "الندوة"],
        category=PestCategory.INSECT,
        family="Aphididae",
        order="Hemiptera",
        description="Small soft-bodied insects that suck plant sap. Major pest of vegetables "
        "and many crops. Transmits plant viruses and produces honeydew.",
        description_ar="حشرات صغيرة رخوة الجسم تمتص عصارة النبات. آفة رئيسية للخضروات "
        "والعديد من المحاصيل. تنقل الفيروسات النباتية وتفرز الندوة العسلية.",
        adult_description="Small (1-2mm), pear-shaped, variable color (green, yellow, or black). "
        "May be winged or wingless.",
        adult_description_ar="صغيرة (1-2 مم)، كمثرية الشكل، متغيرة اللون (أخضر أو أصفر أو أسود). "
        "قد تكون مجنحة أو غير مجنحة.",
        larva_description="N/A - Nymphs similar to adults but smaller.",
        larva_description_ar="لا ينطبق - الحوريات مشابهة للحشرات الكاملة لكن أصغر.",
        egg_description="Rarely seen in warm climates where reproduction is mostly parthenogenetic.",
        egg_description_ar="نادراً ما يُشاهد في المناخات الدافئة حيث التكاثر عذري غالباً.",
        damage_symptoms=[
            "Curling and distortion of leaves",
            "Stunted plant growth",
            "Honeydew and sooty mold",
            "Virus transmission symptoms",
            "Yellowing of leaves",
            "Colony clusters on growing tips",
        ],
        damage_symptoms_ar=[
            "تجعد وتشوه الأوراق",
            "تقزم نمو النبات",
            "ندوة عسلية وعفن هبابي",
            "أعراض نقل الفيروسات",
            "اصفرار الأوراق",
            "تجمعات مستعمرات على القمم النامية",
        ],
        adult_size_mm=(1.0, 2.5),
        adult_color="Variable: green, yellow, or black",
        adult_color_ar="متغير: أخضر أو أصفر أو أسود",
        distinguishing_features=[
            "Cornicles (siphunculi) on abdomen",
            "Soft pear-shaped body",
            "Colonial behavior",
            "Rapid reproduction",
        ],
        distinguishing_features_ar=[
            "قرنيات (أنابيب) على البطن",
            "جسم رخو كمثري",
            "سلوك مستعمراتي",
            "تكاثر سريع",
        ],
        primary_hosts=[CropType.TOMATO, CropType.CUCUMBER, CropType.PEPPER],
        secondary_hosts=[CropType.WATERMELON, CropType.CITRUS, CropType.ALFALFA],
        life_cycle_days=(7, 14),
        generations_per_year=20,
        overwintering_stage=PestLifeStage.ADULT,
        optimal_temperature_c=(20.0, 28.0),
        optimal_humidity_pct=(50.0, 70.0),
        is_quarantine_pest=False,
        economic_importance="high",
        economic_importance_ar="عالية",
        potential_yield_loss_pct=(10.0, 40.0),
        distribution_regions=["Worldwide"],
        first_reported_saudi="Native",
        detection_difficulty="easy",
        detection_notes="Check undersides of leaves and growing tips. Colonies readily visible.",
        detection_notes_ar="افحص السطح السفلي للأوراق والقمم النامية. المستعمرات مرئية بسهولة.",
    ),
    # -------------------------------------------------------------------------
    # GREEN PEACH APHID - من الخوخ الأخضر
    # -------------------------------------------------------------------------
    "APHID002": PestIdentification(
        id="APHID002",
        scientific_name="Myzus persicae",
        common_name="Green Peach Aphid",
        common_name_ar="من الخوخ الأخضر",
        local_names=["من الخوخ", "المن الأخضر"],
        category=PestCategory.INSECT,
        family="Aphididae",
        order="Hemiptera",
        description="Highly polyphagous aphid and important virus vector. Attacks many vegetable "
        "and fruit crops. Known for rapid development of insecticide resistance.",
        description_ar="من متعدد العوائل ومهم في نقل الفيروسات. يهاجم العديد من محاصيل الخضروات "
        "والفاكهة. معروف بتطوير مقاومة سريعة للمبيدات.",
        adult_description="Small (1.5-2.5mm), pale green to yellowish-green, spindle-shaped body.",
        adult_description_ar="صغير (1.5-2.5 مم)، أخضر باهت إلى أصفر مخضر، جسم مغزلي الشكل.",
        larva_description="Nymphs similar to adults, pale green.",
        larva_description_ar="الحوريات مشابهة للحشرات الكاملة، خضراء باهتة.",
        egg_description="Black, oval, deposited on twigs of Prunus hosts for overwintering.",
        egg_description_ar="سوداء، بيضاوية، توضع على أغصان عوائل البرقوق للتشتية.",
        damage_symptoms=[
            "Leaf curling and puckering",
            "Stunted growth",
            "Virus disease transmission (many viruses)",
            "Honeydew and sooty mold",
        ],
        damage_symptoms_ar=[
            "تجعد وتكرمش الأوراق",
            "تقزم النمو",
            "نقل أمراض فيروسية (فيروسات متعددة)",
            "ندوة عسلية وعفن هبابي",
        ],
        adult_size_mm=(1.5, 2.5),
        adult_color="Pale green to yellowish-green",
        adult_color_ar="أخضر باهت إلى أصفر مخضر",
        distinguishing_features=[
            "Converging antennal tubercles",
            "Long slender cornicles",
            "No dorsal abdominal tubercles",
        ],
        distinguishing_features_ar=[
            "حدبات قرنية متقاربة",
            "قرنيات طويلة نحيلة",
            "لا توجد حدبات ظهرية بطنية",
        ],
        primary_hosts=[CropType.TOMATO, CropType.PEPPER, CropType.POTATO],
        secondary_hosts=[CropType.CUCUMBER, CropType.CITRUS],
        life_cycle_days=(10, 14),
        generations_per_year=15,
        overwintering_stage=PestLifeStage.EGG,
        optimal_temperature_c=(18.0, 25.0),
        optimal_humidity_pct=(50.0, 70.0),
        is_quarantine_pest=False,
        economic_importance="very_high",
        economic_importance_ar="عالية جداً",
        potential_yield_loss_pct=(15.0, 60.0),
        distribution_regions=["Worldwide"],
        first_reported_saudi="Native",
        detection_difficulty="easy",
        detection_notes="Important virus vector. Monitor regularly in vegetable crops.",
        detection_notes_ar="ناقل فيروسات مهم. راقب بانتظام في محاصيل الخضروات.",
    ),
    # -------------------------------------------------------------------------
    # WHITEFLIES - الذبابة البيضاء
    # -------------------------------------------------------------------------
    "WHITEFLY001": PestIdentification(
        id="WHITEFLY001",
        scientific_name="Bemisia tabaci",
        common_name="Silverleaf Whitefly / Tobacco Whitefly",
        common_name_ar="الذبابة البيضاء",
        local_names=["الذبابة البيضاء", "ذبابة التبغ البيضاء", "بيميسيا"],
        category=PestCategory.INSECT,
        family="Aleyrodidae",
        order="Hemiptera",
        description="Major pest of greenhouse and field vegetables. Causes direct feeding damage, "
        "honeydew production, and transmits devastating geminiviruses like TYLCV.",
        description_ar="آفة رئيسية للخضروات في البيوت المحمية والحقول المكشوفة. تسبب ضرراً مباشراً "
        "بالتغذية وإنتاج الندوة العسلية وتنقل فيروسات مدمرة مثل فيروس تجعد واصفرار أوراق الطماطم.",
        adult_description="Tiny (1-1.5mm), white moth-like insect with waxy white wings held roof-like.",
        adult_description_ar="حشرة صغيرة جداً (1-1.5 مم)، شبيهة بالعثة بيضاء بأجنحة شمعية بيضاء تُحمل بشكل سقفي.",
        larva_description="Nymphs are flat, oval, scale-like, yellowish, attached to leaf undersides.",
        larva_description_ar="الحوريات مسطحة، بيضاوية، شبيهة بالحراشف، صفراء، ملتصقة بالسطح السفلي للأوراق.",
        egg_description="Tiny (0.2mm), pear-shaped, pale yellow, laid on leaf undersides.",
        egg_description_ar="صغيرة جداً (0.2 مم)، كمثرية الشكل، صفراء باهتة، توضع على السطح السفلي للأوراق.",
        damage_symptoms=[
            "Yellowing and leaf drop",
            "Silvering of leaves (in tomato)",
            "Sticky honeydew and sooty mold",
            "Irregular fruit ripening",
            "Virus symptoms (leaf curling, stunting)",
            "White adults flying when plant disturbed",
        ],
        damage_symptoms_ar=[
            "اصفرار وسقوط الأوراق",
            "تفضض الأوراق (في الطماطم)",
            "ندوة عسلية لزجة وعفن هبابي",
            "نضج غير منتظم للثمار",
            "أعراض فيروسية (تجعد الأوراق، تقزم)",
            "حشرات كاملة بيضاء تطير عند تحريك النبات",
        ],
        adult_size_mm=(1.0, 1.5),
        adult_color="White with yellowish body",
        adult_color_ar="أبيض بجسم مصفر",
        distinguishing_features=[
            "White waxy wings",
            "Holds wings roof-like at rest",
            "Flies when plant disturbed",
            "Scale-like nymphs on leaf undersides",
        ],
        distinguishing_features_ar=[
            "أجنحة شمعية بيضاء",
            "تحمل الأجنحة بشكل سقفي عند الراحة",
            "تطير عند تحريك النبات",
            "حوريات شبيهة بالحراشف على السطح السفلي للأوراق",
        ],
        primary_hosts=[CropType.TOMATO, CropType.CUCUMBER, CropType.PEPPER, CropType.EGGPLANT],
        secondary_hosts=[CropType.WATERMELON, CropType.POTATO],
        life_cycle_days=(18, 28),
        generations_per_year=12,
        overwintering_stage=PestLifeStage.ALL_STAGES,
        optimal_temperature_c=(25.0, 32.0),
        optimal_humidity_pct=(50.0, 70.0),
        is_quarantine_pest=False,
        economic_importance="very_high",
        economic_importance_ar="عالية جداً",
        potential_yield_loss_pct=(30.0, 100.0),
        distribution_regions=["Worldwide in tropical and subtropical regions"],
        first_reported_saudi="1980s",
        detection_difficulty="easy",
        detection_notes="Use yellow sticky traps for monitoring. Check leaf undersides for nymphs.",
        detection_notes_ar="استخدم المصائد اللاصقة الصفراء للمراقبة. افحص السطح السفلي للأوراق للحوريات.",
    ),
    # -------------------------------------------------------------------------
    # SPIDER MITES - العنكبوت الأحمر
    # -------------------------------------------------------------------------
    "MITE001": PestIdentification(
        id="MITE001",
        scientific_name="Tetranychus urticae",
        common_name="Two-spotted Spider Mite",
        common_name_ar="العنكبوت الأحمر ذو البقعتين",
        local_names=["العنكبوت الأحمر", "الأكاروس", "الحلم"],
        category=PestCategory.MITE,
        family="Tetranychidae",
        order="Trombidiformes",
        description="Extremely polyphagous mite pest that thrives in hot, dry conditions. "
        "Causes stippling damage and produces webbing. Can build populations rapidly.",
        description_ar="آفة أكاروسية متعددة العوائل للغاية تزدهر في الظروف الحارة والجافة. "
        "تسبب ضرر التنقيط وتنتج الخيوط العنكبوتية. يمكن أن تبني أعدادها بسرعة.",
        adult_description="Very small (0.4-0.5mm), oval, greenish-yellow to red with two dark spots.",
        adult_description_ar="صغير جداً (0.4-0.5 مم)، بيضاوي، أخضر مصفر إلى أحمر بنقطتين داكنتين.",
        larva_description="Six-legged larvae, very small, pale.",
        larva_description_ar="يرقات بستة أرجل، صغيرة جداً، باهتة.",
        egg_description="Spherical, tiny (0.14mm), initially translucent becoming opaque.",
        egg_description_ar="كروية، صغيرة جداً (0.14 مم)، شفافة في البداية ثم تصبح معتمة.",
        damage_symptoms=[
            "Fine stippling on leaves (tiny yellow dots)",
            "Bronzing or silvering of leaves",
            "Webbing on undersides of leaves",
            "Leaf drop in severe infestations",
            "Stunted plant growth",
        ],
        damage_symptoms_ar=[
            "تنقيط دقيق على الأوراق (نقاط صفراء صغيرة)",
            "تبرنز أو تفضض الأوراق",
            "خيوط عنكبوتية على السطح السفلي للأوراق",
            "سقوط الأوراق في الإصابات الشديدة",
            "تقزم نمو النبات",
        ],
        adult_size_mm=(0.4, 0.5),
        adult_color="Greenish-yellow to orange-red",
        adult_color_ar="أخضر مصفر إلى برتقالي محمر",
        distinguishing_features=[
            "Two dark spots on body",
            "Produces webbing",
            "Eight legs (adults)",
            "Very small - needs magnification",
        ],
        distinguishing_features_ar=[
            "نقطتان داكنتان على الجسم",
            "تنتج خيوطاً عنكبوتية",
            "ثمانية أرجل (الحشرات الكاملة)",
            "صغير جداً - يحتاج تكبير",
        ],
        primary_hosts=[CropType.CUCUMBER, CropType.TOMATO, CropType.PEPPER],
        secondary_hosts=[CropType.WATERMELON, CropType.GRAPE, CropType.CITRUS],
        life_cycle_days=(8, 14),
        generations_per_year=20,
        overwintering_stage=PestLifeStage.ADULT,
        optimal_temperature_c=(28.0, 35.0),
        optimal_humidity_pct=(30.0, 50.0),
        is_quarantine_pest=False,
        economic_importance="high",
        economic_importance_ar="عالية",
        potential_yield_loss_pct=(20.0, 60.0),
        distribution_regions=["Worldwide"],
        first_reported_saudi="Native",
        detection_difficulty="moderate",
        detection_notes="Use hand lens to observe mites. Look for stippling and webbing. "
        "Populations explode in hot, dry weather.",
        detection_notes_ar="استخدم عدسة يدوية لملاحظة العناكب. ابحث عن التنقيط والخيوط. "
        "الأعداد تنفجر في الطقس الحار والجاف.",
    ),
    # -------------------------------------------------------------------------
    # TOMATO LEAFMINER (Tuta absoluta) - حافرة أنفاق الطماطم
    # -------------------------------------------------------------------------
    "TUTA001": PestIdentification(
        id="TUTA001",
        scientific_name="Tuta absoluta",
        common_name="Tomato Leafminer / South American Tomato Moth",
        common_name_ar="حافرة أنفاق الطماطم",
        local_names=["توتا أبسولوتا", "عثة الطماطم", "حافرة الطماطم"],
        category=PestCategory.INSECT,
        family="Gelechiidae",
        order="Lepidoptera",
        description="Highly destructive invasive pest of tomato. Larvae mine leaves, stems, "
        "and fruits. Can cause complete crop loss if uncontrolled.",
        description_ar="آفة غازية شديدة التدمير للطماطم. تحفر اليرقات أنفاقاً في الأوراق والسيقان "
        "والثمار. يمكن أن تسبب خسارة كاملة للمحصول إذا لم تُكافح.",
        adult_description="Small moth (5-7mm wingspan), grayish-brown with black spots on forewings.",
        adult_description_ar="عثة صغيرة (5-7 مم امتداد الجناحين)، رمادية بنية ببقع سوداء على الأجنحة الأمامية.",
        larva_description="Cream to greenish caterpillar with dark head, up to 8mm long.",
        larva_description_ar="يرقة كريمية إلى خضراء برأس داكن، يصل طولها إلى 8 مم.",
        egg_description="Tiny (0.35mm), cylindrical, cream to yellow, laid singly on leaves.",
        egg_description_ar="صغيرة جداً (0.35 مم)، أسطوانية، كريمية إلى صفراء، توضع منفردة على الأوراق.",
        damage_symptoms=[
            "Irregular mines in leaves",
            "Galleries in stems and petioles",
            "Entry holes in fruits",
            "Frass (excrement) visible in mines",
            "Wilting of attacked shoots",
            "Secondary rot in damaged fruits",
        ],
        damage_symptoms_ar=[
            "أنفاق غير منتظمة في الأوراق",
            "دهاليز في السيقان والأعناق",
            "ثقوب دخول في الثمار",
            "براز مرئي في الأنفاق",
            "ذبول الأفرع المصابة",
            "عفن ثانوي في الثمار المتضررة",
        ],
        adult_size_mm=(5.0, 7.0),
        adult_color="Grayish-brown",
        adult_color_ar="رمادي بني",
        distinguishing_features=[
            "Silvery-grey scales on wings",
            "Black spots on forewings",
            "Nocturnal adults",
            "Distinctive leaf mines",
        ],
        distinguishing_features_ar=[
            "حراشف فضية رمادية على الأجنحة",
            "بقع سوداء على الأجنحة الأمامية",
            "حشرات كاملة ليلية",
            "أنفاق أوراق مميزة",
        ],
        primary_hosts=[CropType.TOMATO],
        secondary_hosts=[CropType.POTATO, CropType.EGGPLANT, CropType.PEPPER],
        life_cycle_days=(25, 40),
        generations_per_year=12,
        overwintering_stage=PestLifeStage.PUPA,
        optimal_temperature_c=(20.0, 30.0),
        optimal_humidity_pct=(60.0, 80.0),
        is_quarantine_pest=True,
        economic_importance="very_high",
        economic_importance_ar="عالية جداً",
        potential_yield_loss_pct=(50.0, 100.0),
        distribution_regions=["South America", "Europe", "Middle East", "Africa", "Asia"],
        first_reported_saudi="2010",
        detection_difficulty="moderate",
        detection_notes="Use pheromone traps for adults. Look for leaf mines and fruit entry holes.",
        detection_notes_ar="استخدم المصائد الفرمونية للحشرات الكاملة. ابحث عن أنفاق الأوراق وثقوب دخول الثمار.",
    ),
    # -------------------------------------------------------------------------
    # DATE MOTH - فراشة التمر
    # -------------------------------------------------------------------------
    "DMOTH001": PestIdentification(
        id="DMOTH001",
        scientific_name="Ectomyelois ceratoniae",
        common_name="Carob Moth / Date Moth",
        common_name_ar="فراشة التمر / دودة التمر",
        local_names=["فراشة التمر", "دودة الثمار", "عثة الخروب"],
        category=PestCategory.INSECT,
        family="Pyralidae",
        order="Lepidoptera",
        description="Important pest of dates and other fruits in the Middle East. Larvae feed "
        "inside fruits, causing quality loss and facilitating secondary infections.",
        description_ar="آفة مهمة للتمور والفواكه الأخرى في الشرق الأوسط. تتغذى اليرقات داخل "
        "الثمار مسببة خسارة في الجودة وتسهل الإصابات الثانوية.",
        adult_description="Small moth (10-14mm wingspan), grey with darker markings on wings.",
        adult_description_ar="عثة صغيرة (10-14 مم امتداد الجناحين)، رمادية بعلامات داكنة على الأجنحة.",
        larva_description="Pinkish caterpillar with brown head, up to 15mm long.",
        larva_description_ar="يرقة وردية برأس بني، يصل طولها إلى 15 مم.",
        egg_description="Oval, white to cream, laid on or near fruit.",
        egg_description_ar="بيضاوية، بيضاء إلى كريمية، توضع على الثمرة أو قربها.",
        damage_symptoms=[
            "Entry holes in date fruits",
            "Webbing and frass inside fruits",
            "Premature fruit drop",
            "Fungal contamination of damaged fruits",
            "Reduced fruit quality and marketability",
        ],
        damage_symptoms_ar=[
            "ثقوب دخول في ثمار التمر",
            "خيوط وبراز داخل الثمار",
            "سقوط مبكر للثمار",
            "تلوث فطري للثمار المتضررة",
            "انخفاض جودة وتسويق الثمار",
        ],
        adult_size_mm=(10.0, 14.0),
        adult_color="Grey with darker wing markings",
        adult_color_ar="رمادي بعلامات جناحية داكنة",
        distinguishing_features=[
            "Grey coloration",
            "Nocturnal flight",
            "Larvae bore into fruits",
        ],
        distinguishing_features_ar=[
            "لون رمادي",
            "طيران ليلي",
            "اليرقات تثقب الثمار",
        ],
        primary_hosts=[CropType.DATE_PALM],
        secondary_hosts=[CropType.CITRUS, CropType.GRAPE],
        life_cycle_days=(35, 60),
        generations_per_year=4,
        overwintering_stage=PestLifeStage.LARVA,
        optimal_temperature_c=(25.0, 32.0),
        optimal_humidity_pct=(50.0, 70.0),
        is_quarantine_pest=False,
        economic_importance="high",
        economic_importance_ar="عالية",
        potential_yield_loss_pct=(15.0, 40.0),
        distribution_regions=["Middle East", "North Africa", "Mediterranean"],
        first_reported_saudi="Native",
        detection_difficulty="moderate",
        detection_notes="Use pheromone traps. Inspect fruits for entry holes and webbing.",
        detection_notes_ar="استخدم المصائد الفرمونية. افحص الثمار للثقوب والخيوط.",
    ),
    # -------------------------------------------------------------------------
    # DESERT LOCUST - الجراد الصحراوي
    # -------------------------------------------------------------------------
    "LOCUST001": PestIdentification(
        id="LOCUST001",
        scientific_name="Schistocerca gregaria",
        common_name="Desert Locust",
        common_name_ar="الجراد الصحراوي",
        local_names=["الجراد", "جراد الصحراء"],
        category=PestCategory.INSECT,
        family="Acrididae",
        order="Orthoptera",
        description="The most devastating migratory pest. Swarms can travel long distances and "
        "consume huge quantities of vegetation. A major threat to food security.",
        description_ar="أكثر الآفات المهاجرة تدميراً. يمكن للأسراب السفر لمسافات طويلة واستهلاك "
        "كميات هائلة من النباتات. تهديد رئيسي للأمن الغذائي.",
        adult_description="Large grasshopper (60-75mm), solitary phase: green/brown, gregarious phase: yellow/pink.",
        adult_description_ar="جرادة كبيرة (60-75 مم)، الطور الانفرادي: أخضر/بني، الطور التجمعي: أصفر/وردي.",
        larva_description="Hoppers (nymphs) pass through 5-6 instars, changing color with phase.",
        larva_description_ar="الحوريات (النطاطات) تمر بـ 5-6 أطوار، تتغير ألوانها مع الطور.",
        egg_description="Egg pods buried 10-15cm in sandy soil, containing 80-120 eggs.",
        egg_description_ar="كبسولات بيض مدفونة 10-15 سم في التربة الرملية، تحتوي 80-120 بيضة.",
        damage_symptoms=[
            "Complete defoliation of plants",
            "Consumption of all green vegetation",
            "Bark stripping from trees",
            "Total crop loss in path of swarms",
        ],
        damage_symptoms_ar=[
            "تعرية كاملة للنباتات",
            "استهلاك كل الغطاء النباتي الأخضر",
            "تقشير لحاء الأشجار",
            "خسارة كاملة للمحصول في مسار الأسراب",
        ],
        adult_size_mm=(60.0, 75.0),
        adult_color="Variable: green/brown (solitary) or yellow/pink (gregarious)",
        adult_color_ar="متغير: أخضر/بني (انفرادي) أو أصفر/وردي (تجمعي)",
        distinguishing_features=[
            "Large size",
            "Phase polyphenism (color changes)",
            "Strong fliers - migrate long distances",
            "Form dense swarms",
        ],
        distinguishing_features_ar=[
            "حجم كبير",
            "تعدد الأشكال الطوري (تغير الألوان)",
            "طيارات قوية - تهاجر لمسافات طويلة",
            "تشكل أسراباً كثيفة",
        ],
        primary_hosts=[CropType.WHEAT, CropType.BARLEY, CropType.ALFALFA],
        secondary_hosts=[CropType.DATE_PALM, CropType.CITRUS, CropType.GRAPE],
        life_cycle_days=(40, 90),
        generations_per_year=3,
        overwintering_stage=PestLifeStage.EGG,
        optimal_temperature_c=(25.0, 38.0),
        optimal_humidity_pct=(40.0, 60.0),
        is_quarantine_pest=True,
        economic_importance="very_high",
        economic_importance_ar="عالية جداً",
        potential_yield_loss_pct=(80.0, 100.0),
        distribution_regions=["Africa", "Middle East", "South Asia"],
        first_reported_saudi="Native (invasion zones)",
        detection_difficulty="easy",
        detection_notes="Monitor FAO locust bulletins. Report any swarm sightings immediately to authorities.",
        detection_notes_ar="راقب نشرات الجراد من الفاو. أبلغ عن أي مشاهدات للأسراب فوراً للسلطات.",
    ),
    # -------------------------------------------------------------------------
    # THRIPS - التربس
    # -------------------------------------------------------------------------
    "THRIPS001": PestIdentification(
        id="THRIPS001",
        scientific_name="Frankliniella occidentalis",
        common_name="Western Flower Thrips",
        common_name_ar="تربس الأزهار الغربي",
        local_names=["التربس", "هدبيات الأجنحة"],
        category=PestCategory.INSECT,
        family="Thripidae",
        order="Thysanoptera",
        description="Tiny insect causing silvering damage to leaves and flowers. Important vector "
        "of tospoviruses (TSWV). Difficult to control due to cryptic behavior.",
        description_ar="حشرة صغيرة جداً تسبب تفضض الأوراق والأزهار. ناقل مهم لفيروسات توسبو. "
        "صعبة المكافحة بسبب سلوكها الخفي.",
        adult_description="Very small (1-2mm), slender, yellowish-brown with fringed wings.",
        adult_description_ar="صغيرة جداً (1-2 مم)، نحيلة، بنية مصفرة بأجنحة مهدبة.",
        larva_description="Nymphs similar to adults but wingless, pale yellow.",
        larva_description_ar="الحوريات مشابهة للحشرات الكاملة لكن بدون أجنحة، صفراء باهتة.",
        egg_description="Kidney-shaped, inserted into plant tissue.",
        egg_description_ar="على شكل كلية، تُدخل في أنسجة النبات.",
        damage_symptoms=[
            "Silvering/bronzing of leaves",
            "Distorted flowers and fruit",
            "Scarring on fruit surface",
            "Virus symptoms (ring spots, necrosis)",
            "Feeding scars on petals",
        ],
        damage_symptoms_ar=[
            "تفضض/تبرنز الأوراق",
            "تشوه الأزهار والثمار",
            "ندوب على سطح الثمار",
            "أعراض فيروسية (بقع حلقية، تنخر)",
            "ندوب تغذية على البتلات",
        ],
        adult_size_mm=(1.0, 2.0),
        adult_color="Yellowish-brown",
        adult_color_ar="بني مصفر",
        distinguishing_features=[
            "Fringed wings",
            "Slender body",
            "Jump when disturbed",
            "Hide in flowers and growing points",
        ],
        distinguishing_features_ar=[
            "أجنحة مهدبة",
            "جسم نحيل",
            "تقفز عند إزعاجها",
            "تختبئ في الأزهار ونقاط النمو",
        ],
        primary_hosts=[CropType.TOMATO, CropType.PEPPER, CropType.CUCUMBER],
        secondary_hosts=[CropType.ONION, CropType.GRAPE],
        life_cycle_days=(14, 21),
        generations_per_year=15,
        overwintering_stage=PestLifeStage.ADULT,
        optimal_temperature_c=(25.0, 30.0),
        optimal_humidity_pct=(40.0, 70.0),
        is_quarantine_pest=False,
        economic_importance="high",
        economic_importance_ar="عالية",
        potential_yield_loss_pct=(20.0, 50.0),
        distribution_regions=["Worldwide"],
        first_reported_saudi="1990s",
        detection_difficulty="difficult",
        detection_notes="Use blue sticky traps. Tap flowers over white paper to dislodge thrips.",
        detection_notes_ar="استخدم المصائد اللاصقة الزرقاء. اضرب الأزهار فوق ورق أبيض لإسقاط التربس.",
    ),
    # -------------------------------------------------------------------------
    # FRUIT FLIES - ذباب الفاكهة
    # -------------------------------------------------------------------------
    "FRUITFLY001": PestIdentification(
        id="FRUITFLY001",
        scientific_name="Ceratitis capitata",
        common_name="Mediterranean Fruit Fly",
        common_name_ar="ذبابة فاكهة البحر المتوسط",
        local_names=["ذبابة الفاكهة", "الميدفلاي"],
        category=PestCategory.INSECT,
        family="Tephritidae",
        order="Diptera",
        description="Major quarantine pest of fruits. Females lay eggs in fruit, larvae feed inside "
        "causing rot and fruit drop. Affects many fruit crops.",
        description_ar="آفة حجر زراعي رئيسية للفواكه. تضع الإناث البيض في الثمار، تتغذى اليرقات بالداخل "
        "مسببة التعفن وسقوط الثمار. تصيب العديد من محاصيل الفاكهة.",
        adult_description="Small fly (4-5mm), yellowish with characteristic wing pattern (brown bands).",
        adult_description_ar="ذبابة صغيرة (4-5 مم)، صفراء بنمط جناحي مميز (أشرطة بنية).",
        larva_description="White maggot, legless, up to 8mm long, found inside fruit.",
        larva_description_ar="يرقة بيضاء، بدون أرجل، يصل طولها إلى 8 مم، توجد داخل الثمار.",
        egg_description="White, banana-shaped, laid under fruit skin.",
        egg_description_ar="بيضاء، على شكل موزة، توضع تحت قشرة الثمرة.",
        damage_symptoms=[
            "Oviposition punctures on fruit",
            "Soft spots on fruit surface",
            "Internal rot and tunneling",
            "Premature fruit drop",
            "Secondary fungal infections",
        ],
        damage_symptoms_ar=[
            "ثقوب وضع البيض على الثمار",
            "بقع لينة على سطح الثمرة",
            "تعفن داخلي وأنفاق",
            "سقوط مبكر للثمار",
            "إصابات فطرية ثانوية",
        ],
        adult_size_mm=(4.0, 5.0),
        adult_color="Yellowish with brown wing bands",
        adult_color_ar="أصفر بأشرطة جناحية بنية",
        distinguishing_features=[
            "Characteristic wing pattern",
            "Yellow scutellum",
            "Black markings on thorax",
        ],
        distinguishing_features_ar=[
            "نمط جناحي مميز",
            "حاجز أصفر",
            "علامات سوداء على الصدر",
        ],
        primary_hosts=[CropType.CITRUS, CropType.GRAPE],
        secondary_hosts=[CropType.DATE_PALM],
        life_cycle_days=(21, 30),
        generations_per_year=6,
        overwintering_stage=PestLifeStage.PUPA,
        optimal_temperature_c=(23.0, 30.0),
        optimal_humidity_pct=(60.0, 80.0),
        is_quarantine_pest=True,
        economic_importance="very_high",
        economic_importance_ar="عالية جداً",
        potential_yield_loss_pct=(30.0, 80.0),
        distribution_regions=["Mediterranean", "Middle East", "Africa", "Americas", "Australia"],
        first_reported_saudi="Present",
        detection_difficulty="moderate",
        detection_notes="Use McPhail traps with protein bait. Inspect fruit for oviposition marks.",
        detection_notes_ar="استخدم مصائد ماكفيل مع طعم بروتيني. افحص الثمار لعلامات وضع البيض.",
    ),
}


# =============================================================================
# PEST LOOKUP FUNCTIONS - دوال البحث عن الآفات
# =============================================================================


def get_pest_by_id(pest_id: str) -> PestIdentification | None:
    """
    Get pest identification by ID.
    الحصول على تعريف الآفة بواسطة المعرف.
    """
    return PEST_DATABASE.get(pest_id)


def get_pest_by_scientific_name(scientific_name: str) -> PestIdentification | None:
    """
    Get pest identification by scientific name.
    الحصول على تعريف الآفة بواسطة الاسم العلمي.
    """
    scientific_lower = scientific_name.lower()
    for pest in PEST_DATABASE.values():
        if pest.scientific_name.lower() == scientific_lower:
            return pest
    return None


def search_pests_by_name(
    query: str,
    include_arabic: bool = True,
    include_local_names: bool = True,
) -> list[PestIdentification]:
    """
    Search pests by common name, Arabic name, or local names.
    البحث عن الآفات بالاسم الشائع أو العربي أو الأسماء المحلية.
    """
    results: list[PestIdentification] = []
    query_lower = query.lower()

    for pest in PEST_DATABASE.values():
        # Check English common name
        if query_lower in pest.common_name.lower():
            results.append(pest)
            continue

        # Check Arabic name
        if include_arabic and query in pest.common_name_ar:
            results.append(pest)
            continue

        # Check local names
        if include_local_names:
            for local_name in pest.local_names:
                if query in local_name or query_lower in local_name.lower():
                    results.append(pest)
                    break

    return results


def get_pests_by_crop(crop_type: CropType) -> list[PestIdentification]:
    """
    Get all pests that affect a specific crop.
    الحصول على جميع الآفات التي تصيب محصولاً محدداً.
    """
    results: list[PestIdentification] = []
    for pest in PEST_DATABASE.values():
        if crop_type in pest.primary_hosts or crop_type in pest.secondary_hosts:
            results.append(pest)
    return results


def get_pests_by_category(category: PestCategory) -> list[PestIdentification]:
    """
    Get all pests of a specific category.
    الحصول على جميع الآفات من فئة محددة.
    """
    return [pest for pest in PEST_DATABASE.values() if pest.category == category]


def get_quarantine_pests() -> list[PestIdentification]:
    """
    Get all quarantine pests.
    الحصول على جميع آفات الحجر الزراعي.
    """
    return [pest for pest in PEST_DATABASE.values() if pest.is_quarantine_pest]


def get_high_priority_pests() -> list[PestIdentification]:
    """
    Get pests with very high economic importance.
    الحصول على الآفات ذات الأهمية الاقتصادية العالية جداً.
    """
    return [pest for pest in PEST_DATABASE.values() if pest.economic_importance in ("very_high", "high")]


# =============================================================================
# IDENTIFICATION HELPERS - مساعدات التعريف
# =============================================================================


def identify_by_symptoms(
    symptoms: list[str],
    crop_type: CropType | None = None,
    min_match_score: float = 0.3,
) -> list[tuple[PestIdentification, float]]:
    """
    Identify possible pests based on observed symptoms.
    Returns list of (pest, match_score) tuples sorted by score descending.

    تعريف الآفات المحتملة بناءً على الأعراض الملاحظة.
    يرجع قائمة من (الآفة، درجة التطابق) مرتبة تنازلياً.
    """
    results: list[tuple[PestIdentification, float]] = []
    symptoms_lower = [s.lower() for s in symptoms]

    for pest in PEST_DATABASE.values():
        # Skip if crop filter doesn't match
        if crop_type and crop_type not in pest.primary_hosts and crop_type not in pest.secondary_hosts:
            continue

        # Calculate symptom match score
        all_pest_symptoms = [s.lower() for s in pest.damage_symptoms]
        all_pest_symptoms.extend([s.lower() for s in pest.damage_symptoms_ar])

        matches = 0
        for symptom in symptoms_lower:
            for pest_symptom in all_pest_symptoms:
                if symptom in pest_symptom or pest_symptom in symptom:
                    matches += 1
                    break

        if all_pest_symptoms:
            score = matches / max(len(symptoms_lower), 1)
        else:
            score = 0.0

        if score >= min_match_score:
            results.append((pest, score))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def identify_by_description(
    description: str,
    size_mm: tuple[float, float] | None = None,
    color: str | None = None,
    has_wings: bool | None = None,
) -> list[tuple[PestIdentification, float]]:
    """
    Identify possible pests based on physical description.

    تعريف الآفات المحتملة بناءً على الوصف الجسدي.
    """
    results: list[tuple[PestIdentification, float]] = []
    desc_lower = description.lower()

    for pest in PEST_DATABASE.values():
        score = 0.0
        max_score = 4.0  # Maximum possible score

        # Check description match
        all_desc = pest.adult_description.lower() + pest.larva_description.lower() + pest.description.lower()
        if desc_lower:
            words = desc_lower.split()
            word_matches = sum(1 for word in words if word in all_desc and len(word) > 3)
            score += min(word_matches / max(len(words), 1), 1.0)

        # Check size match
        if size_mm and pest.adult_size_mm:
            obs_size = (size_mm[0] + size_mm[1]) / 2
            pest_size = (pest.adult_size_mm[0] + pest.adult_size_mm[1]) / 2
            size_diff = abs(obs_size - pest_size) / max(pest_size, 1)
            if size_diff < 0.3:  # Within 30%
                score += 1.0
            elif size_diff < 0.5:
                score += 0.5

        # Check color match
        if color:
            color_lower = color.lower()
            if color_lower in pest.adult_color.lower() or color_lower in pest.adult_color_ar:
                score += 1.0

        # Check wing presence
        if has_wings is not None:
            wing_keywords = ["wing", "fly", "moth", "جناح", "طيران"]
            has_wing_desc = any(kw in all_desc for kw in wing_keywords)
            if has_wings == has_wing_desc:
                score += 1.0

        if score > 0:
            results.append((pest, score / max_score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


def get_identification_guide(pest_id: str, language: str = "both") -> str:
    """
    Get a formatted identification guide for a pest.

    الحصول على دليل تعريف منسق للآفة.

    Args:
        pest_id: Pest ID
        language: "en", "ar", or "both"

    Returns:
        Formatted identification guide string
    """
    pest = get_pest_by_id(pest_id)
    if not pest:
        return f"Pest not found: {pest_id}"

    lines: list[str] = []

    if language in ("en", "both"):
        lines.append(f"# {pest.common_name}")
        lines.append(f"**Scientific Name:** {pest.scientific_name}")
        lines.append(f"**Family:** {pest.family}")
        lines.append("")
        lines.append("## Description")
        lines.append(pest.description)
        lines.append("")
        lines.append("## Identification")
        lines.append(f"**Adult:** {pest.adult_description}")
        if pest.adult_size_mm:
            lines.append(f"**Size:** {pest.adult_size_mm[0]}-{pest.adult_size_mm[1]} mm")
        lines.append(f"**Color:** {pest.adult_color}")
        lines.append("")
        lines.append("**Distinguishing Features:**")
        for feature in pest.distinguishing_features:
            lines.append(f"- {feature}")
        lines.append("")
        lines.append("## Damage Symptoms")
        for symptom in pest.damage_symptoms:
            lines.append(f"- {symptom}")

    if language == "both":
        lines.append("")
        lines.append("---")
        lines.append("")

    if language in ("ar", "both"):
        lines.append(f"# {pest.common_name_ar}")
        lines.append(f"**الاسم العلمي:** {pest.scientific_name}")
        lines.append(f"**العائلة:** {pest.family}")
        lines.append("")
        lines.append("## الوصف")
        lines.append(pest.description_ar)
        lines.append("")
        lines.append("## التعريف")
        lines.append(f"**الحشرة الكاملة:** {pest.adult_description_ar}")
        if pest.adult_size_mm:
            lines.append(f"**الحجم:** {pest.adult_size_mm[0]}-{pest.adult_size_mm[1]} مم")
        lines.append(f"**اللون:** {pest.adult_color_ar}")
        lines.append("")
        lines.append("**السمات المميزة:**")
        for feature in pest.distinguishing_features_ar:
            lines.append(f"- {feature}")
        lines.append("")
        lines.append("## أعراض الضرر")
        for symptom in pest.damage_symptoms_ar:
            lines.append(f"- {symptom}")

    return "\n".join(lines)


def assess_infestation_level(
    observation: ScoutObservation,
    pest_id: str,
) -> InfestationLevel:
    """
    Assess infestation level based on observation data.

    تقييم مستوى الإصابة بناءً على بيانات الملاحظة.
    """
    pest = get_pest_by_id(pest_id)
    if not pest:
        return InfestationLevel.NONE

    count = observation.count_per_unit or observation.count or 0
    damage_rating = observation.damage_rating or 0

    # Simple threshold-based assessment
    # This should be replaced with pest-specific thresholds from the thresholds module
    if count == 0 and damage_rating == 0:
        return InfestationLevel.NONE
    elif count <= 1 or damage_rating <= 1:
        return InfestationLevel.TRACE
    elif count <= 3 or damage_rating <= 3:
        return InfestationLevel.LOW
    elif count <= 10 or damage_rating <= 5:
        return InfestationLevel.MODERATE
    elif count <= 30 or damage_rating <= 7:
        return InfestationLevel.HIGH
    elif count <= 50 or damage_rating <= 9:
        return InfestationLevel.SEVERE
    else:
        return InfestationLevel.CRITICAL


def get_similar_pests(pest_id: str) -> list[PestIdentification]:
    """
    Get pests that might be confused with the given pest.

    الحصول على الآفات التي قد تُخلط مع الآفة المحددة.
    """
    pest = get_pest_by_id(pest_id)
    if not pest:
        return []

    similar: list[PestIdentification] = []
    for other_pest in PEST_DATABASE.values():
        if other_pest.id == pest_id:
            continue

        # Same category
        if other_pest.category != pest.category:
            continue

        # Similar hosts
        shared_hosts = set(pest.primary_hosts) & set(other_pest.primary_hosts) or set(pest.primary_hosts) & set(
            other_pest.secondary_hosts
        )
        if not shared_hosts:
            continue

        # Similar size (if available)
        if pest.adult_size_mm and other_pest.adult_size_mm:
            pest_size = (pest.adult_size_mm[0] + pest.adult_size_mm[1]) / 2
            other_size = (other_pest.adult_size_mm[0] + other_pest.adult_size_mm[1]) / 2
            if abs(pest_size - other_size) > pest_size * 0.5:
                continue

        similar.append(other_pest)

    return similar


# =============================================================================
# SEASONAL AND REGIONAL HELPERS - مساعدات موسمية وإقليمية
# =============================================================================


def get_seasonal_pests(month: int, crop_type: CropType | None = None) -> list[PestIdentification]:
    """
    Get pests that are typically active in a given month.

    الحصول على الآفات النشطة عادة في شهر معين.

    Note: This is a simplified implementation. In production, this should
    use actual phenology data from the region.
    """
    # Seasonal activity patterns (simplified for Middle East)
    seasonal_patterns = {
        # pest_id: (active_months)
        "RPW001": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),  # Year-round
        "DUBAS001": (3, 4, 5, 9, 10, 11),  # Spring and fall generations
        "APHID001": (2, 3, 4, 5, 10, 11, 12),  # Cool season
        "APHID002": (2, 3, 4, 5, 10, 11, 12),  # Cool season
        "WHITEFLY001": (4, 5, 6, 7, 8, 9, 10),  # Warm season
        "MITE001": (5, 6, 7, 8, 9),  # Hot, dry season
        "TUTA001": (3, 4, 5, 6, 7, 8, 9, 10),  # Active season
        "DMOTH001": (6, 7, 8, 9, 10),  # Fruit ripening season
        "LOCUST001": (2, 3, 4, 5, 6, 10, 11),  # Migration seasons
        "THRIPS001": (3, 4, 5, 6, 7, 8),  # Flowering season
        "FRUITFLY001": (5, 6, 7, 8, 9, 10),  # Fruit season
    }

    results: list[PestIdentification] = []
    for pest_id, active_months in seasonal_patterns.items():
        if month in active_months:
            pest = get_pest_by_id(pest_id)
            if pest:
                if crop_type is None or crop_type in pest.primary_hosts or crop_type in pest.secondary_hosts:
                    results.append(pest)

    return results


def get_pest_risk_factors(
    pest_id: str,
    temperature_c: float | None = None,
    humidity_pct: float | None = None,
) -> dict[str, Any]:
    """
    Assess environmental risk factors for pest development.

    تقييم عوامل الخطر البيئية لتطور الآفة.
    """
    pest = get_pest_by_id(pest_id)
    if not pest:
        return {"error": f"Pest not found: {pest_id}"}

    result: dict[str, Any] = {
        "pest_id": pest_id,
        "pest_name": pest.common_name,
        "pest_name_ar": pest.common_name_ar,
        "temperature_risk": "unknown",
        "humidity_risk": "unknown",
        "overall_risk": "unknown",
    }

    # Temperature risk
    if temperature_c is not None and pest.optimal_temperature_c:
        opt_min, opt_max = pest.optimal_temperature_c
        if opt_min <= temperature_c <= opt_max:
            result["temperature_risk"] = "high"
            result["temperature_risk_ar"] = "مرتفع"
        elif (opt_min - 5) <= temperature_c <= (opt_max + 5):
            result["temperature_risk"] = "moderate"
            result["temperature_risk_ar"] = "متوسط"
        else:
            result["temperature_risk"] = "low"
            result["temperature_risk_ar"] = "منخفض"

    # Humidity risk
    if humidity_pct is not None and pest.optimal_humidity_pct:
        opt_min, opt_max = pest.optimal_humidity_pct
        if opt_min <= humidity_pct <= opt_max:
            result["humidity_risk"] = "high"
            result["humidity_risk_ar"] = "مرتفع"
        elif (opt_min - 15) <= humidity_pct <= (opt_max + 15):
            result["humidity_risk"] = "moderate"
            result["humidity_risk_ar"] = "متوسط"
        else:
            result["humidity_risk"] = "low"
            result["humidity_risk_ar"] = "منخفض"

    # Overall risk
    risks = [result["temperature_risk"], result["humidity_risk"]]
    if "high" in risks:
        result["overall_risk"] = "high"
        result["overall_risk_ar"] = "مرتفع"
    elif risks.count("moderate") >= 1:
        result["overall_risk"] = "moderate"
        result["overall_risk_ar"] = "متوسط"
    else:
        result["overall_risk"] = "low"
        result["overall_risk_ar"] = "منخفض"

    return result
