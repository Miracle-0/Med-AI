from typing import List

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """将文本分割为chunks"""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        if end < text_len:
            for i in range(end, max(start + chunk_size - 100, start), -1):
                if text[i] in "。！？\n":
                    end = i + 1
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks

def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    """提取关键词"""
    import re
    from collections import Counter

    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()

    stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
    words = [w for w in words if w not in stop_words and len(w) > 1]

    word_counts = Counter(words)
    return [word for word, _ in word_counts.most_common(top_k)]
