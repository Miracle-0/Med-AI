from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import parse_node, extract_node, merge_node

def create_workflow():
    """创建工作流"""
    workflow = StateGraph(GraphState)

    workflow.add_node("parse", parse_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("merge", merge_node)

    workflow.add_edge("parse", "extract")
    workflow.add_edge("extract", "merge")
    workflow.add_edge("merge", END)

    workflow.set_entry_point("parse")

    app = workflow.compile()

    return app

workflow_app = create_workflow()
