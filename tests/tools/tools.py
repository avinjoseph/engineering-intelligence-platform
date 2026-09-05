"""
Real tool: get_service_health(service) — Swapped to query live Prometheus API.

The function signature and return shape remain identical to the initial fake tool contract.
"""

import os
import sys

# Ensure src directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from core.tools import (
    KNOWN_SERVICES,
    extract_service_name,
    get_service_health,
    run_tools,
)

__all__ = [
    "KNOWN_SERVICES",
    "extract_service_name",
    "get_service_health",
    "run_tools",
]