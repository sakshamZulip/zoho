FROM python:3.9.12-buster

WORKDIR /python

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "zulip-botserver --config-file zuliprc-alfred --port 10000 --host 0.0.0.0"]