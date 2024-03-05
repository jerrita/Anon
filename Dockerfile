FROM python:3.10-alpine

COPY . /repo

RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && pip install uv \
    && uv pip install --system -r /repo/requirements.txt \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["/repo/entrypoint.sh"]
