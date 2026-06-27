"""群问答知识库 · 纯本地数据存储"""

import json
import re
import time
from pathlib import Path


# 数据目录 — 改为同步网盘路径即可多人共享
# 例：DATA_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/群问答库"
DATA_DIR = Path.home() / ".qa_kb"
DATA_FILE = DATA_DIR / "qa_data.json"


def _ensure():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def _save(data):
    _ensure()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_qa(question, ta_answer="", teacher_supplement="",
           tags="", asker=""):
    """添加一条问答"""
    data = _load()
    record = {
        "id": int(time.time() * 1000),
        "question": question.strip(),
        "ta_answer": ta_answer.strip(),
        "teacher_supplement": teacher_supplement.strip(),
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "asker": asker.strip(),
        "created_at": time.time(),
        "created_at_str": time.strftime("%Y-%m-%d %H:%M"),
    }
    data.insert(0, record)
    _save(data)
    return record


def update_qa(qid, ta_answer="", teacher_supplement="", tags="", asker=""):
    """更新问答"""
    data = _load()
    for r in data:
        if r["id"] == qid:
            if ta_answer:
                r["ta_answer"] = ta_answer.strip()
            if teacher_supplement:
                r["teacher_supplement"] = teacher_supplement.strip()
            if tags:
                r["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
            if asker:
                r["asker"] = asker.strip()
            _save(data)
            return True
    return False


def delete_qa(qid):
    """删除问答"""
    data = _load()
    data = [r for r in data if r["id"] != qid]
    _save(data)


def search(query, tag="") -> list:
    """搜索问答"""
    data = _load()
    query = query.lower().strip()
    results = []
    for r in data:
        score = 0
        if query and query in r["question"].lower():
            score += 10
        if query and query in r["ta_answer"].lower():
            score += 5
        if query and query in r["teacher_supplement"].lower():
            score += 3
        if query and query in r["asker"].lower():
            score += 2
        if tag and tag in r["tags"]:
            score += 8
        if not query and not tag:
            score = 1
        if score > 0:
            results.append((score, r))
    results.sort(key=lambda x: -x[0])
    return [r for _, r in results]


def get_all_tags() -> list:
    """获取所有标签"""
    data = _load()
    tags = set()
    for r in data:
        tags.update(r.get("tags", []))
    return sorted(tags)


def count():
    return len(_load())
