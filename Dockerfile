FROM python:3.10-alpine

COPY . /repo
RUN pip install -r /repo/requirements.txt

ENTRYPOINT "/repo/entrypoint.sh"