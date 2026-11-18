ARG PYTHON_IMAGE=python:3.13-alpine@sha256:bf12ecc0bea3f171d55145dd02c78b5eeb09f30ee2ac9cc2b4c9e4e8f5e30741
FROM ${PYTHON_IMAGE}
RUN rm -rf /usr/local/lib/python3.13/site-packages/pip* /usr/local/lib/python3.13/ensurepip /usr/local/bin/pip*
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY contact.py /app/contact.py
USER 10001:10001
CMD ["python", "/app/contact.py", "--api-only", "--bind", "0.0.0.0", "--port", "8081"]
