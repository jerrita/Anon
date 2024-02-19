FROM python:3.10-alpine

COPY . /repo
RUN pip install -r /repo/requirements.txt \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT "/repo/entrypoint.sh"