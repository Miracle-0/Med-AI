import uuid
from typing import List
from app.models.knowledge import KnowledgeNode, KnowledgeEdge
from app.services.llm_service import llm_service

class KnowledgeExtractor:
    """知识提取器"""

    async def extract_from_chapter(self, chapter_content: str, textbook_id: str, chapter_id: str, page: int = 1) -> List[KnowledgeNode]:
        """从章节内容中提取知识点"""

        system_prompt = """你是一个学科知识提取专家。请从给定的教材章节内容中提取核心知识点。

要求：
1. 提取概念、定理、方法、现象等知识点
2. 每个知识点包含：名称、定义、分类
3. 分类包括：核心概念、定理、方法、现象
4. 输出JSON格式

输出格式：
{
  "knowledge_points": [
    {
      "name": "知识点名称",
      "definition": "知识点定义",
      "category": "分类"
    }
  ]
}"""

        prompt = f"""请从以下章节内容中提取知识点：

{chapter_content[:3000]}

请输出JSON格式的知识点列表。"""

        result = await llm_service.generate_json(prompt, system_prompt)

        nodes = []
        if "knowledge_points" in result:
            for kp in result["knowledge_points"]:
                # 支持多种 JSON 格式
                name = kp.get("name") or kp.get("topic") or kp.get("title") or ""
                definition = kp.get("definition") or kp.get("content") or kp.get("description") or ""
                category = kp.get("category") or kp.get("type") or "核心概念"

                if not name:
                    continue

                node = KnowledgeNode(
                    node_id=f"{textbook_id}_node_{str(uuid.uuid4())[:8]}",
                    name=name,
                    definition=definition,
                    category=category,
                    textbook_id=textbook_id,
                    chapter_id=chapter_id,
                    page=page
                )
                nodes.append(node)

        return nodes

    async def identify_relations(self, nodes: List[KnowledgeNode]) -> List[KnowledgeEdge]:
        """识别知识点之间的关系"""

        if len(nodes) < 2:
            return []

        nodes_info = "\n".join([f"- {node.name}: {node.definition[:50]}..." for node in nodes[:20]])

        system_prompt = """你是一个学科知识关系分析专家。请分析以下知识点之间的关系。

关系类型：
- prerequisite: 学习B之前必须先掌握A
- parallel: 同一层级的平行概念
- contains: 上位概念与下位概念
- applies_to: 某知识点是另一个的应用场景

输出JSON格式：
{
  "relations": [
    {
      "source": "源知识点名称",
      "target": "目标知识点名称",
      "relation_type": "关系类型",
      "description": "关系描述"
    }
  ]
}"""

        prompt = f"""请分析以下知识点之间的关系：

{nodes_info}

请输出JSON格式的关系列表。"""

        result = await llm_service.generate_json(prompt, system_prompt)

        edges = []
        if "relations" in result:
            name_to_node = {node.name: node for node in nodes}

            for rel in result["relations"]:
                source_name = rel.get("source", "")
                target_name = rel.get("target", "")

                if source_name in name_to_node and target_name in name_to_node:
                    edge = KnowledgeEdge(
                        edge_id=f"edge_{str(uuid.uuid4())[:8]}",
                        source_node_id=name_to_node[source_name].node_id,
                        target_node_id=name_to_node[target_name].node_id,
                        relation_type=rel.get("relation_type", "parallel"),
                        description=rel.get("description", "")
                    )
                    edges.append(edge)

        return edges

extractor = KnowledgeExtractor()
