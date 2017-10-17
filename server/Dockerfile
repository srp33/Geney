FROM python:2.7-alpine3.6

COPY *.py /root/

RUN pip install Flask==0.12.2

WORKDIR /root/

ENTRYPOINT [ "python", "app.py" ]
