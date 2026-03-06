@echo off
echo Starting Celery Worker...
call venv\Scripts\activate.bat
celery -A app.core.celery_app worker --loglevel=info -P solo
