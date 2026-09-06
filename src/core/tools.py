from typing import Any, Dict  # noqa: UP035
from core.prometheus import PrometheusClient

prometheus_client = PrometheusClient()

KNOWN_SERVICES = ["checkout", "auth", "payments"]


def extract_service_name(question: str) -> str:
    """Extract known service name from the question string."""
    question_lower = question.lower()
    for service in KNOWN_SERVICES:
        if service in question_lower:
            return service
    return "unknown"


def get_service_health(service: str) -> Dict[str, Any]:
    """Real tool: query service health metrics from Prometheus."""
    return prometheus_client.fetch_service_health(service)


def check_service_status(service_hint: str) -> Dict[str, Any]:
    """Backwards-compatibility wrapper for get_service_health."""
    service = extract_service_name(service_hint)
    if service == "unknown":
        return get_service_health(service_hint)
    return get_service_health(service)


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