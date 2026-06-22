FROM python:3.11-slim
WORKDIR /app
COPY apps/api ./apps/api
COPY examples ./examples
WORKDIR /app/apps/api
RUN pip install --no-cache-dir -e .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
