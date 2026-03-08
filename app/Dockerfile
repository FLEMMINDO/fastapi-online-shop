FROM python:3.12-alpine

ENV HOME=/home/fastapi_shop \
    APP_HOME=/home/fastapi_shop/app \
	LOGS_PATH=/var/logs \
    PYTHONPATH="$PYTHONPATH:/home/fastapi_shop" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p $APP_HOME \
  && mkdir -p $LOGS_PATH \
  && addgroup -S fast \
  && adduser -S fast -G fast

WORKDIR $HOME
 
COPY app app
COPY requirements.txt alembic.ini .env .

RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && chown -R fast:fast . \
 && chown -R fast:fast /var/logs
 
 USER fast