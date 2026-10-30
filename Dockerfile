FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

COPY requirements.txt setup.py README.md ./
COPY app.py ./
COPY config/ ./config/
COPY templates/ ./templates/
COPY books_recommender_system/ ./books_recommender_system/
COPY artifacts/serialized_objects/book_pivot.pkl ./artifacts/serialized_objects/book_pivot.pkl
COPY artifacts/serialized_objects/final_rating.pkl ./artifacts/serialized_objects/final_rating.pkl
COPY artifacts/trained_model/model.pkl ./artifacts/trained_model/model.pkl

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]
