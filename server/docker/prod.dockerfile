FROM python:3.6-jessie

COPY app.py /app/
COPY private.py /app/
COPY data_access/*.py /app/data_access/
COPY schemas/*.json /app/schemas/

RUN apt-get update && \
    apt-get install -y gcc

RUN pip install Flask==0.12.2 fastnumbers h5py gunicorn jsonschema greenlet eventlet redis pyarrow==0.8.0 pandas==0.23.0 psutil msgpack shapeshifter

ENV GENEY_DATA_PATH=/app/data
ENV GUNICORN_CMD_ARGS="--workers=4 --bind=:8888 --worker-class=eventlet --worker-connections 100"
ENV GENEY_URL=http://kumiko.byu.edu

RUN mkdir /app/downloads/
ENV DOWNLOAD_LOCATION=/app/downloads/

WORKDIR /app/

CMD [ "gunicorn", "app:app" ]
