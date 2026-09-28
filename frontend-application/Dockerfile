FROM docker.io/library/nginx:alpine

RUN apk update \
    && apk upgrade libexpat \
    && rm -rf /var/cache/apk/*

COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/nginx.conf

RUN chgrp -R 0 /var/cache/nginx /var/log/nginx /etc/nginx /usr/share/nginx/html \
    && chmod -R g=u /var/cache/nginx /var/log/nginx /etc/nginx /usr/share/nginx/html

EXPOSE 8080
