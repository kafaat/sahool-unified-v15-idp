"""
Agricultural AI Model Connectors
=================================
موصلات نماذج الذكاء الاصطناعي الزراعي

Connectors for integrating with popular agricultural AI models.
Provides unified interface for different model APIs.

Philosophy:
- "让知识流动" (Let Knowledge Flow) - LLM consultants democratize agricultural expertise
- "让计算创造" (Let Computation Create) - Bio/remote sensing models enable precision agriculture
- Future: From "advice" to "Agent execution" - autonomous farm operations

Supported Models:
- ShengNong 3.0 (神农) - China Agricultural University
- CropWizard - NCSA/UIUC
- PlantGPT - South China Agricultural University
- Generic REST API connector for other models

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import abc
import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .models import AIModelInfo, ModelEndpoint

logger = logging.getLogger(__name__)


# ========================================================================
# Base Connector
# ========================================================================

@dataclass
class ConnectorResponse:
    """Response from a model connector.

    استجابة من موصل نموذج
    模型连接器响应
    """

    text: str
    model_id: str
    success: bool = True
    error: str | None = None
    tokens_used: int | None = None
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "model_id": self.model_id,
            "success": self.success,
            "error": self.error,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseConnector(abc.ABC):
    """Base class for model connectors.

    الفئة الأساسية لموصلات النماذج
    模型连接器基类
    """

    def __init__(self, model: AIModelInfo):
        """Initialize the connector.

        Args:
            model: Model information
        """
        self._model = model
        self._client: Any = None
        self._is_initialized = False

    @property
    def model_id(self) -> str:
        """Get the model ID."""
        return self._model.model_id

    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self._model.name

    async def initialize(self) -> None:
        """Initialize the connector."""
        if self._is_initialized:
            return
        await self._setup_client()
        self._is_initialized = True

    @abc.abstractmethod
    async def _setup_client(self) -> None:
        """Set up the HTTP client."""
        pass

    @abc.abstractmethod
    async def call(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call the model with a query.

        استدعاء النموذج باستعلام
        使用查询调用模型

        Args:
            query: Query/prompt to send
            context: Additional context

        Returns:
            Response dictionary with 'text' and optionally 'tokens_used'
        """
        pass

    async def is_available(self) -> bool:
        """Check if the model is available.

        التحقق مما إذا كان النموذج متاحا
        检查模型是否可用
        """
        try:
            await self.initialize()
            return True
        except Exception as e:
            logger.warning(f"Model {self.model_id} not available: {e}")
            return False

    async def close(self) -> None:
        """Close the connector and release resources."""
        if self._client and hasattr(self._client, "aclose"):
            await self._client.aclose()
        self._is_initialized = False


# ========================================================================
# ShengNong Connector (神农)
# ========================================================================

class ShengNongConnector(BaseConnector):
    """Connector for ShengNong 3.0 (神农) model.

    موصل لنموذج شينونغ 3.0
    神农3.0模型连接器

    ShengNong is a multimodal agricultural AI from China Agricultural University.
    Named after the legendary Chinese agricultural deity, it provides:
    - Crop disease diagnosis
    - Pest identification
    - Yield prediction
    - Expert agricultural consultation

    URL: https://shennong.cau.edu.cn/
    """

    DEFAULT_ENDPOINT = "https://shennong.cau.edu.cn/api/v1/chat"

    def __init__(self, model: AIModelInfo):
        super().__init__(model)
        self._api_key = os.getenv("SHENGNONG_API_KEY", "")
        self._endpoint = self._get_endpoint()

    def _get_endpoint(self) -> str:
        """Get the API endpoint."""
        if self._model.endpoint:
            return self._model.endpoint.url
        return self.DEFAULT_ENDPOINT

    async def _setup_client(self) -> None:
        """Set up the HTTP client."""
        try:
            import httpx
            self._client = httpx.AsyncClient(
                timeout=60.0,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        except ImportError:
            logger.warning("httpx not installed, using mock client")
            self._client = None

    async def call(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call ShengNong with a query.

        Args:
            query: Agricultural query in Chinese or English
            context: Additional context (crop type, location, etc.)

        Returns:
            Response dictionary
        """
        await self.initialize()

        start_time = time.time()
        context = context or {}

        # Build request payload
        payload = {
            "query": query,
            "language": context.get("language", "zh"),
            "crop_type": context.get("crop_type"),
            "location": context.get("location"),
            "include_images": context.get("include_images", False),
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        if not self._client:
            # Mock response for testing/development
            return self._mock_response(query, start_time)

        try:
            response = await self._client.post(
                self._endpoint,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "text": data.get("response", data.get("answer", str(data))),
                "tokens_used": data.get("usage", {}).get("total_tokens"),
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
            }

        except Exception as e:
            logger.error(f"ShengNong API error: {e}")
            return {
                "text": f"Error calling ShengNong: {e}",
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
                "error": str(e),
            }

    def _mock_response(self, query: str, start_time: float) -> dict[str, Any]:
        """Generate mock response for testing."""
        # Simple mock based on query content
        if "病" in query or "disease" in query.lower():
            response = (
                "根据您的描述,这可能是小麦锈病。建议:\n"
                "1. 及时喷施三唑酮等杀菌剂\n"
                "2. 加强田间通风\n"
                "3. 适当控制氮肥用量\n\n"
                "Based on your description, this may be wheat rust. Recommendations:\n"
                "1. Spray fungicides like triadimefon\n"
                "2. Improve field ventilation\n"
                "3. Control nitrogen fertilizer application"
            )
        elif "虫" in query or "pest" in query.lower():
            response = (
                "根据图片识别,这是蚜虫危害。防治建议:\n"
                "1. 使用吡虫啉等内吸性杀虫剂\n"
                "2. 保护天敌,如瓢虫\n"
                "3. 加强监测,早期防治"
            )
        else:
            response = (
                "感谢您的咨询。神农AI为您提供专业的农业建议。\n"
                "Thank you for your inquiry. ShengNong AI provides professional agricultural advice."
            )

        return {
            "text": response,
            "model_id": self.model_id,
            "latency_ms": (time.time() - start_time) * 1000,
            "mock": True,
        }


# ========================================================================
# CropWizard Connector
# ========================================================================

class CropWizardConnector(BaseConnector):
    """Connector for CropWizard model from NCSA/UIUC.

    موصل لنموذج كروب ويزارد
    CropWizard模型连接器

    CropWizard is an agricultural expert system powered by NCSA supercomputing.
    Provides expert-level crop advisory based on extensive agricultural knowledge.

    URL: https://uiuc.chat/cropwizard-1.5/chat
    """

    DEFAULT_ENDPOINT = "https://uiuc.chat/api/cropwizard/v1/chat"

    def __init__(self, model: AIModelInfo):
        super().__init__(model)
        self._api_key = os.getenv("CROPWIZARD_API_KEY", "")
        self._endpoint = self._get_endpoint()

    def _get_endpoint(self) -> str:
        """Get the API endpoint."""
        if self._model.endpoint:
            return self._model.endpoint.url
        return self.DEFAULT_ENDPOINT

    async def _setup_client(self) -> None:
        """Set up the HTTP client."""
        try:
            import httpx
            self._client = httpx.AsyncClient(
                timeout=60.0,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        except ImportError:
            logger.warning("httpx not installed, using mock client")
            self._client = None

    async def call(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call CropWizard with a query.

        Args:
            query: Agricultural query
            context: Additional context (crop, location, etc.)

        Returns:
            Response dictionary
        """
        await self.initialize()

        start_time = time.time()
        context = context or {}

        # Build request payload
        payload = {
            "message": query,
            "context": {
                "crop": context.get("crop_type"),
                "region": context.get("location"),
                "season": context.get("season"),
            },
            "stream": False,
        }

        if not self._client:
            return self._mock_response(query, start_time)

        try:
            response = await self._client.post(
                self._endpoint,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "text": data.get("response", data.get("message", str(data))),
                "tokens_used": data.get("tokens"),
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
            }

        except Exception as e:
            logger.error(f"CropWizard API error: {e}")
            return {
                "text": f"Error calling CropWizard: {e}",
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
                "error": str(e),
            }

    def _mock_response(self, query: str, start_time: float) -> dict[str, Any]:
        """Generate mock response for testing."""
        response = (
            "Based on my analysis of your agricultural query:\n\n"
            f"Query: {query[:100]}...\n\n"
            "Recommendation:\n"
            "1. Monitor soil moisture levels regularly\n"
            "2. Apply appropriate fertilizers based on soil tests\n"
            "3. Implement integrated pest management practices\n"
            "4. Consider crop rotation for sustainable yields\n\n"
            "For more detailed guidance, please provide specific crop and location information."
        )

        return {
            "text": response,
            "model_id": self.model_id,
            "latency_ms": (time.time() - start_time) * 1000,
            "mock": True,
        }


# ========================================================================
# PlantGPT Connector
# ========================================================================

class PlantGPTConnector(BaseConnector):
    """Connector for PlantGPT model from South China Agricultural University.

    موصل لنموذج بلانت جي بي تي
    PlantGPT模型连接器

    PlantGPT specializes in plant genomics and breeding assistance.
    Provides gene function analysis, breeding recommendations, and
    phenotype prediction capabilities.

    URL: https://www.plantgpt.icu
    """

    DEFAULT_ENDPOINT = "https://www.plantgpt.icu/api/v1/chat"

    def __init__(self, model: AIModelInfo):
        super().__init__(model)
        self._api_key = os.getenv("PLANTGPT_API_KEY", "")
        self._endpoint = self._get_endpoint()

    def _get_endpoint(self) -> str:
        """Get the API endpoint."""
        if self._model.endpoint:
            return self._model.endpoint.url
        return self.DEFAULT_ENDPOINT

    async def _setup_client(self) -> None:
        """Set up the HTTP client."""
        try:
            import httpx
            self._client = httpx.AsyncClient(
                timeout=90.0,  # Genomics queries may take longer
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        except ImportError:
            logger.warning("httpx not installed, using mock client")
            self._client = None

    async def call(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call PlantGPT with a query.

        Args:
            query: Plant genomics/breeding query
            context: Additional context (species, gene, etc.)

        Returns:
            Response dictionary
        """
        await self.initialize()

        start_time = time.time()
        context = context or {}

        # Build request payload
        payload = {
            "query": query,
            "species": context.get("species"),
            "gene_id": context.get("gene_id"),
            "task_type": context.get("task_type", "qa"),  # qa, gene_function, breeding
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        if not self._client:
            return self._mock_response(query, context, start_time)

        try:
            response = await self._client.post(
                self._endpoint,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "text": data.get("response", data.get("answer", str(data))),
                "tokens_used": data.get("usage", {}).get("total_tokens"),
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
                "gene_info": data.get("gene_info"),  # Additional genomics data
            }

        except Exception as e:
            logger.error(f"PlantGPT API error: {e}")
            return {
                "text": f"Error calling PlantGPT: {e}",
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
                "error": str(e),
            }

    def _mock_response(
        self,
        query: str,
        context: dict[str, Any],
        start_time: float,
    ) -> dict[str, Any]:
        """Generate mock response for testing."""
        task_type = context.get("task_type", "qa")

        if task_type == "gene_function":
            response = (
                "基因功能分析结果 | Gene Function Analysis:\n\n"
                "该基因编码一种转录因子,参与植物抗旱胁迫响应。\n"
                "This gene encodes a transcription factor involved in drought stress response.\n\n"
                "相关通路 | Related Pathways:\n"
                "- ABA signaling pathway\n"
                "- Osmotic stress response\n"
                "- Stomatal regulation"
            )
        elif task_type == "breeding":
            response = (
                "育种建议 | Breeding Recommendations:\n\n"
                "基于目标性状,建议采用以下育种策略:\n"
                "1. 利用分子标记辅助选择(MAS)\n"
                "2. 考虑导入抗病基因Yr15\n"
                "3. 注意保持产量相关QTL\n\n"
                "Recommended breeding strategies:\n"
                "1. Use marker-assisted selection (MAS)\n"
                "2. Consider introgressing disease resistance gene Yr15\n"
                "3. Maintain yield-related QTLs"
            )
        else:
            response = (
                "PlantGPT为您提供植物基因组学和育种咨询服务。\n"
                "PlantGPT provides plant genomics and breeding consultation.\n\n"
                f"您的查询: {query[:100]}...\n"
                "请提供更具体的基因或物种信息以获得详细分析。"
            )

        return {
            "text": response,
            "model_id": self.model_id,
            "latency_ms": (time.time() - start_time) * 1000,
            "mock": True,
        }


# ========================================================================
# Generic REST Connector
# ========================================================================

class GenericRESTConnector(BaseConnector):
    """Generic REST API connector for agricultural AI models.

    موصل REST API عام لنماذج الذكاء الاصطناعي الزراعي
    农业AI模型通用REST API连接器

    Provides a flexible connector for models with standard REST APIs.
    Supports various authentication methods and request formats.
    """

    def __init__(
        self,
        model: AIModelInfo,
        api_key_env: str | None = None,
    ):
        super().__init__(model)
        self._api_key = self._get_api_key(api_key_env)
        self._endpoint = self._get_endpoint()

    def _get_api_key(self, api_key_env: str | None) -> str:
        """Get API key from environment."""
        if api_key_env:
            return os.getenv(api_key_env, "")

        # Try common patterns
        model_upper = self._model.model_id.upper().replace("-", "_")
        for pattern in [
            f"{model_upper}_API_KEY",
            f"{model_upper}_KEY",
            f"AI_{model_upper}_KEY",
        ]:
            key = os.getenv(pattern)
            if key:
                return key

        return ""

    def _get_endpoint(self) -> str:
        """Get the API endpoint."""
        if self._model.endpoint:
            return self._model.endpoint.url
        if self._model.url:
            # Try to construct API endpoint from URL
            base_url = self._model.url.rstrip("/")
            return f"{base_url}/api/v1/chat"
        return ""

    async def _setup_client(self) -> None:
        """Set up the HTTP client."""
        try:
            import httpx

            headers = {"Content-Type": "application/json"}

            # Add authentication header based on endpoint config
            if self._model.endpoint:
                auth_type = self._model.endpoint.auth_type
                if auth_type == "api_key" and self._api_key:
                    headers["Authorization"] = f"Bearer {self._api_key}"
                elif auth_type == "basic" and self._api_key:
                    import base64
                    encoded = base64.b64encode(self._api_key.encode()).decode()
                    headers["Authorization"] = f"Basic {encoded}"

            timeout = 60.0
            if self._model.endpoint:
                timeout = self._model.endpoint.timeout_seconds

            self._client = httpx.AsyncClient(
                timeout=timeout,
                headers=headers,
            )
        except ImportError:
            logger.warning("httpx not installed, using mock client")
            self._client = None

    async def call(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call the model with a query.

        Args:
            query: Query/prompt to send
            context: Additional context

        Returns:
            Response dictionary
        """
        await self.initialize()

        start_time = time.time()
        context = context or {}

        if not self._endpoint:
            return {
                "text": f"No endpoint configured for model {self.model_id}",
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
                "error": "No endpoint",
            }

        # Build generic request payload
        payload = {
            "query": query,
            "prompt": query,  # Some APIs use 'prompt'
            "message": query,  # Some APIs use 'message'
            "context": context,
        }

        if not self._client:
            return self._mock_response(query, start_time)

        try:
            response = await self._client.post(
                self._endpoint,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            # Try to extract response from various formats
            text = (
                data.get("response") or
                data.get("answer") or
                data.get("message") or
                data.get("text") or
                data.get("content") or
                str(data)
            )

            return {
                "text": text,
                "tokens_used": data.get("usage", {}).get("total_tokens"),
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
                "raw_response": data,
            }

        except Exception as e:
            logger.error(f"REST API error for {self.model_id}: {e}")
            return {
                "text": f"Error calling {self.model_name}: {e}",
                "model_id": self.model_id,
                "latency_ms": (time.time() - start_time) * 1000,
                "error": str(e),
            }

    def _mock_response(self, query: str, start_time: float) -> dict[str, Any]:
        """Generate mock response for testing."""
        return {
            "text": (
                f"Mock response from {self.model_name}:\n\n"
                f"Query received: {query[:100]}...\n\n"
                "This is a simulated response for development/testing purposes. "
                "Configure the API key and endpoint for actual model responses."
            ),
            "model_id": self.model_id,
            "latency_ms": (time.time() - start_time) * 1000,
            "mock": True,
        }


# ========================================================================
# AgroGPT Connector (MBZUAI - Arabic Support)
# ========================================================================

class AgroGPTConnector(BaseConnector):
    """Connector for AgroGPT model from MBZUAI.

    موصل لنموذج أجرو جي بي تي من جامعة محمد بن زايد للذكاء الاصطناعي
    来自MBZUAI的AgroGPT模型连接器

    AgroGPT is a vision-language model for agricultural applications
    with Arabic language support, developed by MBZUAI in UAE.

    GitHub: https://github.com/awaisrauf/agroGPT
    """

    def __init__(self, model: AIModelInfo):
        super().__init__(model)
        self._api_key = os.getenv("AGROGPT_API_KEY", "")

    async def _setup_client(self) -> None:
        """Set up the HTTP client."""
        try:
            import httpx
            self._client = httpx.AsyncClient(
                timeout=90.0,  # VLM may take longer
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        except ImportError:
            self._client = None

    async def call(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call AgroGPT with a query.

        Args:
            query: Agricultural query (supports Arabic and English)
            context: Additional context including optional image_url

        Returns:
            Response dictionary
        """
        await self.initialize()

        start_time = time.time()
        context = context or {}

        # Build payload with optional image
        payload = {
            "query": query,
            "language": context.get("language", "en"),
        }

        if context.get("image_url"):
            payload["image_url"] = context["image_url"]

        if context.get("image_base64"):
            payload["image"] = context["image_base64"]

        if not self._client:
            return self._mock_response(query, context, start_time)

        # Mock response for now (actual implementation would call the API)
        return self._mock_response(query, context, start_time)

    def _mock_response(
        self,
        query: str,
        context: dict[str, Any],
        start_time: float,
    ) -> dict[str, Any]:
        """Generate mock response for testing."""
        lang = context.get("language", "en")

        if lang == "ar":
            response = (
                "تحليل الصورة الزراعية:\n\n"
                f"الاستعلام: {query[:100]}...\n\n"
                "النتائج:\n"
                "- تم التعرف على المحصول: قمح\n"
                "- الحالة الصحية: جيدة\n"
                "- التوصيات: الاستمرار في برنامج الري الحالي\n"
            )
        else:
            response = (
                "Agricultural Image Analysis:\n\n"
                f"Query: {query[:100]}...\n\n"
                "Results:\n"
                "- Crop identified: Wheat\n"
                "- Health status: Good\n"
                "- Recommendations: Continue current irrigation program\n"
            )

        return {
            "text": response,
            "model_id": self.model_id,
            "latency_ms": (time.time() - start_time) * 1000,
            "mock": True,
        }


# ========================================================================
# Factory Functions
# ========================================================================

def create_connector(model: AIModelInfo) -> BaseConnector:
    """Create an appropriate connector for a model.

    إنشاء موصل مناسب لنموذج
    为模型创建适当的连接器

    Args:
        model: Model information

    Returns:
        Appropriate connector instance
    """
    # Model-specific connectors
    connector_map = {
        "shengnong": ShengNongConnector,
        "cropwizard": CropWizardConnector,
        "plantgpt": PlantGPTConnector,
        "agrogpt": AgroGPTConnector,
    }

    connector_class = connector_map.get(model.model_id, GenericRESTConnector)
    return connector_class(model)


def get_available_connectors() -> list[str]:
    """Get list of models with dedicated connectors.

    الحصول على قائمة النماذج ذات الموصلات المخصصة
    获取具有专用连接器的模型列表
    """
    return [
        "shengnong",    # ShengNong 3.0 (神农)
        "cropwizard",   # CropWizard (NCSA)
        "plantgpt",     # PlantGPT
        "agrogpt",      # AgroGPT (MBZUAI)
    ]
