"""
Agricultural AI Models
النماذج الزراعية للذكاء الاصطناعي

Provides:
- AgriGuardScorer: rules-based crop health scoring from spectral indices
  (always available, no downloads — inspired by github.com/debanjan06/Agriguard)
- Optional HuggingFace model wrappers (loaded only when env vars are set)
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# ── AgriGuard-inspired rules-based scorer ────────────────────────────────────


class AgriGuardScorer:
    """
    Rules-based crop health classifier using spectral indices.
    Inspired by the AgriGuard PyTorch model (399K params) but implemented as
    a deterministic rules engine so it works without GPU or model downloads.

    Inputs : NDVI, NDRE, NDMI, EVI2 (any subset)
    Outputs: health_class ("healthy" | "stressed" | "diseased"), confidence (0–1)
    """

    def score(
        self,
        ndvi: float | None = None,
        ndre: float | None = None,
        ndmi: float | None = None,
        evi2: float | None = None,
        temperature: float | None = None,
        humidity: float | None = None,
    ) -> tuple[str, float]:
        if ndvi is None:
            return "unknown", 0.0

        weighted_score = 0.0
        weight_sum = 0.0

        # NDVI — overall greenness (weight 0.40)
        if ndvi is not None:
            if ndvi >= 0.60:
                weighted_score += 0.40 * 1.00
            elif ndvi >= 0.40:
                weighted_score += 0.40 * 0.70
            elif ndvi >= 0.20:
                weighted_score += 0.40 * 0.35
            else:
                weighted_score += 0.40 * 0.05
            weight_sum += 0.40

        # NDRE — chlorophyll & nitrogen status (weight 0.25)
        if ndre is not None:
            if ndre >= 0.20:
                weighted_score += 0.25 * 1.00
            elif ndre >= 0.10:
                weighted_score += 0.25 * 0.60
            else:
                weighted_score += 0.25 * 0.20
            weight_sum += 0.25

        # NDMI — water content / irrigation need (weight 0.25)
        if ndmi is not None:
            if ndmi >= 0.00:
                weighted_score += 0.25 * 1.00
            elif ndmi >= -0.20:
                weighted_score += 0.25 * 0.50
            else:
                weighted_score += 0.25 * 0.10
            weight_sum += 0.25

        # EVI2 — dense canopy performance (weight 0.10)
        if evi2 is not None:
            if evi2 >= 0.40:
                weighted_score += 0.10 * 1.00
            elif evi2 >= 0.20:
                weighted_score += 0.10 * 0.55
            else:
                weighted_score += 0.10 * 0.10
            weight_sum += 0.10

        if weight_sum == 0.0:
            return "unknown", 0.0

        normalised = weighted_score / weight_sum

        # Confidence grows with number of indices available
        index_coverage = weight_sum  # max 1.0 when all 4 present
        confidence = round(min(0.95, index_coverage * normalised + 0.05), 2)

        if normalised >= 0.65:
            return "healthy", confidence
        elif normalised >= 0.33:
            return "stressed", confidence
        else:
            return "diseased", confidence

    def interpret_index(self, name: str, value: float | None) -> str:
        """Return a one-line Arabic interpretation for a single index value."""
        if value is None:
            return "غير متوفر"
        name = name.upper()
        if name == "NDVI":
            if value >= 0.6:
                return f"NDVI = {value:.3f} — غطاء نباتي صحي ممتاز"
            elif value >= 0.4:
                return f"NDVI = {value:.3f} — غطاء نباتي متوسط، مراقبة مستحسنة"
            elif value >= 0.2:
                return f"NDVI = {value:.3f} — نبات مجهد، تدخل مطلوب"
            else:
                return f"NDVI = {value:.3f} — غطاء ضعيف جداً أو تربة عارية"
        elif name == "NDRE":
            if value >= 0.2:
                return f"NDRE = {value:.3f} — مستوى الكلوروفيل والنيتروجين جيد"
            elif value >= 0.1:
                return f"NDRE = {value:.3f} — نقص طفيف في النيتروجين"
            else:
                return f"NDRE = {value:.3f} — نقص حاد في النيتروجين/الكلوروفيل"
        elif name == "NDMI":
            if value >= 0.0:
                return f"NDMI = {value:.3f} — محتوى الرطوبة في النبات كافٍ"
            elif value >= -0.2:
                return f"NDMI = {value:.3f} — إجهاد مائي معتدل، يُنصح بالري"
            else:
                return f"NDMI = {value:.3f} — إجهاد مائي شديد، ري عاجل مطلوب"
        elif name == "EVI2":
            if value >= 0.4:
                return f"EVI2 = {value:.3f} — كثافة المحصول ممتازة"
            elif value >= 0.2:
                return f"EVI2 = {value:.3f} — كثافة متوسطة"
            else:
                return f"EVI2 = {value:.3f} — كثافة المحصول منخفضة"
        elif name in ("GNDVI",):
            return f"GNDVI = {value:.3f} — مؤشر الكلوروفيل الأخضر"
        elif name == "MSI":
            if value <= 0.4:
                return f"MSI = {value:.3f} — رطوبة النبات عالية"
            elif value <= 1.0:
                return f"MSI = {value:.3f} — رطوبة طبيعية"
            else:
                return f"MSI = {value:.3f} — إجهاد رطوبي"
        elif name == "LAI":
            if value >= 3.0:
                return f"LAI = {value:.2f} م²/م² — مساحة ورقية جيدة"
            elif value >= 1.0:
                return f"LAI = {value:.2f} م²/م² — مساحة ورقية متوسطة"
            else:
                return f"LAI = {value:.2f} م²/م² — مساحة ورقية ضعيفة"
        return f"{name} = {value:.3f}"


# ── Optional HuggingFace model wrappers ───────────────────────────────────────


class HFAdvisorModel:
    """
    Wrapper for a local 7B agricultural LLM (CropSeek-LLM or aksara_v1).
    Only instantiated when CROP_ADVISOR_MODEL env var is set and
    transformers + torch are installed.

    Falls back gracefully — callers must check .is_available() before use.
    """

    def __init__(self) -> None:
        self._pipe: Any = None
        self._loaded = False
        self._model_name = os.environ.get("CROP_ADVISOR_MODEL", "")

    def is_available(self) -> bool:
        return bool(self._model_name) and self._loaded

    def load(self) -> bool:
        if not self._model_name:
            return False
        if self._loaded:
            return True
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

            hf_home = os.environ.get("HF_HOME", "/app/models")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info("Loading agricultural LLM: %s on %s", self._model_name, device)

            tokenizer = AutoTokenizer.from_pretrained(self._model_name, cache_dir=hf_home)
            model = AutoModelForCausalLM.from_pretrained(
                self._model_name,
                cache_dir=hf_home,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
            self._pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                do_sample=False,
            )
            self._loaded = True
            logger.info("Agricultural LLM loaded successfully: %s", self._model_name)
            return True
        except Exception as exc:
            logger.warning("Could not load agricultural LLM (%s): %s", self._model_name, exc)
            return False

    def generate(self, prompt: str) -> str | None:
        if not self._pipe:
            return None
        try:
            output = self._pipe(prompt)
            return output[0]["generated_text"][len(prompt) :].strip()
        except Exception as exc:
            logger.warning("HF model inference failed: %s", exc)
            return None


class NLLBTranslator:
    """
    Wrapper for facebook/nllb-200-distilled-600M Arabic translation.
    Only loaded when TRANSLATION_MODEL env var is set.
    Falls back gracefully — callers should check .is_available().
    """

    def __init__(self) -> None:
        self._pipe: Any = None
        self._loaded = False
        self._model_name = os.environ.get("TRANSLATION_MODEL", "")

    def is_available(self) -> bool:
        return bool(self._model_name) and self._loaded

    def load(self) -> bool:
        if not self._model_name:
            return False
        if self._loaded:
            return True
        try:
            import torch
            from transformers import pipeline as hf_pipeline

            hf_home = os.environ.get("HF_HOME", "/app/models")
            device = 0 if __import__("torch").cuda.is_available() else -1
            logger.info("Loading NLLB translation model: %s", self._model_name)
            self._pipe = hf_pipeline(
                "translation",
                model=self._model_name,
                src_lang="eng_Latn",
                tgt_lang="arb_Arab",
                cache_dir=hf_home,
                device=device,
                max_length=512,
            )
            self._loaded = True
            logger.info("NLLB translation model loaded")
            return True
        except Exception as exc:
            logger.warning("Could not load NLLB translator (%s): %s", self._model_name, exc)
            return False

    def translate(self, text: str) -> str | None:
        if not self._pipe:
            return None
        try:
            result = self._pipe(text)
            return result[0]["translation_text"]
        except Exception as exc:
            logger.warning("NLLB translation failed: %s", exc)
            return None
