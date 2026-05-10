from typing import List, Optional, TypedDict
from enum import Enum

class PipelineState(Enum):
    """流水线状态"""
    PARSE = "parse"
    EXTRACT = "extract"
    MERGE = "merge"
    DONE = "done"

class GraphState(TypedDict):
    """状态机状态"""
    textbook_paths: List[str]
    textbooks: List[dict]
    chapters: List[dict]
    nodes: List[dict]
    edges: List[dict]
    merged_nodes: List[dict]
    merge_decisions: List[dict]
    current_state: str
    error: Optional[str]
    progress: float
