from flask import Blueprint, jsonify, request

from viberbot.auth import get_current_user, require_admin, require_session
from viberbot.db import KnowledgeEntry, db
from viberbot.services.knowledge_base import KNOWLEDGE_CHUNKS

bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")


@bp.route("/", methods=["GET"], strict_slashes=False)
@require_session
@require_admin
def list_entries():
    entries = KnowledgeEntry.query.order_by(KnowledgeEntry.updated_at.desc()).all()
    return jsonify({
        "entries": [e.to_dict() for e in entries],
        "file_chunks": len(KNOWLEDGE_CHUNKS),
    })


@bp.route("/", methods=["POST"], strict_slashes=False)
@require_session
@require_admin
def create_entry():
    data = request.json or {}
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    if not title or not content:
        return jsonify({"status": "error", "message": "'title' and 'content' are required"}), 400

    user = get_current_user()
    entry = KnowledgeEntry(title=title, content=content, created_by=user.id if user else None)
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@bp.route("/<int:entry_id>", methods=["PUT"])
@require_session
@require_admin
def update_entry(entry_id):
    entry = KnowledgeEntry.query.get_or_404(entry_id)
    data = request.json or {}
    if "title" in data:
        entry.title = data["title"].strip()
    if "content" in data:
        entry.content = data["content"].strip()
    if not entry.title or not entry.content:
        return jsonify({"status": "error", "message": "'title' and 'content' cannot be empty"}), 400
    db.session.commit()
    return jsonify(entry.to_dict())


@bp.route("/<int:entry_id>", methods=["DELETE"])
@require_session
@require_admin
def delete_entry(entry_id):
    entry = KnowledgeEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"status": "deleted"})
