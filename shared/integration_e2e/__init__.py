# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""End-to-end integration tests for the v3.1 agronomy stack (Phase 4).

This package wires the four ADRs that landed in v3.1 into a single
in-process pipeline so we can prove they compose:

* ADR-014 — :mod:`shared.edge_resilience.wal` (durable buffer)
* ADR-011 — :mod:`shared.spatiotemporal` (sensor fusion)
* ADR-015 — :mod:`shared.process_models.prosail_inversion` (canopy retrieval)
* ADR-013 — :mod:`shared.prescription_safety` (safety gateway)

The tests are pure-Python and require no external services — they use
the WAL with a temp directory and inject mock checkers so the gateway
runs offline.
"""
