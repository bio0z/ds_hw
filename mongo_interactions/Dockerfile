FROM alpine:edge

RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

RUN apk update && apk upgrade && apk --no-cache --update-cache add mongodb su-exec curl mongodb-tools nano


COPY ./agg.js /home/
COPY ./hw5.sh /home/
