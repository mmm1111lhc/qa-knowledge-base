"""群问答知识库 · Web版 —— 学员手写提问 / TA手写录音回答 / 老师补充"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from flask import Flask, request, jsonify, send_from_directory
from database import add_qa, search, delete_qa, update_qa, get_all_tags, count, _load, _save

app = Flask(__name__, static_folder="static", static_url_path="")

# ── 上传文件保存目录 ──
UPLOAD_DIR = os.path.expanduser("~/.qa_kb/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==================== API ====================

@app.route("/")
def index():
    return send_from_directory(".", "templates/index.html")

@app.route("/api/questions")
def api_questions():
    """获取所有问答"""
    data = _load()
    tag = request.args.get("tag", "")
    role = request.args.get("role", "")  # student / ta / teacher
    results = []
    for r in data:
        if tag and tag not in r.get("tags", []):
            continue
        results.append(r)
    # 按角色过滤: student只看自己的，ta/teacher看所有
    return jsonify(results)

@app.route("/api/question", methods=["POST"])
def api_add():
    """新增问答"""
    body = request.json or {}
    q = body.get("question", "").strip()
    if not q:
        return jsonify({"error": "问题不能为空"}), 400
    r = add_qa(
        question=q,
        ta_answer=body.get("ta_answer", ""),
        teacher_supplement=body.get("teacher_supplement", ""),
        tags=body.get("tags", ""),
        asker=body.get("asker", ""),
    )
    return jsonify(r)

@app.route("/api/question/<int:qid>", methods=["PUT"])
def api_update(qid):
    """更新问答"""
    body = request.json or {}
    data = _load()
    for r in data:
        if r["id"] == qid:
            if "ta_answer" in body:
                r["ta_answer"] = body["ta_answer"].strip()
            if "teacher_supplement" in body:
                r["teacher_supplement"] = body["teacher_supplement"].strip()
            if "tags" in body:
                r["tags"] = [t.strip() for t in body["tags"].split(",") if t.strip()]
            r["updated_at"] = time.time()
            _save(data)
            return jsonify(r)
    return jsonify({"error": "not found"}), 404

@app.route("/api/question/<int:qid>", methods=["DELETE"])
def api_delete(qid):
    delete_qa(qid)
    return jsonify({"ok": True})

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """上传图片/录音文件"""
    if "file" not in request.files:
        return jsonify({"error": "no file"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "no filename"}), 400
    filename = f"{int(time.time() * 1000)}_{f.filename}"
    f.save(os.path.join(UPLOAD_DIR, filename))
    return jsonify({"url": f"/uploads/{filename}"})

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/api/stats")
def api_stats():
    data = _load()
    total = len(data)
    with_ta = sum(1 for r in data if r.get("ta_answer"))
    with_teacher = sum(1 for r in data if r.get("teacher_supplement"))
    return jsonify({"total": total, "ta_answered": with_ta, "teacher_supplemented": with_teacher})

if __name__ == "__main__":
    print("🌐 群问答知识库 · Web版")
    print("   启动: http://localhost:5000")
    print("   手机同WiFi: http://<本机IP>:5000")
    print("   按 Ctrl+C 停止")
    app.run(host="0.0.0.0", port=5000, debug=True)
