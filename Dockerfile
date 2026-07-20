FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY sales_pipeline ./sales_pipeline
COPY sql ./sql
COPY sample_data ./sample_data
RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "sales_pipeline"]
CMD ["all"]

