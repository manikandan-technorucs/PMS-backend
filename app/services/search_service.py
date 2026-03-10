from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.project import Project
from app.models.task import Task
from app.models.issue import Issue

class SearchService:
    def global_search(self, db: Session, query: str, limit: int = 15):
        if not query:
            return []
        
        search_results = []
        q = f"%{query}%"

        # Search Projects
        projects = db.query(Project).filter(
            or_(
                Project.name.ilike(q),
                Project.public_id.ilike(q),
                Project.client.ilike(q)
            )
        ).limit(limit).all()
        
        for p in projects:
            search_results.append({
                "type": "project",
                "id": p.public_id,
                "title": p.name,
                "path": f"/projects/{p.id}"
            })

        # Search Tasks
        tasks = db.query(Task).filter(
            or_(
                Task.title.ilike(q),
                Task.public_id.ilike(q)
            )
        ).limit(limit).all()
        
        for t in tasks:
            search_results.append({
                "type": "task",
                "id": t.public_id,
                "title": t.title,
                "path": f"/tasks/{t.id}"
            })

        # Search Issues
        issues = db.query(Issue).filter(
            or_(
                Issue.title.ilike(q),
                Issue.public_id.ilike(q)
            )
        ).limit(limit).all()
        
        for i in issues:
            search_results.append({
                "type": "issue",
                "id": i.public_id,
                "title": i.title,
                "path": f"/issues/{i.id}"
            })

        return search_results

search_service = SearchService()
