web: gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
worker: celery -A src.workers.celery_app worker --loglevel=info
beat: celery -A src.workers.celery_app beat --loglevel=info
frontend: streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0
