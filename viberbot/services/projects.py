from datetime import datetime

from viberbot.db import Doc, Project, Sprint, Task, db


def list_projects():
    return [p.to_dict() for p in Project.query.order_by(Project.created_at.desc()).all()]


def get_project(project_id):
    p = Project.query.get(project_id)
    return p.to_dict() if p else None


def create_project(name, description, created_by):
    p = Project(name=name, description=description, created_by=created_by)
    db.session.add(p)
    db.session.commit()
    return p.to_dict()


def update_project(project_id, name=None, description=None):
    p = Project.query.get(project_id)
    if not p:
        return None
    if name is not None:
        p.name = name
    if description is not None:
        p.description = description
    db.session.commit()
    return p.to_dict()


def delete_project(project_id):
    p = Project.query.get(project_id)
    if not p:
        return False
    Task.query.filter_by(project_id=project_id).delete()
    Sprint.query.filter_by(project_id=project_id).delete()
    Doc.query.filter_by(project_id=project_id).delete()
    db.session.delete(p)
    db.session.commit()
    return True


def list_sprints(project_id):
    return [s.to_dict() for s in Sprint.query.filter_by(project_id=project_id).order_by(Sprint.created_at.desc()).all()]


def create_sprint(project_id, name, start_date=None, end_date=None):
    s = Sprint(
        project_id=project_id,
        name=name,
        start_date=datetime.fromisoformat(start_date).date() if start_date else None,
        end_date=datetime.fromisoformat(end_date).date() if end_date else None,
    )
    db.session.add(s)
    db.session.commit()
    return s.to_dict()


def update_sprint(sprint_id, **fields):
    s = Sprint.query.get(sprint_id)
    if not s:
        return None
    if "name" in fields and fields["name"] is not None:
        s.name = fields["name"]
    if "status" in fields and fields["status"] is not None:
        s.status = fields["status"]
    if "start_date" in fields and fields["start_date"] is not None:
        s.start_date = datetime.fromisoformat(fields["start_date"]).date()
    if "end_date" in fields and fields["end_date"] is not None:
        s.end_date = datetime.fromisoformat(fields["end_date"]).date()
    db.session.commit()
    return s.to_dict()


def delete_sprint(sprint_id):
    s = Sprint.query.get(sprint_id)
    if not s:
        return False
    Task.query.filter_by(sprint_id=sprint_id).update({"sprint_id": None})
    db.session.delete(s)
    db.session.commit()
    return True


def list_tasks(project_id=None, sprint_id=None, status=None):
    query = Task.query
    if project_id is not None:
        query = query.filter_by(project_id=project_id)
    if sprint_id is not None:
        query = query.filter_by(sprint_id=sprint_id)
    if status is not None:
        query = query.filter_by(status=status)
    return [t.to_dict() for t in query.order_by(Task.created_at.desc()).all()]


def list_triage_tasks():
    return [t.to_dict() for t in Task.query.filter_by(status="triage").order_by(Task.created_at.desc()).all()]


def get_task(task_id):
    t = Task.query.get(task_id)
    return t.to_dict() if t else None


def create_task(title, description=None, project_id=None, status=None, priority="none", assignee_id=None, created_by=None):
    t = Task(
        title=title,
        description=description,
        project_id=project_id,
        status=status or ("triage" if not project_id else "backlog"),
        priority=priority,
        assignee_id=assignee_id,
        created_by=created_by,
    )
    db.session.add(t)
    db.session.commit()
    return t.to_dict()


def update_task(task_id, **fields):
    t = Task.query.get(task_id)
    if not t:
        return None
    for key in ("title", "description", "status", "priority", "project_id", "sprint_id", "assignee_id"):
        if key in fields and fields[key] is not None:
            setattr(t, key, fields[key])
    db.session.commit()
    return t.to_dict()


def delete_task(task_id):
    t = Task.query.get(task_id)
    if not t:
        return False
    db.session.delete(t)
    db.session.commit()
    return True


def list_docs(project_id):
    return [d.to_dict() for d in Doc.query.filter_by(project_id=project_id).order_by(Doc.updated_at.desc()).all()]


def get_doc(doc_id):
    d = Doc.query.get(doc_id)
    return d.to_dict() if d else None


def create_doc(project_id, title, content, created_by):
    d = Doc(project_id=project_id, title=title, content=content, created_by=created_by)
    db.session.add(d)
    db.session.commit()
    return d.to_dict()


def update_doc(doc_id, title=None, content=None):
    d = Doc.query.get(doc_id)
    if not d:
        return None
    if title is not None:
        d.title = title
    if content is not None:
        d.content = content
    db.session.commit()
    return d.to_dict()


def delete_doc(doc_id):
    d = Doc.query.get(doc_id)
    if not d:
        return False
    db.session.delete(d)
    db.session.commit()
    return True
