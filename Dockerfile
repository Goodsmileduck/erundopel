FROM python:3.6-alpine3.7

ENV DIR /app

COPY requirements.txt ${DIR}/requirements.txt
RUN apk add --no-cache build-base git\
  && pip install -r ${DIR}/requirements.txt\
  && apk del build-base git
EXPOSE 5000

COPY ./app /app
WORKDIR ${DIR}
CMD ["python", "app.py"]
