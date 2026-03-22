"""
Tests for Model Training Module
===============================
اختبارات وحدة تدريب النماذج

Tests for dataset creation, training jobs, and model evaluation.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import json
import os
import tempfile
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Skip all tests if httpx is not available
pytest.importorskip("httpx")

from shared.ai.model_training import (
    DatasetBuilder,
    DatasetType,
    EvaluationResult,
    ModelTrainer,
    TrainingConfig,
    TrainingDataset,
    TrainingExample,
    TrainingJob,
    TrainingStatus,
    create_code_fix_dataset,
)


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_training_example():
    """Create a sample training example."""
    return TrainingExample(
        id=str(uuid.uuid4()),
        prompt="Fix the following Python code:\n```python\nx= 1\n```",
        completion="x = 1",
        language="python",
        category="code_fix",
        metadata={"rule_id": "E225"},
    )


@pytest.fixture
def sample_dataset(sample_training_example):
    """Create a sample training dataset."""
    return TrainingDataset(
        id=str(uuid.uuid4()),
        name="test-dataset",
        name_ar="مجموعة اختبار",
        description="Test dataset",
        description_ar="مجموعة بيانات اختبارية",
        dataset_type=DatasetType.CODE_FIX,
        examples=[sample_training_example],
    )


@pytest.fixture
def sample_config():
    """Create a sample training configuration."""
    return TrainingConfig(
        base_model="codellama:7b",
        output_model="test-model:latest",
        epochs=1,
        batch_size=2,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test Training Example
# ═══════════════════════════════════════════════════════════════════════════


class TestTrainingExample:
    """Tests for TrainingExample class."""

    def test_example_creation(self, sample_training_example):
        """Test TrainingExample creation."""
        assert sample_training_example.language == "python"
        assert sample_training_example.category == "code_fix"
        assert "rule_id" in sample_training_example.metadata

    def test_example_to_dict(self, sample_training_example):
        """Test to_dict conversion."""
        data = sample_training_example.to_dict()

        assert "id" in data
        assert "prompt" in data
        assert "completion" in data
        assert data["language"] == "python"

    def test_example_to_jsonl(self, sample_training_example):
        """Test JSONL conversion."""
        jsonl = sample_training_example.to_jsonl()
        parsed = json.loads(jsonl)

        assert "prompt" in parsed
        assert "completion" in parsed


# ═══════════════════════════════════════════════════════════════════════════
# Test Training Dataset
# ═══════════════════════════════════════════════════════════════════════════


class TestTrainingDataset:
    """Tests for TrainingDataset class."""

    def test_dataset_creation(self, sample_dataset):
        """Test TrainingDataset creation."""
        assert sample_dataset.name == "test-dataset"
        assert sample_dataset.name_ar == "مجموعة اختبار"
        assert len(sample_dataset.examples) == 1

    def test_add_example(self, sample_dataset):
        """Test adding examples to dataset."""
        new_example = TrainingExample(
            id=str(uuid.uuid4()),
            prompt="Test prompt",
            completion="Test completion",
        )

        initial_count = len(sample_dataset.examples)
        sample_dataset.add_example(new_example)

        assert len(sample_dataset.examples) == initial_count + 1

    def test_to_jsonl(self, sample_dataset):
        """Test JSONL export."""
        jsonl = sample_dataset.to_jsonl()
        lines = jsonl.strip().split("\n")

        assert len(lines) == len(sample_dataset.examples)

        for line in lines:
            parsed = json.loads(line)
            assert "prompt" in parsed
            assert "completion" in parsed

    def test_save_and_load(self, sample_dataset):
        """Test saving and loading dataset."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".jsonl",
            delete=False,
        ) as f:
            temp_path = f.name

        try:
            # Save
            sample_dataset.save(temp_path)
            assert os.path.exists(temp_path)

            # Load
            loaded = TrainingDataset.load(temp_path)

            assert len(loaded.examples) == len(sample_dataset.examples)
            assert loaded.examples[0].prompt == sample_dataset.examples[0].prompt

        finally:
            os.unlink(temp_path)

    def test_to_dict(self, sample_dataset):
        """Test to_dict conversion."""
        data = sample_dataset.to_dict()

        assert data["name"] == "test-dataset"
        assert data["name_ar"] == "مجموعة اختبار"
        assert data["examples_count"] == 1
        assert data["dataset_type"] == "code_fix"


# ═══════════════════════════════════════════════════════════════════════════
# Test Dataset Builder
# ═══════════════════════════════════════════════════════════════════════════


class TestDatasetBuilder:
    """Tests for DatasetBuilder class."""

    def test_add_code_fix_example(self):
        """Test adding code fix examples."""
        builder = DatasetBuilder()

        builder.add_code_fix_example(
            original="x= 1",
            fixed="x = 1",
            error_message="E225 missing whitespace around operator",
            rule_id="E225",
        )

        dataset = builder.build("test", "اختبار")

        assert len(dataset.examples) == 1
        assert dataset.dataset_type == DatasetType.CODE_FIX

    def test_add_code_review_example(self):
        """Test adding code review examples."""
        builder = DatasetBuilder()

        builder.add_code_review_example(
            code="def foo():\n    pass",
            review="Function 'foo' is missing a docstring.",
        )

        dataset = builder.build("reviews", "مراجعات")

        assert len(dataset.examples) == 1
        assert dataset.dataset_type == DatasetType.CODE_REVIEW

    def test_add_test_generation_example(self):
        """Test adding test generation examples."""
        builder = DatasetBuilder()

        builder.add_test_generation_example(
            code="def add(a, b):\n    return a + b",
            tests="def test_add():\n    assert add(1, 2) == 3",
            framework="pytest",
        )

        dataset = builder.build("tests", "اختبارات")

        assert len(dataset.examples) == 1
        assert dataset.dataset_type == DatasetType.TEST_GENERATION

    def test_add_agricultural_advisory_example(self):
        """Test adding agricultural advisory examples."""
        builder = DatasetBuilder()

        builder.add_agricultural_advisory_example(
            query="When should I irrigate my wheat field?",
            response="For wheat in the tillering stage, irrigate when soil moisture drops below 40%.",
            crop_type="wheat",
        )

        dataset = builder.build("agricultural", "زراعي")

        assert len(dataset.examples) == 1
        assert dataset.dataset_type == DatasetType.AGRICULTURAL

    def test_chaining(self):
        """Test method chaining."""
        builder = DatasetBuilder()

        dataset = (
            builder.add_code_fix_example("x=1", "x = 1", "E225")
            .add_code_fix_example("y=2", "y = 2", "E225")
            .build("chained", "متسلسل")
        )

        assert len(dataset.examples) == 2

    def test_from_diagnostic_reports(self):
        """Test building from diagnostic reports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock report file
            report = {
                "diagnostics": [
                    {
                        "source_code": "x=1",
                        "suggestion": "x = 1",
                        "message": "Missing whitespace",
                        "rule_id": "E225",
                    }
                ]
            }

            report_path = os.path.join(temp_dir, "report.json")
            with open(report_path, "w") as f:
                json.dump(report, f)

            builder = DatasetBuilder()
            builder.from_diagnostic_reports(temp_dir)

            dataset = builder.build("from-reports", "من التقارير")

            assert len(dataset.examples) == 1


# ═══════════════════════════════════════════════════════════════════════════
# Test Training Configuration
# ═══════════════════════════════════════════════════════════════════════════


class TestTrainingConfig:
    """Tests for TrainingConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TrainingConfig()

        assert config.base_model == "codellama:7b"
        assert config.epochs == 3
        assert config.batch_size == 4
        assert config.lora_rank == 8

    def test_custom_config(self, sample_config):
        """Test custom configuration."""
        assert sample_config.epochs == 1
        assert sample_config.batch_size == 2

    def test_to_dict(self, sample_config):
        """Test to_dict conversion."""
        data = sample_config.to_dict()

        assert data["base_model"] == "codellama:7b"
        assert data["output_model"] == "test-model:latest"
        assert data["epochs"] == 1


# ═══════════════════════════════════════════════════════════════════════════
# Test Evaluation Result
# ═══════════════════════════════════════════════════════════════════════════


class TestEvaluationResult:
    """Tests for EvaluationResult class."""

    def test_evaluation_result_creation(self):
        """Test EvaluationResult creation."""
        result = EvaluationResult(
            model="test-model",
            accuracy=0.85,
            precision=0.80,
            recall=0.90,
            f1_score=0.85,
            examples_evaluated=100,
            correct_predictions=85,
            average_latency_ms=150.5,
        )

        assert result.accuracy == 0.85
        assert result.examples_evaluated == 100

    def test_to_dict(self):
        """Test to_dict conversion."""
        result = EvaluationResult(
            model="test-model",
            accuracy=0.85,
            precision=0.80,
            recall=0.90,
            f1_score=0.85,
            examples_evaluated=100,
            correct_predictions=85,
            average_latency_ms=150.5,
        )

        data = result.to_dict()

        assert data["model"] == "test-model"
        assert data["accuracy"] == 0.85
        assert "timestamp" in data


# ═══════════════════════════════════════════════════════════════════════════
# Test Training Job
# ═══════════════════════════════════════════════════════════════════════════


class TestTrainingJob:
    """Tests for TrainingJob class."""

    def test_job_creation(self, sample_config):
        """Test TrainingJob creation."""
        job = TrainingJob(
            id=str(uuid.uuid4()),
            dataset_id="dataset-1",
            config=sample_config,
        )

        assert job.status == TrainingStatus.PENDING
        assert job.progress == 0.0

    def test_to_dict(self, sample_config):
        """Test to_dict conversion."""
        job = TrainingJob(
            id="job-1",
            dataset_id="dataset-1",
            config=sample_config,
            status=TrainingStatus.TRAINING,
            progress=50.0,
        )

        data = job.to_dict()

        assert data["id"] == "job-1"
        assert data["status"] == "training"
        assert data["progress"] == 50.0


# ═══════════════════════════════════════════════════════════════════════════
# Test Model Trainer
# ═══════════════════════════════════════════════════════════════════════════


class TestModelTrainer:
    """Tests for ModelTrainer class."""

    @pytest.mark.asyncio
    async def test_create_training_job(self, sample_dataset, sample_config):
        """Test creating a training job."""
        trainer = ModelTrainer()

        job = await trainer.create_training_job(sample_dataset, sample_config)

        assert job.status == TrainingStatus.PENDING
        assert job.dataset_id == sample_dataset.id

    @pytest.mark.asyncio
    async def test_get_job_status(self, sample_dataset, sample_config):
        """Test getting job status."""
        trainer = ModelTrainer()

        job = await trainer.create_training_job(sample_dataset, sample_config)
        status = await trainer.get_job_status(job.id)

        assert status is not None
        assert status.id == job.id

    @pytest.mark.asyncio
    async def test_cancel_job(self, sample_dataset, sample_config):
        """Test cancelling a job."""
        trainer = ModelTrainer()

        job = await trainer.create_training_job(sample_dataset, sample_config)
        result = await trainer.cancel_job(job.id)

        assert result is True
        assert job.status == TrainingStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_list_jobs(self, sample_dataset, sample_config):
        """Test listing all jobs."""
        trainer = ModelTrainer()

        await trainer.create_training_job(sample_dataset, sample_config)
        await trainer.create_training_job(sample_dataset, sample_config)

        jobs = await trainer.list_jobs()

        assert len(jobs) == 2

    @pytest.mark.asyncio
    async def test_start_training_with_mock(self, sample_dataset, sample_config):
        """Test starting training with mocked Ollama."""
        trainer = ModelTrainer()

        job = await trainer.create_training_job(sample_dataset, sample_config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "x = 1"}
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            completed_job = await trainer.start_training(job.id)

        # Ollama /api/create registers configurations, not real fine-tuning
        assert completed_job.status in (TrainingStatus.COMPLETED, TrainingStatus.CONFIGURED)
        assert completed_job.progress == 100.0

    def test_build_system_prompt_code_fix(self, sample_dataset):
        """Test system prompt generation for code fix."""
        trainer = ModelTrainer()
        prompt = trainer._build_system_prompt(sample_dataset)

        assert "code" in prompt.lower()
        assert "fix" in prompt.lower()

    def test_build_system_prompt_agricultural(self):
        """Test system prompt generation for agricultural."""
        dataset = TrainingDataset(
            id="test",
            name="agricultural",
            name_ar="زراعي",
            description="Test",
            description_ar="اختبار",
            dataset_type=DatasetType.AGRICULTURAL,
        )

        trainer = ModelTrainer()
        prompt = trainer._build_system_prompt(dataset)

        assert "agricultural" in prompt.lower()
        assert "سهول" in prompt  # Arabic SAHOOL

    def test_check_similarity_exact_match(self):
        """Test similarity check with exact match."""
        trainer = ModelTrainer()

        assert trainer._check_similarity("x = 1", "x = 1") is True

    def test_check_similarity_contains(self):
        """Test similarity check with contains."""
        trainer = ModelTrainer()

        assert trainer._check_similarity("Here is the fix: x = 1", "x = 1") is True

    def test_check_similarity_high_overlap(self):
        """Test similarity check with high token overlap."""
        trainer = ModelTrainer()

        # Test with higher token overlap (>70%)
        assert trainer._check_similarity("def hello world print message", "def hello world print") is True


# ═══════════════════════════════════════════════════════════════════════════
# Test Convenience Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_code_fix_dataset(self):
        """Test create_code_fix_dataset function."""
        examples = [
            ("x=1", "x = 1", "E225"),
            ("y=2", "y = 2", "E225"),
            ("import os", "", "F401 unused import"),
        ]

        dataset = create_code_fix_dataset(examples, "test-fixes")

        assert dataset.name == "test-fixes"
        assert len(dataset.examples) == 3
        assert dataset.dataset_type == DatasetType.CODE_FIX


# ═══════════════════════════════════════════════════════════════════════════
# Test Arabic Support
# ═══════════════════════════════════════════════════════════════════════════


class TestArabicSupport:
    """Tests for Arabic language support."""

    def test_arabic_dataset_names(self):
        """Test Arabic names in datasets."""
        builder = DatasetBuilder()

        builder.add_code_fix_example("x=1", "x = 1", "خطأ في المسافات")

        dataset = builder.build(
            name="fixes",
            name_ar="إصلاحات الكود",
            description="Code fixes dataset",
            description_ar="مجموعة بيانات إصلاحات الكود",
        )

        assert dataset.name_ar == "إصلاحات الكود"
        assert dataset.description_ar == "مجموعة بيانات إصلاحات الكود"

    def test_arabic_advisory_example(self):
        """Test Arabic agricultural advisory."""
        builder = DatasetBuilder()

        builder.add_agricultural_advisory_example(
            query="متى يجب أن أروي حقل القمح؟",
            response="يجب ري حقل القمح عندما تنخفض رطوبة التربة إلى أقل من 40%",
            crop_type="wheat",
            language_code="ar",
        )

        dataset = builder.build("advisory-ar", "استشارات زراعية")

        assert len(dataset.examples) == 1
        assert dataset.examples[0].language == "ar"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
