FROM python:3.11-slim
WORKDIR /usr/src/app
RUN apt-get update && \
    apt-get install -y --no-install-recommends git
RUN git clone https://github.com/lucio-modrono/python-htspclient
RUN apt-get remove -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR python-htspclient
RUN pip install -e /usr/src/app/python-htspclient
ENTRYPOINT ["python", "./scripts/htsp_ops.py"]
