FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY medical_dashboard.py .

EXPOSE 8501

CMD ["streamlit", "run", "medical_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]