from flask import Blueprint, jsonify, request

from viberbot.auth import require_api_key
from viberbot.services import state

bp = Blueprint("dashboard_api", __name__, url_prefix="/api")


@bp.route("/conversations", methods=["GET"])
@require_api_key
def list_conversations():
    return jsonify(state.list_conversations()), 200


@bp.route("/conversations/<sender>", methods=["GET"])
@require_api_key
def get_conversation(sender):
    return jsonify({"sender": sender, "history": state.get_history(sender)}), 200


@bp.route("/conversations/<sender>", methods=["DELETE"])
@require_api_key
def reset_conversation(sender):
    state.clear_conversation(sender)
    return jsonify({"status": "cleared", "sender": sender}), 200


@bp.route("/agent-queue", methods=["GET"])
@require_api_key
def agent_queue():
    return jsonify(state.list_agent_queue()), 200


@bp.route("/templates", methods=["GET"])
@require_api_key
def list_templates():
    return jsonify(state.list_templates()), 200


@bp.route("/templates", methods=["POST"])
@require_api_key
def create_template():
    data = request.json or {}
    key = data.get("key")
    template_id = data.get("id")
    language = data.get("language", "bg")
    params = data.get("params", [])
    description = data.get("description")

    if not key or not template_id:
        return jsonify({"status": "error", "message": "'key' and 'id' are required"}), 400

    template = state.upsert_template(key, template_id, language, params, description)
    return jsonify(template), 201


@bp.route("/templates/<key>", methods=["PUT"])
@require_api_key
def update_template(key):
    existing = state.get_template(key)
    if not existing:
        return jsonify({"status": "error", "message": f"Template '{key}' not found"}), 404

    data = request.json or {}
    template = state.upsert_template(
        key,
        data.get("id", existing["id"]),
        data.get("language", existing["language"]),
        data.get("params", existing["params"]),
        data.get("description", existing["description"]),
    )
    return jsonify(template), 200


@bp.route("/templates/<key>", methods=["DELETE"])
@require_api_key
def delete_template(key):
    if not state.delete_template(key):
        return jsonify({"status": "error", "message": f"Template '{key}' not found"}), 404
    return jsonify({"status": "deleted", "key": key}), 200
