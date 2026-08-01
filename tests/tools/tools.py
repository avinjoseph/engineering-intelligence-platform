"""
First real tool: get_service_health(service) — FAKE data for now.

This intentionally mimics what a Prometheus/Grafana query would return
(latency, error rate, current deploy version) without needing any real
monitoring stack connected. Once the agent reliably uses this data
correctly in its reasoning, swap the body of get_service_health() for a
real Prometheus query — nothing else in the graph needs to change, since
the function signature and return shape stay the same.
"""

from typing import Any, Dict  # noqa: UP035

# Fake health data, keyed by service name. Deliberately includes a service
# with a recent deploy + degraded metrics (checkout) so we can test whether
# the agent correctly correlates "recent deploy" with "current problem" —
# exactly the reasoning pattern real incident response needs.
FAKE_HEALTH_DATA: Dict[str, Dict[str, Any]] = {
    "checkout": {
        "latency": "900ms",
        "error_rate": "5%",
        "deploy": "checkout-v1.4",
        "deployed_minutes_ago": 12,
    },
    "auth": {
        "latency": "120ms",
        "error_rate": "0.2%",
        "deploy": "auth-v2.1",
        "deployed_minutes_ago": 4320,  # 3 days ago, stable
    },
    "payments": {
        "latency": "210ms",
        "error_rate": "0.8%",
        "deploy": "payments-v3.0",
        "deployed_minutes_ago": 60,
    },
}


def get_service_health(service: str) -> Dict[str, Any]:
    """Fake tool — replace internals with a real Prometheus query later."""
    service = service.lower().strip()
    if service in FAKE_HEALTH_DATA:
        data = FAKE_HEALTH_DATA[service]
        return {"service": service, **data}
    return {
        "service": service,
        "status": "no health data available for this service",
    }


# --- service name extraction -------------------------------------------
# Naive keyword match for now. This is exactly the kind of thing a real
# tool-calling LLM step would normally do (decide *which* service the
# question is about) — hardcoded here to keep this step focused on
# proving the tool-use pattern before adding that reasoning layer.

KNOWN_SERVICES = list(FAKE_HEALTH_DATA.keys())


def extract_service_name(question: str) -> str:
    question_lower = question.lower()
    for service in KNOWN_SERVICES:
        if service in question_lower:
            return service
    return "unknown"


def run_tools(state) -> Dict[str, Any]:
    """LangGraph node: investigate step. Calls get_service_health for the
    service mentioned in the question."""
    question = state["question"]
    service = extract_service_name(question)

    if service == "unknown":
        result = {"note": "Could not determine which service this question refers to."}
    else:
        result = get_service_health(service)

    print(f"Tool call: get_service_health({service!r}) -> {result}")
    return {"tool_results": result}