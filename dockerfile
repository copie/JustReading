FROM python:3.7-alpine

VOLUME [ "/data" ]
COPY ./requirements.txt /
RUN cd /
RUN apk add --no-cache --virtual .build-deps gcc musl-dev&& \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple gunicorn&& \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple gevent&& \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /requirements.txt&& \
    apk del .build-deps gcc musl-dev
EXPOSE 8000
ENV FLASK_CONFIG=production
WORKDIR /data
CMD [ "gunicorn","manage:app","--bind=0.0.0.0:8000","-k","gevent"]
