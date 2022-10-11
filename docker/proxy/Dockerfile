#FROM nginx:1.23.0-alpine
FROM nginxinc/nginx-unprivileged:1.23.0-alpine

COPY ./nginx/* /etc/nginx/
COPY run.sh /run.sh

ENV APP_HOST=app
ENV APP_PORT=9090


USER root

RUN apk add --no-cache openssl bash
RUN chmod +x /run.sh

RUN mkdir -p /vol/web/static
RUN chmod -R 755 /vol/web/static

VOLUME /vol/web
VOLUME /vol/www

USER nginx

CMD ["/run.sh"]