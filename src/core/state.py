from typing import Any, Dict, List, TypedDict  # noqa: UP035


class IncidentState(TypedDict):
    """Represents the state of an incident."""
    question: str
    retrieved_docs: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    final_answer: str