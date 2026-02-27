FROM python:3.11-slim
WORKDIR /usr/src/app/python-htspclient
COPY . .
RUN pip install -e /usr/src/app/python-htspclient
ENTRYPOINT ["python", "./scripts/htsp_ops.py"]
