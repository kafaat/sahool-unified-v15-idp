"""
SAHOOL Smart Agriculture - Blockchain Traceability Tests
اختبارات تتبع البلوكتشين للزراعة الذكية

Tests for blockchain traceability including:
- Creating batches
- Recording operations
- Generating hashes
- Verifying integrity
- Full traceability chain
- Immutability

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from .conftest import OperationType

# ==============================================================================
# Blockchain Traceability Implementation (Test Target Mock)
# ==============================================================================


class Block:
    """Single block in the traceability chain"""

    def __init__(
        self,
        index: int,
        data: dict[str, Any],
        previous_hash: str,
        timestamp: datetime | None = None,
    ):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.timestamp = timestamp or datetime.now(UTC)
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = json.dumps(
            {
                "index": self.index,
                "data": self.data,
                "previous_hash": self.previous_hash,
                "timestamp": self.timestamp.isoformat(),
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_data.encode()).hexdigest()


class TraceabilityChain:
    """Blockchain-based traceability chain for agricultural products"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._chain: list[Block] = []
        self._batches: dict[str, dict[str, Any]] = {}
        self._pending_operations: list[dict[str, Any]] = []

        # Create genesis block
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Create the genesis (first) block"""
        genesis_data = {
            "type": "genesis",
            "chain_id": self.config.get("chain_id", "sahool-trace"),
            "created_at": datetime.now(UTC).isoformat(),
        }
        genesis_block = Block(
            index=0,
            data=genesis_data,
            previous_hash="0",
        )
        self._chain.append(genesis_block)

    def create_batch(self, batch_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new product batch
        إنشاء دفعة منتج جديدة
        """
        batch_id = batch_data.get("batch_id", str(uuid.uuid4()))

        batch = {
            "batch_id": batch_id,
            "farm_id": batch_data.get("farm_id"),
            "field_id": batch_data.get("field_id"),
            "product_type": batch_data.get("product_type"),
            "variety": batch_data.get("variety"),
            "quantity_kg": batch_data.get("quantity_kg"),
            "created_at": datetime.now(UTC).isoformat(),
            "status": "active",
            "operations": [],
        }

        self._batches[batch_id] = batch

        # Record batch creation on chain
        self._add_block(
            {
                "type": "batch_created",
                "batch_id": batch_id,
                "product_type": batch["product_type"],
                "quantity_kg": batch["quantity_kg"],
            }
        )

        return {
            "success": True,
            "batch_id": batch_id,
            "block_index": len(self._chain) - 1,
            "block_hash": self._chain[-1].hash,
        }

    def record_operation(
        self,
        batch_id: str,
        operation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Record an operation for a batch
        تسجيل عملية لدفعة
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch not found: {batch_id}")

        batch = self._batches[batch_id]

        record = {
            "record_id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "operation_type": operation.get("operation_type"),
            "timestamp": operation.get("timestamp", datetime.now(UTC).isoformat()),
            "data": operation.get("data", {}),
            "operator_id": operation.get("operator_id"),
            "verified": False,
        }

        # Add to batch operations
        batch["operations"].append(record)

        # Add to blockchain
        self._add_block(
            {
                "type": "operation_recorded",
                "record_id": record["record_id"],
                "batch_id": batch_id,
                "operation_type": record["operation_type"],
                "data_hash": self._hash_data(record["data"]),
            }
        )

        record["verified"] = True
        record["block_hash"] = self._chain[-1].hash
        record["block_index"] = len(self._chain) - 1

        return {
            "success": True,
            "record": record,
        }

    def _add_block(self, data: dict[str, Any]) -> Block:
        """Add a new block to the chain"""
        previous_block = self._chain[-1]
        new_block = Block(
            index=len(self._chain),
            data=data,
            previous_hash=previous_block.hash,
        )
        self._chain.append(new_block)
        return new_block

    def _hash_data(self, data: dict[str, Any]) -> str:
        """Hash operation data"""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def generate_hash(self, data: Any) -> str:
        """
        Generate hash for any data
        توليد تجزئة لأي بيانات
        """
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = str(data)

        return hashlib.sha256(data_str.encode()).hexdigest()

    def verify_integrity(self) -> dict[str, Any]:
        """
        Verify the integrity of the entire chain
        التحقق من سلامة السلسلة بأكملها
        """
        if len(self._chain) <= 1:
            return {"valid": True, "blocks_checked": 1, "errors": []}

        errors = []

        for i in range(1, len(self._chain)):
            current = self._chain[i]
            previous = self._chain[i - 1]

            # Verify hash link
            if current.previous_hash != previous.hash:
                errors.append(
                    {
                        "block_index": i,
                        "error": "hash_mismatch",
                        "expected": previous.hash,
                        "actual": current.previous_hash,
                    }
                )

            # Verify block hash
            calculated_hash = current.calculate_hash()
            if calculated_hash != current.hash:
                errors.append(
                    {
                        "block_index": i,
                        "error": "invalid_block_hash",
                    }
                )

        return {
            "valid": len(errors) == 0,
            "blocks_checked": len(self._chain),
            "errors": errors,
        }

    def verify_operation(self, record_id: str) -> dict[str, Any]:
        """
        Verify a specific operation record
        التحقق من سجل عملية محدد
        """
        # Find the record
        record = None
        batch_id = None
        for bid, batch in self._batches.items():
            for op in batch["operations"]:
                if op["record_id"] == record_id:
                    record = op
                    batch_id = bid
                    break
            if record:
                break

        if not record:
            return {"valid": False, "reason": "record_not_found"}

        # Find the block
        block_index = record.get("block_index")
        if block_index is None or block_index >= len(self._chain):
            return {"valid": False, "reason": "block_not_found"}

        block = self._chain[block_index]

        # Verify the operation is in the block
        if block.data.get("record_id") != record_id:
            return {"valid": False, "reason": "record_not_in_block"}

        # Verify block hash matches stored hash
        if block.hash != record.get("block_hash"):
            return {"valid": False, "reason": "hash_mismatch"}

        return {
            "valid": True,
            "record_id": record_id,
            "batch_id": batch_id,
            "block_index": block_index,
            "block_hash": block.hash,
        }

    def get_full_trace(self, batch_id: str) -> dict[str, Any]:
        """
        Get full traceability history for a batch
        الحصول على تاريخ التتبع الكامل لدفعة
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch not found: {batch_id}")

        batch = self._batches[batch_id]
        operations = batch["operations"]

        # Build trace with verification
        trace = []
        for op in operations:
            verification = self.verify_operation(op["record_id"])
            trace.append(
                {
                    **op,
                    "verified": verification["valid"],
                }
            )

        return {
            "batch_id": batch_id,
            "product_type": batch["product_type"],
            "variety": batch.get("variety"),
            "quantity_kg": batch["quantity_kg"],
            "created_at": batch["created_at"],
            "status": batch["status"],
            "operations": trace,
            "total_operations": len(trace),
            "chain_integrity": self.verify_integrity(),
        }

    def get_batch(self, batch_id: str) -> dict[str, Any] | None:
        """Get batch information"""
        return self._batches.get(batch_id)

    def get_chain_length(self) -> int:
        """Get current chain length"""
        return len(self._chain)

    def attempt_tamper(self, block_index: int, new_data: dict[str, Any]) -> None:
        """
        Attempt to tamper with a block (for testing immutability)
        محاولة العبث بكتلة (لاختبار عدم القابلية للتغيير)
        """
        if block_index < 0 or block_index >= len(self._chain):
            raise ValueError("Invalid block index")

        # Directly modify block data (simulating tampering)
        self._chain[block_index].data = new_data
        # Note: We don't recalculate hash, which is what tampering would look like


# ==============================================================================
# Test Classes
# ==============================================================================


class TestCreateBatch:
    """Tests for batch creation"""

    @pytest.fixture
    def chain(self, blockchain_config: dict[str, Any]) -> TraceabilityChain:
        return TraceabilityChain(blockchain_config)

    def test_create_batch_success(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
    ):
        """Test successful batch creation"""
        result = chain.create_batch(sample_batch)

        assert result["success"] is True
        assert "batch_id" in result
        assert "block_hash" in result

        batch = chain.get_batch(result["batch_id"])
        assert batch is not None
        assert batch["product_type"] == sample_batch["product_type"]

    def test_create_batch_with_custom_id(self, chain: TraceabilityChain):
        """Test batch creation with custom ID"""
        custom_id = "BATCH-2024-001"
        result = chain.create_batch(
            {
                "batch_id": custom_id,
                "product_type": "wheat",
                "quantity_kg": 1000,
            }
        )

        assert result["batch_id"] == custom_id

    def test_create_batch_adds_block(self, chain: TraceabilityChain):
        """Test batch creation adds a block to chain"""
        initial_length = chain.get_chain_length()

        chain.create_batch(
            {
                "product_type": "barley",
                "quantity_kg": 500,
            }
        )

        assert chain.get_chain_length() == initial_length + 1

    def test_batch_initial_status(self, chain: TraceabilityChain):
        """Test batch has initial status of active"""
        result = chain.create_batch(
            {
                "product_type": "wheat",
                "quantity_kg": 1000,
            }
        )

        batch = chain.get_batch(result["batch_id"])
        assert batch["status"] == "active"


class TestRecordOperation:
    """Tests for recording operations"""

    @pytest.fixture
    def chain(self, blockchain_config: dict[str, Any]) -> TraceabilityChain:
        return TraceabilityChain(blockchain_config)

    @pytest.fixture
    def batch_id(self, chain: TraceabilityChain, sample_batch: dict[str, Any]) -> str:
        result = chain.create_batch(sample_batch)
        return result["batch_id"]

    def test_record_operation_success(
        self,
        chain: TraceabilityChain,
        batch_id: str,
    ):
        """Test successful operation recording"""
        result = chain.record_operation(
            batch_id,
            {
                "operation_type": OperationType.IRRIGATION.value,
                "data": {
                    "water_amount_mm": 25,
                    "method": "drip",
                },
                "operator_id": "farmer-001",
            },
        )

        assert result["success"] is True
        assert result["record"]["verified"] is True
        assert "block_hash" in result["record"]

    def test_record_multiple_operations(
        self,
        chain: TraceabilityChain,
        batch_id: str,
    ):
        """Test recording multiple operations"""
        operations = [
            {"operation_type": OperationType.IRRIGATION.value, "data": {"amount": 25}},
            {"operation_type": OperationType.FERTILIZATION.value, "data": {"type": "urea"}},
            {"operation_type": OperationType.HARVEST.value, "data": {"yield_kg": 5000}},
        ]

        for op in operations:
            chain.record_operation(batch_id, op)

        batch = chain.get_batch(batch_id)
        assert len(batch["operations"]) == 3

    def test_record_operation_invalid_batch(self, chain: TraceabilityChain):
        """Test recording operation for invalid batch fails"""
        with pytest.raises(ValueError, match="Batch not found"):
            chain.record_operation(
                "invalid-batch-id",
                {
                    "operation_type": OperationType.IRRIGATION.value,
                },
            )

    def test_operation_includes_timestamp(
        self,
        chain: TraceabilityChain,
        batch_id: str,
    ):
        """Test operation record includes timestamp"""
        result = chain.record_operation(
            batch_id,
            {
                "operation_type": OperationType.PLANTING.value,
                "data": {"seed_rate": 120},
            },
        )

        assert "timestamp" in result["record"]


class TestGenerateHash:
    """Tests for hash generation"""

    @pytest.fixture
    def chain(self, blockchain_config: dict[str, Any]) -> TraceabilityChain:
        return TraceabilityChain(blockchain_config)

    def test_generate_hash_dict(self, chain: TraceabilityChain):
        """Test hash generation for dictionary"""
        data = {"field": "value", "number": 42}
        hash_result = chain.generate_hash(data)

        assert len(hash_result) == 64  # SHA-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_generate_hash_string(self, chain: TraceabilityChain):
        """Test hash generation for string"""
        data = "test string"
        hash_result = chain.generate_hash(data)

        assert len(hash_result) == 64

    def test_generate_hash_deterministic(self, chain: TraceabilityChain):
        """Test hash generation is deterministic"""
        data = {"key": "value"}

        hash1 = chain.generate_hash(data)
        hash2 = chain.generate_hash(data)

        assert hash1 == hash2

    def test_generate_hash_different_inputs(self, chain: TraceabilityChain):
        """Test different inputs produce different hashes"""
        hash1 = chain.generate_hash({"key": "value1"})
        hash2 = chain.generate_hash({"key": "value2"})

        assert hash1 != hash2


class TestVerifyIntegrity:
    """Tests for integrity verification"""

    @pytest.fixture
    def chain(self, blockchain_config: dict[str, Any]) -> TraceabilityChain:
        return TraceabilityChain(blockchain_config)

    def test_verify_integrity_empty_chain(self, chain: TraceabilityChain):
        """Test integrity verification on chain with only genesis block"""
        result = chain.verify_integrity()

        assert result["valid"] is True
        assert result["blocks_checked"] == 1

    def test_verify_integrity_with_operations(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
    ):
        """Test integrity verification after adding operations"""
        batch_result = chain.create_batch(sample_batch)
        batch_id = batch_result["batch_id"]

        for i in range(5):
            chain.record_operation(
                batch_id,
                {
                    "operation_type": OperationType.IRRIGATION.value,
                    "data": {"iteration": i},
                },
            )

        result = chain.verify_integrity()

        assert result["valid"] is True
        assert result["blocks_checked"] == 7  # Genesis + batch + 5 operations

    def test_verify_operation_record(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
    ):
        """Test verifying a specific operation record"""
        batch_result = chain.create_batch(sample_batch)
        batch_id = batch_result["batch_id"]

        op_result = chain.record_operation(
            batch_id,
            {
                "operation_type": OperationType.HARVEST.value,
                "data": {"yield_kg": 5000},
            },
        )

        record_id = op_result["record"]["record_id"]
        verification = chain.verify_operation(record_id)

        assert verification["valid"] is True
        assert verification["batch_id"] == batch_id

    def test_verify_nonexistent_operation(self, chain: TraceabilityChain):
        """Test verifying non-existent operation fails"""
        result = chain.verify_operation("nonexistent-record-id")

        assert result["valid"] is False
        assert result["reason"] == "record_not_found"


class TestFullTrace:
    """Tests for full traceability"""

    @pytest.fixture
    def chain(self, blockchain_config: dict[str, Any]) -> TraceabilityChain:
        return TraceabilityChain(blockchain_config)

    def test_get_full_trace(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
        sample_operation_records: list[dict[str, Any]],
    ):
        """Test getting full traceability history"""
        batch_result = chain.create_batch(sample_batch)
        batch_id = batch_result["batch_id"]

        # Record operations
        for op in sample_operation_records:
            chain.record_operation(batch_id, op)

        trace = chain.get_full_trace(batch_id)

        assert trace["batch_id"] == batch_id
        assert trace["product_type"] == sample_batch["product_type"]
        assert trace["total_operations"] == len(sample_operation_records)
        assert trace["chain_integrity"]["valid"] is True

    def test_full_trace_includes_verification(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
    ):
        """Test full trace includes verification status for each operation"""
        batch_result = chain.create_batch(sample_batch)
        batch_id = batch_result["batch_id"]

        chain.record_operation(
            batch_id,
            {
                "operation_type": OperationType.PLANTING.value,
                "data": {"seed_rate": 120},
            },
        )

        trace = chain.get_full_trace(batch_id)

        for op in trace["operations"]:
            assert "verified" in op
            assert op["verified"] is True

    def test_full_trace_invalid_batch(self, chain: TraceabilityChain):
        """Test getting trace for invalid batch fails"""
        with pytest.raises(ValueError, match="Batch not found"):
            chain.get_full_trace("invalid-batch-id")

    def test_trace_chronological_order(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
    ):
        """Test operations in trace are in chronological order"""
        batch_result = chain.create_batch(sample_batch)
        batch_id = batch_result["batch_id"]

        operations = [
            {"operation_type": OperationType.PLANTING.value},
            {"operation_type": OperationType.IRRIGATION.value},
            {"operation_type": OperationType.FERTILIZATION.value},
            {"operation_type": OperationType.HARVEST.value},
        ]

        for op in operations:
            chain.record_operation(batch_id, op)

        trace = chain.get_full_trace(batch_id)

        # Verify order matches insertion order
        assert trace["operations"][0]["operation_type"] == OperationType.PLANTING.value
        assert trace["operations"][3]["operation_type"] == OperationType.HARVEST.value


class TestImmutability:
    """Tests for blockchain immutability"""

    @pytest.fixture
    def chain(self, blockchain_config: dict[str, Any]) -> TraceabilityChain:
        return TraceabilityChain(blockchain_config)

    def test_tampered_block_detected(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
    ):
        """Test that tampering with a block is detected"""
        batch_result = chain.create_batch(sample_batch)
        batch_id = batch_result["batch_id"]

        chain.record_operation(
            batch_id,
            {
                "operation_type": OperationType.HARVEST.value,
                "data": {"yield_kg": 5000},
            },
        )

        # Verify integrity before tampering
        result_before = chain.verify_integrity()
        assert result_before["valid"] is True

        # Attempt to tamper with a block
        chain.attempt_tamper(1, {"type": "tampered", "fake_data": True})

        # Verify integrity after tampering - should detect the change
        result_after = chain.verify_integrity()
        assert result_after["valid"] is False
        assert len(result_after["errors"]) > 0

    def test_hash_chain_maintains_integrity(
        self,
        chain: TraceabilityChain,
        sample_batch: dict[str, Any],
    ):
        """Test that hash chain maintains integrity"""
        batch_result = chain.create_batch(sample_batch)
        batch_id = batch_result["batch_id"]

        # Add multiple blocks
        for i in range(5):
            chain.record_operation(
                batch_id,
                {
                    "operation_type": OperationType.IRRIGATION.value,
                    "data": {"iteration": i},
                },
            )

        # Verify each block links to previous
        for i in range(1, len(chain._chain)):
            current = chain._chain[i]
            previous = chain._chain[i - 1]
            assert current.previous_hash == previous.hash

    def test_block_hash_changes_with_data(self, chain: TraceabilityChain):
        """Test that block hash changes when data changes"""
        # Create two chains with different data
        chain2 = TraceabilityChain(chain.config)

        chain.create_batch({"product_type": "wheat", "quantity_kg": 1000})
        chain2.create_batch({"product_type": "barley", "quantity_kg": 2000})

        # Block hashes should be different
        assert chain._chain[1].hash != chain2._chain[1].hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
