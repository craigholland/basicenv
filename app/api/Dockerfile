FROM python:3.12 as python_pkg_installer
WORKDIR /app
COPY dockerbuild/domain domain
COPY dockerbuild/database database
COPY requirements.txt /app/
COPY docker-entrypoint.sh /app



RUN apt-get update

RUN pip install -r requirements.txt

FROM python_pkg_installer
COPY services /app/services
COPY build.sh /app
COPY docker-entrypoint.sh .
COPY main.py /app
EXPOSE 8081
ENV FLASK_APP=main.py
ENV PYTHONPATH /app:/app/services/build/lib

LABEL authors="rook"

ENTRYPOINT ["bash", "docker-entrypoint.sh"]