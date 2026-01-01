#!/usr/bin/env python3
"""
Create Golden Dataset
إنشاء مجموعة البيانات الذهبية

Script to create default golden dataset for agent evaluation.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def create_golden_dataset() -> List[Dict[str, Any]]:
    """
    Create comprehensive golden dataset
    إنشاء مجموعة بيانات ذهبية شاملة
    """
    dataset = [
        # English: Disease Diagnosis
        {
            "id": "disease-001-en",
            "category": "disease_diagnosis",
            "language": "en",
            "input": {
                "query": "My wheat crop has yellow spots on leaves. What could be the problem?",
                "context": {
                    "crop_type": "wheat",
                    "location": "Yemen",
                    "season": "winter",
                },
            },
            "expected_output": {
                "response": "Yellow spots on wheat leaves typically indicate fungal disease such as leaf rust or septoria.",
                "agents": ["disease_expert"],
                "key_points": ["yellow spots", "fungal disease", "wheat", "treatment"],
                "safety_constraints": ["accurate_diagnosis", "no_harmful_chemicals"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["disease", "wheat", "leaf"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # Arabic: Disease Diagnosis
        {
            "id": "disease-001-ar",
            "category": "disease_diagnosis",
            "language": "ar",
            "input": {
                "query": "محصول القمح لديه بقع صفراء على الأوراق. ما المشكلة؟",
                "context": {
                    "crop_type": "wheat",
                    "location": "اليمن",
                    "season": "شتاء",
                },
            },
            "expected_output": {
                "response": "البقع الصفراء على أوراق القمح تشير عادة إلى مرض فطري مثل صدأ الأوراق",
                "agents": ["disease_expert"],
                "key_points": ["بقع صفراء", "مرض فطري", "القمح", "علاج"],
                "safety_constraints": ["accurate_diagnosis", "no_harmful_chemicals"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["مرض", "القمح"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # English: Irrigation Advice
        {
            "id": "irrigation-001-en",
            "category": "irrigation",
            "language": "en",
            "input": {
                "query": "When should I irrigate my tomato plants?",
                "context": {
                    "crop_type": "tomato",
                    "growth_stage": "flowering",
                    "soil_moisture": 45,
                    "temperature": 28,
                },
            },
            "expected_output": {
                "response": "Tomato plants during flowering stage need consistent moisture. Irrigate when soil moisture drops below 50%.",
                "agents": ["irrigation_advisor"],
                "key_points": [
                    "tomato",
                    "flowering",
                    "soil moisture",
                    "irrigation schedule",
                ],
                "safety_constraints": ["water_conservation", "no_overwatering"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["irrigation", "tomato", "moisture"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # English: Field Analysis
        {
            "id": "field-001-en",
            "category": "field_analysis",
            "language": "en",
            "input": {
                "query": "Analyze the health of my corn field based on NDVI data",
                "context": {
                    "field_id": "field-123",
                    "crop_type": "corn",
                    "ndvi_average": 0.65,
                    "growth_stage": "vegetative",
                },
            },
            "expected_output": {
                "response": "NDVI of 0.65 indicates moderate vegetation health. Corn in vegetative stage should have higher values.",
                "agents": ["field_analyst"],
                "key_points": ["NDVI", "corn", "field health", "vegetation"],
                "safety_constraints": ["accurate_analysis"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["NDVI", "corn", "health"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # English: Yield Prediction
        {
            "id": "yield-001-en",
            "category": "yield_prediction",
            "language": "en",
            "input": {
                "query": "What will be the expected yield for my wheat field?",
                "context": {
                    "crop_type": "wheat",
                    "field_size_hectares": 10,
                    "growth_stage": "grain filling",
                    "weather_conditions": "favorable",
                },
            },
            "expected_output": {
                "response": "Based on favorable conditions and grain filling stage, expect 4-5 tons per hectare yield.",
                "agents": ["yield_predictor"],
                "key_points": ["yield", "wheat", "prediction", "tons per hectare"],
                "safety_constraints": ["realistic_expectations"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.75,
                "required_keywords": ["yield", "wheat", "tons"],
                "forbidden_keywords": [],
                "max_latency_ms": 5000,
            },
        },
        # Multi-agent coordination test
        {
            "id": "multi-001-en",
            "category": "multi_agent",
            "language": "en",
            "input": {
                "query": "My wheat field shows low NDVI. Should I irrigate and how will this affect yield?",
                "context": {
                    "crop_type": "wheat",
                    "ndvi_average": 0.45,
                    "soil_moisture": 30,
                    "growth_stage": "heading",
                },
            },
            "expected_output": {
                "response": "Low NDVI and soil moisture indicate stress. Immediate irrigation recommended to prevent yield loss.",
                "agents": ["field_analyst", "irrigation_advisor", "yield_predictor"],
                "key_points": ["NDVI", "irrigation", "yield impact", "coordination"],
                "safety_constraints": ["holistic_advice"],
            },
            "evaluation_criteria": {
                "min_similarity": 0.70,
                "required_keywords": ["NDVI", "irrigation", "yield"],
                "forbidden_keywords": [],
                "max_latency_ms": 8000,
            },
        },
    ]

    return dataset


def main():
    """Main execution"""
    # Create datasets directory
    script_dir = Path(__file__).parent
    datasets_dir = script_dir.parent / "datasets"
    datasets_dir.mkdir(parents=True, exist_ok=True)

    # Create golden dataset
    golden_dataset = create_golden_dataset()

    # Save to file
    output_file = datasets_dir / "golden_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(golden_dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ Created golden dataset with {len(golden_dataset)} test cases")
    print(f"📁 Saved to: {output_file}")

    # Print summary
    categories = {}
    languages = {}
    for case in golden_dataset:
        cat = case.get("category", "unknown")
        lang = case.get("language", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        languages[lang] = languages.get(lang, 0) + 1

    print("\n📊 Dataset Summary:")
    print(f"  Categories: {categories}")
    print(f"  Languages: {languages}")


if __name__ == "__main__":
    main()
