FROM python:3.11-slim
WORKDIR /usr/src/app/python-htspclient
COPY . .
WORKDIR python-htspclient
RUN pip install -e /usr/src/app/python-htspclient
ENTRYPOINT ["python", "./scripts/htsp_ops.py"]
