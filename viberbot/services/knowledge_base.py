import glob
import os
import re

from viberbot import config


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

    all_chunks = list(KNOWLEDGE_CHUNKS)

    # Also search user-managed knowledge entries stored in the DB.
    try:
        from viberbot.db import KnowledgeEntry
        for entry in KnowledgeEntry.query.all():
            all_chunks.append(f"# {entry.title}\n{entry.content}")
    except Exception:
        pass

    scored = []
    for chunk in all_chunks:
        chunk_words = set(re.findall(r"\w+", chunk.lower()))
        overlap = len(query_words & chunk_words)
        if overlap > 0:
            scored.append((overlap, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_n]]
