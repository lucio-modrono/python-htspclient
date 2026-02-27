FROM python:3.11-slim
WORKDIR /usr/src/app
RUN apk add --no-cache git
RUN git clone https://github.com/lucio-modrono/python-htspclient
WORKDIR python-htspclient
RUN pip install -e /usr/src/app/python-htspclient
ENTRYPOINT ["python", "./scripts/htsp_ops.py"]
