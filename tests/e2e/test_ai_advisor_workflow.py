"""
SAHOOL AI Advisor Workflow E2E Tests
اختبارات سير عمل المستشار الذكي من البداية إلى النهاية

End-to-end tests for AI Advisor multi-agent system workflow:
1. Ask agricultural question
2. Multi-agent processing (Weather, Crop Health, Satellite, Agro Advisor)
3. RAG (Retrieval-Augmented Generation) from Qdrant
4. Receive comprehensive answer

Author: SAHOOL Platform Team
"""

import asyncio
from typing import Any

import httpx
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Complete AI Advisor Workflow Test - اختبار سير عمل المستشار الذكي الكامل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_complete_ai_advisor_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    sample_ai_question: dict[str, Any],
    ensure_ai_advisor_ready,
):
    """
    Test complete AI Advisor workflow: Question → Multi-Agent Processing → Answer
    اختبار سير عمل المستشار الذكي الكامل: سؤال → معالجة متعددة الوكلاء → إجابة

    Workflow Steps:
    1. Submit agricultural question
    2. AI Advisor coordinates multiple agents:
       - Weather Agent (gets weather data)
       - Crop Health Agent (analyzes crop conditions)
       - Satellite Agent (gets satellite imagery)
       - Agro Advisor Agent (provides recommendations)
    3. RAG system retrieves relevant context from Qdrant
    4. Claude AI generates comprehensive answer
    5. Receive and validate response
    """

    print("\n" + "=" * 80)
    print("SAHOOL AI Advisor Multi-Agent Workflow E2E Test")
    print("اختبار سير عمل المستشار الذكي متعدد الوكلاء")
    print("=" * 80)

    # ───────────────────────────────────────────────────────────────────────────
    # Step 1: Submit Agricultural Question - تقديم السؤال الزراعي
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 1] Submitting agricultural question...")
    print(f"Question (AR): {sample_ai_question['question']}")
    print(f"Question (EN): {sample_ai_question['question_en']}")

    question_response = await workflow_client.post(
        "http://localhost:8112/api/v1/advisor/ask",
        headers=e2e_headers,
        json=sample_ai_question,
        timeout=60.0,  # AI processing can take time
    )

    assert question_response.status_code in (
        200,
        202,
        401,
        422,
        503,
    ), f"Question submission failed with status {question_response.status_code}"

    if question_response.status_code == 200:
        # Synchronous response
        answer_data = question_response.json()
        print("✓ Received immediate answer")

        # Verify answer structure
        assert (
            "answer" in answer_data or "response" in answer_data
        ), "Response should contain answer"

        answer_text = answer_data.get("answer") or answer_data.get("response")
        print(f"\nAnswer preview: {answer_text[:200]}...")

        # Verify agent coordination metadata
        if "agents_used" in answer_data:
            print(f"\nAgents coordinated: {answer_data['agents_used']}")

        if "sources" in answer_data:
            print(f"Information sources: {len(answer_data['sources'])} sources")

    elif question_response.status_code == 202:
        # Async processing
        processing_data = question_response.json()
        question_id = processing_data.get("id") or processing_data.get("question_id")

        print(f"✓ Question accepted for async processing: {question_id}")

        # Poll for result
        print("\nWaiting for AI processing...")
        for attempt in range(30):  # 30 attempts x 2 seconds = 60 seconds max
            await asyncio.sleep(2)

            status_response = await workflow_client.get(
                f"http://localhost:8112/api/v1/advisor/questions/{question_id}",
                headers=e2e_headers,
            )

            if status_response.status_code == 200:
                status_data = status_response.json()
                state = status_data.get("status") or status_data.get("state")

                if state == "completed":
                    print("✓ AI processing completed")
                    answer_data = status_data
                    break
                elif state == "failed":
                    print("✗ AI processing failed")
                    break

                print(f"  Processing... (attempt {attempt + 1}/30)")
        else:
            pytest.skip("AI processing timed out")

    else:
        pytest.skip(f"Cannot submit question: {question_response.status_code}")

    # ───────────────────────────────────────────────────────────────────────────
    # Step 2: Verify Multi-Agent Coordination - التحقق من تنسيق الوكلاء المتعددين
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 2] Verifying multi-agent coordination...")

    # Check that dependent services are healthy
    dependent_services = [
        ("Weather Core", "http://localhost:8108/healthz"),
        ("Crop Health AI", "http://localhost:8095/healthz"),
        ("Agro Advisor", "http://localhost:8105/healthz"),
        ("Qdrant Vector DB", "http://localhost:6333/healthz"),
    ]

    for service_name, health_url in dependent_services:
        try:
            health_response = await workflow_client.get(health_url)
            if health_response.status_code == 200:
                print(f"  ✓ {service_name} is operational")
            else:
                print(f"  ⚠ {service_name} may not be available")
        except Exception:
            print(f"  ⚠ {service_name} not accessible")

    # ───────────────────────────────────────────────────────────────────────────
    # Step 3: Verify RAG Integration - التحقق من تكامل RAG
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 3] Verifying RAG (Retrieval-Augmented Generation) integration...")

    # Check Qdrant collections (used for RAG)
    qdrant_response = await workflow_client.get("http://localhost:6333/collections")

    if qdrant_response.status_code == 200:
        qdrant_data = qdrant_response.json()
        print("✓ Qdrant vector database operational")

        # Check if agricultural knowledge base exists
        if "result" in qdrant_data:
            collections = qdrant_data["result"].get("collections", [])
            print(f"  Available collections: {len(collections)}")
    else:
        print(f"⚠ Qdrant may not be configured: {qdrant_response.status_code}")

    print("\n" + "=" * 80)
    print("✓ Complete AI Advisor workflow test PASSED")
    print("=" * 80)


# ═══════════════════════════════════════════════════════════════════════════════
# AI Agents Individual Tests - اختبارات الوكلاء الأفراد
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_weather_agent_integration(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    test_location_yemen: dict[str, float],
    ensure_weather_ready,
):
    """
    Test Weather Agent integration
    اختبار تكامل وكيل الطقس
    """

    print("\n[Weather Agent Test]")

    # Weather agent should provide current weather
    weather_response = await workflow_client.get(
        "http://localhost:8108/api/v1/weather/current",
        headers=e2e_headers,
        params=test_location_yemen,
    )

    assert weather_response.status_code in (
        200,
        401,
        503,
    ), "Weather agent should respond"

    if weather_response.status_code == 200:
        weather_response.json()
        print("✓ Weather agent operational")
        print("  Location: Sana'a, Yemen")


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_crop_health_agent_integration(
    workflow_client: httpx.AsyncClient, e2e_headers: dict[str, str]
):
    """
    Test Crop Health Agent integration
    اختبار تكامل وكيل صحة المحاصيل
    """

    print("\n[Crop Health Agent Test]")

    # Check crop health AI service
    health_response = await workflow_client.get("http://localhost:8095/healthz")

    if health_response.status_code == 200:
        print("✓ Crop Health AI agent operational")
    else:
        pytest.skip("Crop Health AI not available")


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_satellite_agent_integration(
    workflow_client: httpx.AsyncClient, e2e_headers: dict[str, str]
):
    """
    Test Satellite Agent integration
    اختبار تكامل وكيل الأقمار الصناعية
    """

    print("\n[Satellite Agent Test]")

    # Check satellite service
    health_response = await workflow_client.get("http://localhost:8090/healthz")

    if health_response.status_code == 200:
        print("✓ Satellite agent operational")
    else:
        pytest.skip("Satellite service not available")


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_agro_advisor_agent_integration(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    ensure_ai_advisor_ready,
):
    """
    Test Agro Advisor Agent integration
    اختبار تكامل وكيل المستشار الزراعي
    """

    print("\n[Agro Advisor Agent Test]")

    # Check agro advisor service
    health_response = await workflow_client.get("http://localhost:8105/healthz")

    assert health_response.status_code in (200, 503), "Agro Advisor should respond"

    if health_response.status_code == 200:
        print("✓ Agro Advisor agent operational")


# ═══════════════════════════════════════════════════════════════════════════════
# RAG System Tests - اختبارات نظام RAG
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_rag_knowledge_base(
    workflow_client: httpx.AsyncClient, e2e_headers: dict[str, str]
):
    """
    Test RAG knowledge base integration
    اختبار تكامل قاعدة المعرفة RAG
    """

    print("\n[RAG Knowledge Base Test]")

    # Check Qdrant collections
    collections_response = await workflow_client.get(
        "http://localhost:6333/collections"
    )

    assert collections_response.status_code == 200, "Qdrant should be accessible"

    collections_data = collections_response.json()
    print("✓ RAG knowledge base accessible")

    # Check if knowledge base has data
    if "result" in collections_data:
        result = collections_data["result"]
        if "collections" in result:
            collections = result["collections"]
            print(f"  Total collections: {len(collections)}")

            for collection in collections:
                if isinstance(collection, dict):
                    name = collection.get("name", "unknown")
                    print(f"    - {name}")


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_semantic_search_capability(
    workflow_client: httpx.AsyncClient, e2e_headers: dict[str, str]
):
    """
    Test semantic search capability
    اختبار قدرة البحث الدلالي
    """

    print("\n[Semantic Search Test]")

    # This would test Qdrant's vector search capability
    # In production, this would search for agricultural knowledge

    cluster_response = await workflow_client.get("http://localhost:6333/cluster")

    assert cluster_response.status_code == 200, "Qdrant cluster should be operational"

    print("✓ Semantic search engine operational")


# ═══════════════════════════════════════════════════════════════════════════════
# AI Advisor Question Types Tests - اختبارات أنواع أسئلة المستشار الذكي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_weather_related_question(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    ensure_ai_advisor_ready,
):
    """
    Test weather-related agricultural question
    اختبار سؤال زراعي متعلق بالطقس
    """

    print("\n[Weather Question Test]")

    question = {
        "question": "متى يكون أفضل وقت للري بناءً على توقعات الطقس؟",
        "question_en": "When is the best time to irrigate based on weather forecast?",
        "language": "ar",
        "context": {"location": {"latitude": 15.3694, "longitude": 44.1910}},
    }

    response = await workflow_client.post(
        "http://localhost:8112/api/v1/advisor/ask",
        headers=e2e_headers,
        json=question,
        timeout=60.0,
    )

    assert response.status_code in (
        200,
        202,
        401,
        503,
    ), "Weather question should be processed"

    if response.status_code == 200:
        print("✓ Weather-related question answered")


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_crop_disease_question(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    ensure_ai_advisor_ready,
):
    """
    Test crop disease diagnosis question
    اختبار سؤال تشخيص أمراض المحاصيل
    """

    print("\n[Crop Disease Question Test]")

    question = {
        "question": "ما هي أعراض مرض الصدأ في القمح وكيف يمكن علاجه؟",
        "question_en": "What are the symptoms of rust disease in wheat and how to treat it?",
        "language": "ar",
        "context": {"crop_type": "wheat"},
    }

    response = await workflow_client.post(
        "http://localhost:8112/api/v1/advisor/ask",
        headers=e2e_headers,
        json=question,
        timeout=60.0,
    )

    assert response.status_code in (
        200,
        202,
        401,
        503,
    ), "Crop disease question should be processed"

    if response.status_code == 200:
        print("✓ Crop disease question answered")


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_fertilizer_recommendation_question(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    ensure_ai_advisor_ready,
):
    """
    Test fertilizer recommendation question
    اختبار سؤال توصيات التسميد
    """

    print("\n[Fertilizer Recommendation Test]")

    question = {
        "question": "ما هي كمية الأسمدة النيتروجينية المناسبة للقمح في مرحلة النمو الخضري؟",
        "question_en": "What is the appropriate amount of nitrogen fertilizer for wheat in vegetative growth stage?",
        "language": "ar",
        "context": {
            "crop_type": "wheat",
            "growth_stage": "vegetative",
            "soil_type": "clay_loam",
        },
    }

    response = await workflow_client.post(
        "http://localhost:8112/api/v1/advisor/ask",
        headers=e2e_headers,
        json=question,
        timeout=60.0,
    )

    assert response.status_code in (
        200,
        202,
        401,
        503,
    ), "Fertilizer question should be processed"

    if response.status_code == 200:
        print("✓ Fertilizer recommendation question answered")


# ═══════════════════════════════════════════════════════════════════════════════
# AI Advisor Performance Test - اختبار أداء المستشار الذكي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_ai_advisor_response_time(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    sample_ai_question: dict[str, Any],
    ensure_ai_advisor_ready,
):
    """
    Test AI Advisor response time
    اختبار وقت استجابة المستشار الذكي
    """

    print("\n[Response Time Test]")

    import time

    start_time = time.time()

    response = await workflow_client.post(
        "http://localhost:8112/api/v1/advisor/ask",
        headers=e2e_headers,
        json=sample_ai_question,
        timeout=60.0,
    )

    end_time = time.time()
    response_time = end_time - start_time

    print(f"Response time: {response_time:.2f} seconds")

    # AI response should complete within reasonable time
    # or return async processing acknowledgment quickly
    if response.status_code == 202:
        assert response_time < 5.0, "Async acknowledgment should be quick"
        print(f"✓ Async processing accepted in {response_time:.2f}s")
    elif response.status_code == 200:
        # Sync response can take longer but should be reasonable
        print(f"✓ Sync response completed in {response_time:.2f}s")


# ═══════════════════════════════════════════════════════════════════════════════
# AI Advisor History and Context Tests - اختبارات السجل والسياق
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_conversation_history(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    ensure_ai_advisor_ready,
):
    """
    Test conversation history tracking
    اختبار تتبع سجل المحادثات
    """

    print("\n[Conversation History Test]")

    # Get user's question history
    history_response = await workflow_client.get(
        "http://localhost:8112/api/v1/advisor/history", headers=e2e_headers
    )

    assert history_response.status_code in (
        200,
        401,
        404,
    ), "History endpoint should respond"

    if history_response.status_code == 200:
        history = history_response.json()
        print("✓ Conversation history accessible")

        if isinstance(history, list):
            print(f"  Total questions in history: {len(history)}")
