#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - AI Agents Simulator
محاكي وكلاء الذكاء الاصطناعي لمنصة سهول
═══════════════════════════════════════════════════════════════════════════════════════

This simulator tests all AI agents:
- Field Analyst Agent (محلل الحقول)
- Disease Expert Agent (خبير الأمراض)
- Irrigation Advisor Agent (مستشار الري)
- Yield Predictor Agent (متنبئ المحصول)
- Supervisor/Orchestrator (المشرف/المنسق)

Usage:
    python agents_simulator.py --duration 300 --users 20 --gateway http://localhost:8081

═══════════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import aiohttp
import argparse
import random
import time
import json
import uuid
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sahool-agents-simulator")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SAUDI_LOCATIONS = [
    {"name": "Al-Kharj", "lat": 24.1500, "lng": 47.3000, "region": "Riyadh"},
    {"name": "Al-Ahsa", "lat": 25.3800, "lng": 49.5900, "region": "Eastern"},
    {"name": "Tabuk", "lat": 28.3838, "lng": 36.5550, "region": "Tabuk"},
    {"name": "Wadi Al-Dawasir", "lat": 20.4910, "lng": 44.7800, "region": "Riyadh"},
    {"name": "Jizan", "lat": 16.8892, "lng": 42.5511, "region": "Jizan"},
]

CROP_TYPES = ["wheat", "barley", "dates", "tomatoes", "cucumbers", "alfalfa"]
GROWTH_STAGES = ["seedling", "vegetative", "flowering", "fruiting", "mature", "harvest"]
SOIL_TYPES = ["sandy", "clay", "loam", "silt", "sandy_loam"]

DISEASE_SYMPTOMS = {
    "ar": [
        "اصفرار الأوراق",
        "ذبول النبات",
        "بقع بنية على الأوراق",
        "تقزم النمو",
        "تجعد الأوراق",
        "تعفن الجذور",
        "بقع سوداء",
        "نقاط بيضاء",
    ],
    "en": [
        "yellow leaves",
        "wilting",
        "brown spots on leaves",
        "stunted growth",
        "leaf curling",
        "root rot",
        "black spots",
        "white patches",
    ]
}

FARMER_QUESTIONS = {
    "ar": [
        "ما هو أفضل وقت لري القمح في فصل الصيف؟",
        "كيف أعالج اصفرار أوراق الطماطم؟",
        "ما هي كمية السماد المناسبة للنخيل؟",
        "متى يجب حصاد الشعير؟",
        "كيف أحمي المحاصيل من الحرارة العالية؟",
        "ما هي علامات نقص النيتروجين؟",
        "كيف أحسن جودة التربة الرملية؟",
        "ما أفضل نظام ري للبيوت المحمية؟",
        "كيف أكتشف الإصابة بالآفات مبكراً؟",
        "ما هي أفضل الأصناف للزراعة في تبوك؟",
    ],
    "en": [
        "What is the best time to irrigate wheat in summer?",
        "How do I treat yellowing tomato leaves?",
        "What is the appropriate fertilizer amount for palm trees?",
        "When should barley be harvested?",
        "How do I protect crops from high temperatures?",
        "What are the signs of nitrogen deficiency?",
        "How can I improve sandy soil quality?",
        "What is the best irrigation system for greenhouses?",
        "How to detect pest infection early?",
        "What are the best varieties to grow in Tabuk?",
    ]
}

# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentStats:
    requests: int = 0
    success: int = 0
    failed: int = 0
    total_latency_ms: float = 0.0
    total_tokens: int = 0

    @property
    def success_rate(self) -> float:
        return (self.success / self.requests * 100) if self.requests > 0 else 0.0

    @property
    def avg_latency(self) -> float:
        return (self.total_latency_ms / self.success) if self.success > 0 else 0.0

@dataclass
class SimulatorStats:
    start_time: float = field(default_factory=time.time)
    agents: Dict[str, AgentStats] = field(default_factory=dict)

    def get_agent(self, name: str) -> AgentStats:
        if name not in self.agents:
            self.agents[name] = AgentStats()
        return self.agents[name]

    def record(self, agent: str, success: bool, latency_ms: float, tokens: int = 0):
        stats = self.get_agent(agent)
        stats.requests += 1
        if success:
            stats.success += 1
            stats.total_latency_ms += latency_ms
            stats.total_tokens += tokens
        else:
            stats.failed += 1

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT SIMULATORS
# ═══════════════════════════════════════════════════════════════════════════════

class AIAgentSimulator:
    """Base class for AI agent simulators."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, stats: SimulatorStats):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.stats = stats
        self.token: Optional[str] = None

    @property
    def headers(self) -> Dict[str, str]:
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Request-ID": str(uuid.uuid4()),
            "X-Tenant-ID": "tenant-001",
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def request(self, method: str, path: str, agent_name: str, **kwargs) -> tuple[bool, Any]:
        url = f"{self.base_url}{path}"
        start = time.time()

        try:
            async with self.session.request(
                method, url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=60),  # Longer timeout for AI
                **kwargs
            ) as response:
                latency = (time.time() - start) * 1000
                success = response.status in [200, 201, 202, 204, 404]

                try:
                    data = await response.json()
                    tokens = data.get("usage", {}).get("total_tokens", 0) if isinstance(data, dict) else 0
                except:
                    data = await response.text()
                    tokens = 0

                self.stats.record(agent_name, success, latency, tokens)

                if not success:
                    logger.warning(f"{agent_name}: {method} {path} -> {response.status}")

                return success, data

        except asyncio.TimeoutError:
            self.stats.record(agent_name, False, 60000)
            logger.warning(f"{agent_name}: {method} {path} -> Timeout")
            return False, None
        except Exception as e:
            self.stats.record(agent_name, False, 0)
            logger.warning(f"{agent_name}: {method} {path} -> {e}")
            return False, None

    # ═══════════════════════════════════════════════════════════════════════════
    # SUPERVISOR AGENT (المشرف)
    # ═══════════════════════════════════════════════════════════════════════════

    async def ask_supervisor(self):
        """Ask a general question to the AI supervisor."""
        lang = random.choice(["ar", "en"])
        question = random.choice(FARMER_QUESTIONS[lang])

        return await self.request("POST", "/api/advisor/ask", "supervisor", json={
            "question": question,
            "language": lang,
            "context": {
                "region": random.choice(SAUDI_LOCATIONS)["region"],
                "crop_type": random.choice(CROP_TYPES),
                "season": random.choice(["spring", "summer", "fall", "winter"]),
            }
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # FIELD ANALYST AGENT (محلل الحقول)
    # ═══════════════════════════════════════════════════════════════════════════

    async def analyze_field(self):
        """Request comprehensive field analysis."""
        field_id = f"field-{random.randint(1, 50)}"

        return await self.request("POST", "/api/advisor/analyze-field", "field_analyst", json={
            "field_id": field_id,
            "crop_type": random.choice(CROP_TYPES),
            "include_disease_check": True,
            "include_irrigation": True,
            "include_yield_prediction": True,
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # DISEASE EXPERT AGENT (خبير الأمراض)
    # ═══════════════════════════════════════════════════════════════════════════

    async def diagnose_disease(self):
        """Request disease diagnosis."""
        lang = random.choice(["ar", "en"])
        symptoms = random.sample(DISEASE_SYMPTOMS[lang], random.randint(2, 4))
        location = random.choice(SAUDI_LOCATIONS)

        return await self.request("POST", "/api/advisor/diagnose", "disease_expert", json={
            "crop_type": random.choice(CROP_TYPES),
            "symptoms": {
                "visual": symptoms,
                "severity": random.choice(["mild", "moderate", "severe"]),
                "spread_pattern": random.choice(["localized", "scattered", "widespread"]),
                "affected_parts": random.sample(["leaves", "stems", "roots", "fruits", "flowers"], random.randint(1, 3)),
            },
            "image_path": None,  # No image in simulation
            "location": location["name"],
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # IRRIGATION ADVISOR AGENT (مستشار الري)
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_irrigation_advice(self):
        """Request irrigation recommendations."""
        location = random.choice(SAUDI_LOCATIONS)

        return await self.request("POST", "/api/advisor/recommend", "irrigation_advisor", json={
            "crop_type": random.choice(CROP_TYPES),
            "growth_stage": random.choice(GROWTH_STAGES),
            "recommendation_type": "irrigation",
            "field_data": {
                "soil": {
                    "type": random.choice(SOIL_TYPES),
                    "moisture": random.uniform(15, 60),
                    "temperature": random.uniform(15, 40),
                    "depth_cm": random.choice([20, 40, 60]),
                },
                "weather": {
                    "temperature": random.uniform(20, 50),
                    "humidity": random.uniform(10, 60),
                    "wind_speed": random.uniform(0, 20),
                    "evapotranspiration": random.uniform(3, 10),
                },
                "location": {
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "region": location["region"],
                },
                "irrigation_system": random.choice(["drip", "sprinkler", "flood", "center_pivot"]),
            }
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # YIELD PREDICTOR AGENT (متنبئ المحصول)
    # ═══════════════════════════════════════════════════════════════════════════

    async def predict_yield(self):
        """Request yield prediction."""
        location = random.choice(SAUDI_LOCATIONS)
        crop = random.choice(CROP_TYPES)

        return await self.request("POST", "/api/advisor/recommend", "yield_predictor", json={
            "crop_type": crop,
            "growth_stage": random.choice(GROWTH_STAGES),
            "recommendation_type": "yield",
            "field_data": {
                "area_hectares": random.uniform(1, 100),
                "planting_date": (datetime.now() - timedelta(days=random.randint(30, 120))).strftime("%Y-%m-%d"),
                "variety": f"{crop}_variety_{random.randint(1, 5)}",
                "soil": {
                    "type": random.choice(SOIL_TYPES),
                    "quality_score": random.uniform(0.5, 1.0),
                },
                "historical_yield": random.uniform(2, 10),  # tons/hectare
                "ndvi_current": random.uniform(0.3, 0.8),
                "weather_forecast": {
                    "avg_temperature": random.uniform(25, 40),
                    "expected_rainfall_mm": random.uniform(0, 50),
                },
            }
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # FERTILIZER ADVISOR (مستشار التسميد)
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_fertilizer_advice(self):
        """Request fertilizer recommendations."""
        return await self.request("POST", "/api/advisor/recommend", "fertilizer_advisor", json={
            "crop_type": random.choice(CROP_TYPES),
            "growth_stage": random.choice(GROWTH_STAGES),
            "recommendation_type": "fertilizer",
            "field_data": {
                "soil_analysis": {
                    "nitrogen": random.uniform(10, 100),
                    "phosphorus": random.uniform(5, 50),
                    "potassium": random.uniform(50, 200),
                    "ph": random.uniform(5.5, 8.0),
                    "organic_matter": random.uniform(0.5, 5),
                },
                "previous_crop": random.choice(CROP_TYPES + [None]),
                "target_yield": random.uniform(3, 12),  # tons/hectare
            }
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # PEST CONTROL ADVISOR (مستشار مكافحة الآفات)
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_pest_advice(self):
        """Request pest control recommendations."""
        location = random.choice(SAUDI_LOCATIONS)

        return await self.request("POST", "/api/advisor/recommend", "pest_advisor", json={
            "crop_type": random.choice(CROP_TYPES),
            "growth_stage": random.choice(GROWTH_STAGES),
            "recommendation_type": "pest",
            "field_data": {
                "pest_type": random.choice(["aphids", "whitefly", "spider_mites", "locusts", "borers"]),
                "infestation_level": random.choice(["low", "medium", "high"]),
                "location": location["region"],
                "organic_only": random.choice([True, False]),
            }
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # RAG KNOWLEDGE RETRIEVAL
    # ═══════════════════════════════════════════════════════════════════════════

    async def query_knowledge_base(self):
        """Query the RAG knowledge base."""
        queries = [
            "best practices for wheat irrigation in Saudi Arabia",
            "common tomato diseases in hot climates",
            "organic pest control methods for date palms",
            "soil preparation for greenhouse cultivation",
            "water conservation techniques in arid regions",
            "مكافحة الآفات بطرق عضوية",
            "تحسين جودة التربة الرملية",
            "أفضل أوقات الري في الصيف",
        ]

        return await self.request("POST", "/api/advisor/knowledge/search", "rag_retriever", json={
            "query": random.choice(queries),
            "top_k": random.randint(3, 10),
            "language": random.choice(["ar", "en"]),
            "filters": {
                "category": random.choice(["irrigation", "pest_control", "fertilization", "diseases", None]),
                "region": random.choice([loc["region"] for loc in SAUDI_LOCATIONS] + [None]),
            }
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # AGENT INFO ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    async def list_agents(self):
        """List available AI agents."""
        return await self.request("GET", "/api/advisor/agents", "system")

    async def list_tools(self):
        """List available external tools."""
        return await self.request("GET", "/api/advisor/tools", "system")

    async def get_rag_info(self):
        """Get RAG system information."""
        return await self.request("GET", "/api/advisor/rag/info", "system")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class AgentsSimulator:
    """Main simulator for AI agents."""

    AGENT_METHODS = [
        ("ask_supervisor", 0.25),          # General questions - 25%
        ("analyze_field", 0.15),           # Field analysis - 15%
        ("diagnose_disease", 0.15),        # Disease diagnosis - 15%
        ("get_irrigation_advice", 0.15),   # Irrigation - 15%
        ("predict_yield", 0.10),           # Yield prediction - 10%
        ("get_fertilizer_advice", 0.10),   # Fertilizer - 10%
        ("get_pest_advice", 0.05),         # Pest control - 5%
        ("query_knowledge_base", 0.05),    # RAG queries - 5%
    ]

    def __init__(self, gateway_url: str, num_users: int, duration_seconds: int):
        self.gateway_url = gateway_url
        self.num_users = num_users
        self.duration_seconds = duration_seconds
        self.stats = SimulatorStats()
        self.running = False

    def _select_method(self) -> str:
        """Select a method based on weighted distribution."""
        rand = random.random()
        cumulative = 0
        for method, weight in self.AGENT_METHODS:
            cumulative += weight
            if rand <= cumulative:
                return method
        return self.AGENT_METHODS[0][0]

    async def user_session(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate a single user session with AI agents."""
        simulator = AIAgentSimulator(session, self.gateway_url, self.stats)

        while self.running:
            method_name = self._select_method()
            method = getattr(simulator, method_name)

            try:
                await method()
            except Exception as e:
                logger.error(f"User {user_id}: Error in {method_name}: {e}")

            # Longer delay for AI requests (they're more expensive)
            await asyncio.sleep(random.uniform(2, 8))

    async def run(self):
        """Run the agents simulation."""
        self.running = True

        logger.info("=" * 80)
        logger.info("  SAHOOL IDP - AI Agents Simulator")
        logger.info("  محاكي وكلاء الذكاء الاصطناعي لمنصة سهول")
        logger.info("=" * 80)
        logger.info(f"  Gateway URL:     {self.gateway_url}")
        logger.info(f"  Virtual Users:   {self.num_users}")
        logger.info(f"  Duration:        {self.duration_seconds}s")
        logger.info("=" * 80)
        logger.info("")
        logger.info("  AI Agents being simulated:")
        logger.info("    - Supervisor Agent (المشرف)")
        logger.info("    - Field Analyst Agent (محلل الحقول)")
        logger.info("    - Disease Expert Agent (خبير الأمراض)")
        logger.info("    - Irrigation Advisor Agent (مستشار الري)")
        logger.info("    - Yield Predictor Agent (متنبئ المحصول)")
        logger.info("    - Fertilizer Advisor (مستشار التسميد)")
        logger.info("    - Pest Control Advisor (مستشار مكافحة الآفات)")
        logger.info("    - RAG Knowledge Retriever (مسترجع المعرفة)")
        logger.info("")
        logger.info("=" * 80)

        async with aiohttp.ClientSession() as session:
            # Get agent info first
            simulator = AIAgentSimulator(session, self.gateway_url, self.stats)
            await simulator.list_agents()
            await simulator.list_tools()
            await simulator.get_rag_info()

            # Create user tasks
            tasks = [
                asyncio.create_task(self.user_session(session, i))
                for i in range(self.num_users)
            ]

            # Run for specified duration
            await asyncio.sleep(self.duration_seconds)
            self.running = False

            # Cancel all tasks
            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

        self.print_results()
        self.save_results()

    def print_results(self):
        """Print simulation results."""
        duration = time.time() - self.stats.start_time

        logger.info("")
        logger.info("=" * 80)
        logger.info("  AI AGENTS SIMULATION RESULTS - نتائج محاكاة الوكلاء")
        logger.info("=" * 80)
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info("")
        logger.info("  Agent Results:")
        logger.info("  " + "-" * 76)
        logger.info(f"  {'Agent':<25} {'Requests':>10} {'Success':>10} {'Failed':>10} {'Rate':>10} {'Avg Latency':>12}")
        logger.info("  " + "-" * 76)

        total_requests = 0
        total_success = 0
        total_failed = 0

        for name, stats in sorted(self.stats.agents.items()):
            total_requests += stats.requests
            total_success += stats.success
            total_failed += stats.failed

            logger.info(
                f"  {name:<25} {stats.requests:>10} {stats.success:>10} {stats.failed:>10} "
                f"{stats.success_rate:>9.1f}% {stats.avg_latency:>10.1f}ms"
            )

        logger.info("  " + "-" * 76)
        overall_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
        logger.info(f"  {'TOTAL':<25} {total_requests:>10} {total_success:>10} {total_failed:>10} {overall_rate:>9.1f}%")
        logger.info("=" * 80)

    def save_results(self):
        """Save results to JSON file."""
        duration = time.time() - self.stats.start_time

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "gateway_url": self.gateway_url,
                "num_users": self.num_users,
                "duration_seconds": self.duration_seconds,
            },
            "duration_actual": duration,
            "agents": {
                name: {
                    "requests": stats.requests,
                    "success": stats.success,
                    "failed": stats.failed,
                    "success_rate": stats.success_rate,
                    "avg_latency_ms": stats.avg_latency,
                    "total_tokens": stats.total_tokens,
                }
                for name, stats in self.stats.agents.items()
            },
            "totals": {
                "requests": sum(s.requests for s in self.stats.agents.values()),
                "success": sum(s.success for s in self.stats.agents.values()),
                "failed": sum(s.failed for s in self.stats.agents.values()),
                "total_tokens": sum(s.total_tokens for s in self.stats.agents.values()),
            }
        }

        filename = f"agents_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"  Results saved to: {filename}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL IDP - AI Agents Simulator"
    )
    parser.add_argument(
        "--gateway", "-g",
        default="http://localhost:8081",
        help="Kong Gateway URL (default: http://localhost:8081)"
    )
    parser.add_argument(
        "--users", "-u",
        type=int,
        default=5,
        help="Number of virtual users (default: 5)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=60,
        help="Duration in seconds (default: 60)"
    )

    args = parser.parse_args()

    simulator = AgentsSimulator(
        gateway_url=args.gateway,
        num_users=args.users,
        duration_seconds=args.duration
    )

    try:
        asyncio.run(simulator.run())
    except KeyboardInterrupt:
        logger.info("\nSimulation stopped by user")

if __name__ == "__main__":
    main()
