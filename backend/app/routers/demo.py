import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.textbook import Textbook, ParseStatus
from app.models.chapter import Chapter
from app.models.knowledge import KnowledgeNode, KnowledgeEdge
from app.services.parser import parser
from app.services.extractor import extractor
from app.routers.graph import _extraction_progress

router = APIRouter()

DEMO_TEXTBOOK_ID = "demo_医学基础"

DEMO_CONTENT = """# 第一章 细胞的基本功能

## 1.1 细胞膜的结构

细胞膜是细胞的外层边界，由磷脂双分子层构成。细胞膜具有选择性通透性，能够控制物质的进出。膜蛋白以镶嵌、贯穿或附着的方式分布在脂双层中，承担运输、识别、催化等功能。流动镶嵌模型是目前公认的细胞膜结构模型。

## 1.2 物质的跨膜运输

物质跨膜运输的方式包括被动运输和主动运输。被动运输不需要消耗能量，包括自由扩散和协助扩散。主动运输需要消耗ATP，可以逆浓度梯度运输物质。胞吞和胞吐是大分子物质进出细胞的方式。

## 1.3 细胞信号转导

细胞通过信号分子进行通讯。信号转导过程包括信号的接收、转换和响应。受体蛋白识别信号分子后，通过第二信使系统将信号放大并传递到细胞内，最终引发细胞反应。

# 第二章 神经系统

## 2.1 神经元的结构

神经元是神经系统的基本功能单位，由细胞体、树突和轴突组成。树突负责接收信号，轴突负责传出信号。轴突末梢形成突触，与其他神经元或效应器建立联系。

## 2.2 神经冲动的传导

神经冲动以电信号的形式在神经纤维上传导。动作电位是神经冲动的基本形式，由钠离子内流和钾离子外流产生。静息电位约为-70mV，动作电位可达+30mV。

## 2.3 突触传递

突触是神经元之间的连接点。神经递质在突触传递中起重要作用。当动作电位到达突触前膜时，突触小泡释放神经递质到突触间隙，与突触后膜上的受体结合，引发突触后电位。

# 第三章 免疫系统

## 3.1 免疫系统的组成

免疫系统由免疫器官、免疫细胞和免疫活性物质组成。免疫器官包括骨髓、胸腺、脾脏、淋巴结等。免疫细胞包括T细胞、B细胞、巨噬细胞等。

## 3.2 非特异性免疫

非特异性免疫是机体的第一道防线，包括皮肤和黏膜的屏障作用、吞噬细胞的吞噬作用、以及补体系统等。非特异性免疫不针对特定病原体，反应迅速。

## 3.3 特异性免疫

特异性免疫包括细胞免疫和体液免疫。T细胞介导细胞免疫，直接杀伤靶细胞。B细胞介导体液免疫，产生抗体与抗原结合。记忆细胞使机体在再次接触相同抗原时能快速反应。"""


@router.post("/load")
async def load_demo(db: AsyncSession = Depends(get_db)):
    """加载演示数据（快速展示用）"""
    # 检查是否已存在
    result = await db.execute(
        select(Textbook).where(Textbook.textbook_id == DEMO_TEXTBOOK_ID)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {"message": "演示数据已加载", "textbook_id": DEMO_TEXTBOOK_ID}

    # 创建教材记录
    textbook = Textbook(
        textbook_id=DEMO_TEXTBOOK_ID,
        filename="医学基础知识.md",
        title="医学基础知识（演示）",
        format="md",
        total_pages=1,
        total_chars=len(DEMO_CONTENT),
        upload_time=parser.now(),
        parse_status=ParseStatus.COMPLETED
    )
    db.add(textbook)

    # 解析章节
    chapters = []
    current_chapter = None
    chapter_content = []
    chapter_id = 0

    for line in DEMO_CONTENT.split("\n"):
        if line.startswith("# ") or line.startswith("## "):
            if current_chapter and chapter_content:
                chapter_id += 1
                ch_content = "\n".join(chapter_content)
                chapters.append(Chapter(
                    chapter_id=f"{DEMO_TEXTBOOK_ID}_ch_{chapter_id:02d}",
                    textbook_id=DEMO_TEXTBOOK_ID,
                    title=current_chapter,
                    page_start=1, page_end=1,
                    content=ch_content,
                    char_count=len(ch_content)
                ))
            current_chapter = line.lstrip("# ").strip()
            chapter_content = []
        else:
            chapter_content.append(line)

    if current_chapter and chapter_content:
        chapter_id += 1
        ch_content = "\n".join(chapter_content)
        chapters.append(Chapter(
            chapter_id=f"{DEMO_TEXTBOOK_ID}_ch_{chapter_id:02d}",
            textbook_id=DEMO_TEXTBOOK_ID,
            title=current_chapter,
            page_start=1, page_end=1,
            content=ch_content,
            char_count=len(ch_content)
        ))

    for chapter in chapters:
        db.add(chapter)

    # 预置知识点（跳过LLM调用）
    demo_nodes = _build_demo_nodes()
    for node in demo_nodes:
        db.add(node)

    # 预置关系
    demo_edges = _build_demo_edges(demo_nodes)
    for edge in demo_edges:
        db.add(edge)

    await db.commit()

    return {
        "message": "演示数据加载成功",
        "textbook_id": DEMO_TEXTBOOK_ID,
        "chapters_count": len(chapters),
        "nodes_count": len(demo_nodes),
        "edges_count": len(demo_edges)
    }


@router.delete("/clear")
async def clear_demo(db: AsyncSession = Depends(get_db)):
    """清除演示数据"""
    result = await db.execute(
        select(Textbook).where(Textbook.textbook_id == DEMO_TEXTBOOK_ID)
    )
    textbook = result.scalar_one_or_none()
    if not textbook:
        return {"message": "无演示数据"}
    await db.delete(textbook)
    await db.commit()
    return {"message": "演示数据已清除"}


def _build_demo_nodes():
    """构建演示知识点"""
    nodes_data = [
        ("细胞膜", "细胞膜是细胞的外层边界，由磷脂双分子层构成，具有选择性通透性", "核心概念", "ch_02"),
        ("磷脂双分子层", "磷脂双分子层是细胞膜的基本骨架，亲水头朝外，疏水尾朝内", "核心概念", "ch_02"),
        ("流动镶嵌模型", "流动镶嵌模型是公认的细胞膜结构模型，描述膜蛋白在脂双层中的分布", "核心概念", "ch_02"),
        ("膜蛋白", "膜蛋白以镶嵌、贯穿或附着方式分布在脂双层中，承担运输、识别、催化功能", "核心概念", "ch_02"),
        ("被动运输", "被动运输不需要消耗能量，包括自由扩散和协助扩散两种方式", "核心概念", "ch_03"),
        ("主动运输", "主动运输需要消耗ATP，可以逆浓度梯度运输物质", "核心概念", "ch_03"),
        ("自由扩散", "自由扩散是物质从高浓度向低浓度运输的过程，不需要载体蛋白", "核心概念", "ch_03"),
        ("协助扩散", "协助扩散需要载体蛋白或通道蛋白协助，但不消耗能量", "核心概念", "ch_03"),
        ("信号转导", "细胞通过信号分子进行通讯，包括信号的接收、转换和响应", "核心概念", "ch_04"),
        ("受体蛋白", "受体蛋白识别信号分子后，通过第二信使系统将信号放大传递", "核心概念", "ch_04"),
        ("神经元", "神经元是神经系统的基本功能单位，由细胞体、树突和轴突组成", "核心概念", "ch_06"),
        ("树突", "树突负责接收其他神经元传来的信号", "核心概念", "ch_06"),
        ("轴突", "轴突负责将神经冲动传出到其他神经元或效应器", "核心概念", "ch_06"),
        ("动作电位", "动作电位是神经冲动的基本形式，由钠离子内流和钾离子外流产生", "定理", "ch_07"),
        ("静息电位", "静息电位约为-70mV，由钾离子外流维持", "定理", "ch_07"),
        ("突触", "突触是神经元之间的连接点，包括突触前膜、突触间隙和突触后膜", "核心概念", "ch_08"),
        ("神经递质", "神经递质在突触传递中起重要作用，由突触前膜释放", "核心概念", "ch_08"),
        ("免疫系统", "免疫系统由免疫器官、免疫细胞和免疫活性物质组成", "核心概念", "ch_10"),
        ("T细胞", "T细胞介导细胞免疫，直接杀伤靶细胞", "核心概念", "ch_12"),
        ("B细胞", "B细胞介导体液免疫，产生抗体与抗原结合", "核心概念", "ch_12"),
        ("非特异性免疫", "非特异性免疫是机体的第一道防线，包括皮肤和黏膜的屏障作用", "核心概念", "ch_11"),
        ("特异性免疫", "特异性免疫包括细胞免疫和体液免疫，具有记忆性", "核心概念", "ch_12"),
    ]

    nodes = []
    for name, definition, category, ch in nodes_data:
        node = KnowledgeNode(
            node_id=f"{DEMO_TEXTBOOK_ID}_node_{str(uuid.uuid4())[:8]}",
            name=name, definition=definition, category=category,
            textbook_id=DEMO_TEXTBOOK_ID,
            chapter_id=f"{DEMO_TEXTBOOK_ID}_{ch}",
            page=1
        )
        nodes.append(node)
    return nodes


def _build_demo_edges(nodes):
    """构建演示关系"""
    name_to_node = {n.name: n for n in nodes}
    edges_data = [
        ("细胞膜", "磷脂双分子层", "contains", "细胞膜由磷脂双分子层构成"),
        ("细胞膜", "膜蛋白", "contains", "细胞膜中镶嵌有多种膜蛋白"),
        ("磷脂双分子层", "流动镶嵌模型", "applies_to", "磷脂双分子层是流动镶嵌模型的核心"),
        ("被动运输", "自由扩散", "contains", "自由扩散属于被动运输"),
        ("被动运输", "协助扩散", "contains", "协助扩散属于被动运输"),
        ("细胞膜", "被动运输", "applies_to", "细胞膜控制被动运输过程"),
        ("细胞膜", "主动运输", "applies_to", "细胞膜控制主动运输过程"),
        ("信号转导", "受体蛋白", "prerequisite", "信号转导需要受体蛋白识别信号"),
        ("细胞膜", "信号转导", "applies_to", "信号转导发生在细胞膜上"),
        ("神经元", "树突", "contains", "树突是神经元的组成部分"),
        ("神经元", "轴突", "contains", "轴突是神经元的组成部分"),
        ("动作电位", "静息电位", "prerequisite", "动作电位以静息电位为基础"),
        ("突触", "神经递质", "contains", "突触传递依赖神经递质"),
        ("轴突", "突触", "prerequisite", "轴突末梢形成突触"),
        ("免疫系统", "T细胞", "contains", "T细胞是免疫系统的重要组成"),
        ("免疫系统", "B细胞", "contains", "B细胞是免疫系统的重要组成"),
        ("免疫系统", "非特异性免疫", "contains", "非特异性免疫是免疫系统的一部分"),
        ("免疫系统", "特异性免疫", "contains", "特异性免疫是免疫系统的一部分"),
        ("特异性免疫", "T细胞", "contains", "T细胞介导特异性免疫中的细胞免疫"),
        ("特异性免疫", "B细胞", "contains", "B细胞介导特异性免疫中的体液免疫"),
    ]

    edges = []
    for src, tgt, rel, desc in edges_data:
        if src in name_to_node and tgt in name_to_node:
            edge = KnowledgeEdge(
                edge_id=f"edge_{str(uuid.uuid4())[:8]}",
                source_node_id=name_to_node[src].node_id,
                target_node_id=name_to_node[tgt].node_id,
                relation_type=rel, description=desc
            )
            edges.append(edge)
    return edges
