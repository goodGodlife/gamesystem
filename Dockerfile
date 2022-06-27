FROM python:3.10-alpine
RUN pip install -U pip
RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com
RUN sed -i 's@dl-cdn.alpinelinux.org@mirrors.aliyun.com@g' /etc/apk/repositories

RUN apk --no-cache add python3-dev build-base linux-headers pcre-dev
ADD ./ /app/

WORKDIR /app/
RUN pip install --no-cache-dir -r require.txt


EXPOSE 5000
CMD flask run --host=0.0.0.0 --port=5000