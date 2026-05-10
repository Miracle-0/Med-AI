import uuid
from typing import List, Tuple
from app.models.knowledge import KnowledgeNode, KnowledgeEdge, MergeDecision, MergeAction
from app.services.llm_service import llm_service
from app.utils.embedding import embedding_service

class KnowledgeMerger:
    """知识整合器"""

    async def find_duplicates(self, nodes: List[KnowledgeNode]) -> List[List[KnowledgeNode]]:
        """识别重复知识点"""
        if len(nodes) < 2:
            return []

        texts = [f"{node.name}: {node.definition}" for node in nodes]
        embeddings = await embedding_service.get_embeddings(texts)

        duplicate_groups = []
        processed = set()

        for i in range(len(nodes)):
            if i in processed:
                continue

            group = [nodes[i]]
            processed.add(i)

            for j in range(i + 1, len(nodes)):
                if j in processed:
                    continue

                similarity = self._cosine_similarity(embeddings[i], embeddings[j])

                if similarity > 0.85:
                    group.append(nodes[j])
                    processed.add(j)

            if len(group) > 1:
                duplicate_groups.append(group)

        return duplicate_groups

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        import numpy as np
        a = np.array(vec1)
        b = np.array(vec2)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    async def execute_merge(
        self,
        nodes: List[KnowledgeNode],
        duplicate_groups: List[List[KnowledgeNode]]
    ) -> Tuple[List[KnowledgeNode], List[MergeDecision]]:
        """执行整合决策"""
        merged_nodes = []
        decisions = []
        merged_node_ids = set()

        for group in duplicate_groups:
            decision = await self._make_merge_decision(group)
            decisions.append(decision)

            if decision.action == MergeAction.MERGE:
                best_node = self._select_best_node(group)
                merged_nodes.append(best_node)
                merged_node_ids.update(node.node_id for node in group)
            elif decision.action == MergeAction.KEEP:
                for node in group:
                    if node.node_id not in merged_node_ids:
                        merged_nodes.append(node)
                        merged_node_ids.add(node.node_id)
            elif decision.action == MergeAction.REMOVE:
                merged_node_ids.update(node.node_id for node in group)

        for node in nodes:
            if node.node_id not in merged_node_ids:
                merged_nodes.append(node)

        return merged_nodes, decisions

    async def _make_merge_decision(self, group: List[KnowledgeNode]) -> MergeDecision:
        """使用LLM做出整合决策"""

        nodes_info = "\n".join([
            f"- {node.name} ({node.textbook_id}): {node.definition[:100]}..."
            for node in group
        ])

        system_prompt = """你是一个学科知识整合专家。请判断以下重复知识点应该如何处理。

处理方式：
- merge: 合并为一个知识点，保留最完整的描述
- keep: 保留所有知识点，因为它们有细微但重要的区别
- remove: 删除冗余知识点，保留最权威的来源

输出JSON格式：
{
  "action": "merge/keep/remove",
  "reason": "决策理由",
  "confidence": 0.9
}"""

        prompt = f"""请判断以下知识点应该如何处理：

{nodes_info}

请输出JSON格式的决策。"""

        result = await llm_service.generate_json(prompt, system_prompt)

        return MergeDecision(
            decision_id=f"decision_{str(uuid.uuid4())[:8]}",
            action=MergeAction(result.get("action", "merge")),
            affected_nodes=[node.node_id for node in group],
            result_node_id=group[0].node_id if result.get("action") == "merge" else None,
            reason=result.get("reason", ""),
            confidence=result.get("confidence", 0.8)
        )

    def _select_best_node(self, group: List[KnowledgeNode]) -> KnowledgeNode:
        """选择最完整的节点"""
        return max(group, key=lambda node: len(node.definition))

    def calculate_compression_ratio(
        self,
        original_nodes: List[KnowledgeNode],
        merged_nodes: List[KnowledgeNode]
    ) -> float:
        """计算压缩比"""
        if not original_nodes:
            return 0.0
        return 1 - (len(merged_nodes) / len(original_nodes))

merger = KnowledgeMerger()
