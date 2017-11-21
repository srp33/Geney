FROM python:3.6-jessie

COPY app.py /app/
COPY data_access/*.py /app/data_access/
COPY schemas/*.json /app/schemas/
COPY responders/*.py /app/responders/

RUN apt-get update && \
    apt-get install -y gcc

RUN pip install Flask==0.12.2 fastnumbers h5py gunicorn jsonschema greenlet eventlet

WORKDIR /app/

CMD [ "gunicorn", "app:app" ]