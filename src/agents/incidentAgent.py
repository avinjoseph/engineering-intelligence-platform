import os
import sys

# Add the src directory to sys.path so we can import from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.graph import END, START, StateGraph

from core.llm import chat
from core.state import IncidentState
from core.tools import run_tools
from scripts.search import search


def retrieve_docs(state: IncidentState) -> dict:
    """Retrieve relevant documents based on the question in the state."""
    question = state["question"]
    retrieved_docs = search(question)
    return {"retrieved_docs": retrieved_docs}

def generate_response(state: IncidentState) -> dict:
    
    question = state["question"]
    retrieved_docs = state["retrieved_docs"]
    tool_results = state["tool_results"]
    
    if retrieved_docs:
        docs_block = "\n\n".join(
            [f"Source: {doc['source']}\nText: {doc['text']}" for doc in retrieved_docs])
    else:
        docs_block = "No relevant documents found in knowledge base."
        
    system_prompt = (
        "You are an incident-response assistant. You have two sources of "
        "information: retrieved documentation, and a live tool result "
        "(current service health data). Use BOTH:\n"
        "- If the tool result shows a recent deploy AND degraded metrics "
        "(high latency or error rate), treat the recent deploy as the "
        "likely cause and say so explicitly.\n"
        "- Ground any documentation-based claims in the retrieved docs only.\n"
        "- If neither source supports an answer, say so plainly instead of "
        "guessing.\n"
        "- Cite the source filename for any claim from the documents."
    )
    
    user_prompt = f"""Question: {question}
    
    Retrieved Documents:
    {docs_block}
    
    Live system check:
    {tool_results}
    
    Answer the question using above context only."""
    
    answer = chat(system_prompt, user_prompt)
    return {"final_answer": answer}

def build_graph():
    graph = StateGraph(IncidentState)
    graph.add_node("retrieve", retrieve_docs)
    graph.add_node("investigate", run_tools)
    graph.add_node("answer", generate_response)
    
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "investigate")
    graph.add_edge("investigate", "answer")
    graph.add_edge("answer", END)
    
    return graph.compile()

app = build_graph()


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "why is checkout slow"
    initial_state = IncidentState(
        question=question,
        retrieved_docs=[],
        tool_results={},
        final_answer=""
    )
    
    final_state = app.invoke(initial_state)
    
    print(f"\nQuestion: {question}\n")
    print(f"Retrieved {len(final_state['retrieved_docs'])} doc(s):")
    
    for d in final_state["retrieved_docs"]:
        print(f"- {d['source']} (vector_score: {d['vector_score']}")
        
    print(f"\nTool Results: {final_state['tool_results']}\n")
    print(f"Final Answer: {final_state['final_answer']}\n")
        