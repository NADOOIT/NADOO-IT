#TODO Check for new versions of the base image. If a new version is available, rebuild the image.
FROM certbot/certbot:v1.27.0

COPY certify-init.sh /opt/
RUN chmod +x /opt/certify-init.sh

ENTRYPOINT []
CMD ["certbot", "renew"]