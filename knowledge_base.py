import glob
import os
import re

import config


def load_knowledge_chunks():
    chunks = []
    for path in glob.glob(os.path.join(config.KNOWLEDGE_DIR, "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        sections = re.split(r"\n(?=#{1,3} )", content)
        chunks.extend(section.strip() for section in sections if section.strip())
    return chunks


KNOWLEDGE_CHUNKS = load_knowledge_chunks()
print(f"Loaded {len(KNOWLEDGE_CHUNKS)} knowledge chunks")


def find_relevant_chunks(query, top_n=3):
    query_words = set(re.findall(r"\w+", query.lower()))
    if not query_words:
        return []

    scored = []
    for chunk in KNOWLEDGE_CHUNKS:
        chunk_words = set(re.findall(r"\w+", chunk.lower()))
        overlap = len(query_words & chunk_words)
        if overlap > 0:
            scored.append((overlap, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_n]]
