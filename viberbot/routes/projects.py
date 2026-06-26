from flask import Blueprint, g, jsonify, request

from viberbot.auth import require_session
from viberbot.services import projects

bp = Blueprint("projects", __name__, url_prefix="/api")


@bp.route("/projects", methods=["GET"])
@require_session
def list_projects():
    return jsonify(projects.list_projects()), 200


@bp.route("/projects", methods=["POST"])
@require_session
def create_project():
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"status": "error", "message": "'name' is required"}), 400
    return jsonify(projects.create_project(name, data.get("description"), g.user.id)), 201


@bp.route("/projects/<int:project_id>", methods=["GET"])
@require_session
def get_project(project_id):
    p = projects.get_project(project_id)
    if not p:
        return jsonify({"status": "error", "message": "Project not found"}), 404
    return jsonify(p), 200


@bp.route("/projects/<int:project_id>", methods=["PUT"])
@require_session
def update_project(project_id):
    data = request.json or {}
    p = projects.update_project(project_id, data.get("name"), data.get("description"))
    if not p:
        return jsonify({"status": "error", "message": "Project not found"}), 404
    return jsonify(p), 200


@bp.route("/projects/<int:project_id>", methods=["DELETE"])
@require_session
def delete_project(project_id):
    if not projects.delete_project(project_id):
        return jsonify({"status": "error", "message": "Project not found"}), 404
    return jsonify({"status": "deleted", "id": project_id}), 200


@bp.route("/projects/<int:project_id>/sprints", methods=["GET"])
@require_session
def list_sprints(project_id):
    return jsonify(projects.list_sprints(project_id)), 200


@bp.route("/projects/<int:project_id>/sprints", methods=["POST"])
@require_session
def create_sprint(project_id):
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"status": "error", "message": "'name' is required"}), 400
    return jsonify(projects.create_sprint(project_id, name, data.get("start_date"), data.get("end_date"))), 201


@bp.route("/sprints/<int:sprint_id>", methods=["PUT"])
@require_session
def update_sprint(sprint_id):
    data = request.json or {}
    s = projects.update_sprint(sprint_id, **data)
    if not s:
        return jsonify({"status": "error", "message": "Sprint not found"}), 404
    return jsonify(s), 200


@bp.route("/sprints/<int:sprint_id>", methods=["DELETE"])
@require_session
def delete_sprint(sprint_id):
    if not projects.delete_sprint(sprint_id):
        return jsonify({"status": "error", "message": "Sprint not found"}), 404
    return jsonify({"status": "deleted", "id": sprint_id}), 200


@bp.route("/tasks", methods=["GET"])
@require_session
def list_tasks():
    project_id = request.args.get("project_id", type=int)
    sprint_id = request.args.get("sprint_id", type=int)
    status = request.args.get("status")
    return jsonify(projects.list_tasks(project_id, sprint_id, status)), 200


@bp.route("/triage", methods=["GET"])
@require_session
def triage_inbox():
    return jsonify(projects.list_triage_tasks()), 200


@bp.route("/tasks", methods=["POST"])
@require_session
def create_task():
    data = request.json or {}
    title = data.get("title")
    if not title:
        return jsonify({"status": "error", "message": "'title' is required"}), 400
    task = projects.create_task(
        title=title,
        description=data.get("description"),
        project_id=data.get("project_id"),
        status=data.get("status"),
        priority=data.get("priority", "none"),
        assignee_id=data.get("assignee_id"),
        created_by=g.user.id,
    )
    return jsonify(task), 201


@bp.route("/tasks/<int:task_id>", methods=["PUT"])
@require_session
def update_task(task_id):
    data = request.json or {}
    task = projects.update_task(task_id, **data)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404
    return jsonify(task), 200


@bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@require_session
def delete_task(task_id):
    if not projects.delete_task(task_id):
        return jsonify({"status": "error", "message": "Task not found"}), 404
    return jsonify({"status": "deleted", "id": task_id}), 200


@bp.route("/projects/<int:project_id>/docs", methods=["GET"])
@require_session
def list_docs(project_id):
    return jsonify(projects.list_docs(project_id)), 200


@bp.route("/projects/<int:project_id>/docs", methods=["POST"])
@require_session
def create_doc(project_id):
    data = request.json or {}
    title = data.get("title")
    if not title:
        return jsonify({"status": "error", "message": "'title' is required"}), 400
    doc = projects.create_doc(project_id, title, data.get("content", ""), g.user.id)
    return jsonify(doc), 201


@bp.route("/docs/<int:doc_id>", methods=["GET"])
@require_session
def get_doc(doc_id):
    d = projects.get_doc(doc_id)
    if not d:
        return jsonify({"status": "error", "message": "Doc not found"}), 404
    return jsonify(d), 200


@bp.route("/docs/<int:doc_id>", methods=["PUT"])
@require_session
def update_doc(doc_id):
    data = request.json or {}
    d = projects.update_doc(doc_id, data.get("title"), data.get("content"))
    if not d:
        return jsonify({"status": "error", "message": "Doc not found"}), 404
    return jsonify(d), 200


@bp.route("/docs/<int:doc_id>", methods=["DELETE"])
@require_session
def delete_doc(doc_id):
    if not projects.delete_doc(doc_id):
        return jsonify({"status": "error", "message": "Doc not found"}), 404
    return jsonify({"status": "deleted", "id": doc_id}), 200
