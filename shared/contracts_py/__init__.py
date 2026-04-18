"""
SAHOOL Python Contracts
=======================

Python mirror of the TypeScript contracts in::

    packages/shared-types/src/contracts/

The TypeScript package is the canonical source of truth. This Python
package is **auto-generated** from those TS sources.

To regenerate::

    npm run contracts:sync-python

CI enforces drift via ``.github/workflows/contracts-drift-guard.yml`` —
any TS-side change to a contract requires running the sync script and
committing ``shared/contracts_py/service_ports.py`` in the same PR.

DO NOT edit files in this package by hand.
"""

from .service_ports import SERVICE_PORTS, ServicePorts

__all__ = ["SERVICE_PORTS", "ServicePorts"]
