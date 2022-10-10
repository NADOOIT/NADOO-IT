#!/bin/sh

#Waits for proxy to be available, then gets the first certificate.

see -echo

until nc -z proxy 80; do
  echo "Waiting for proxy to be available..."
  sleep 5s & wait ${!}
done

echo "Proxy is available, getting certificate..."

certbot certonly certonly \
    --webroot \
    --webroot-path "/vol/www/" \
    -d "$DOMAIN" \
    --agree-tos \
    --email "$EMAIL" \
    --noninteractive \
    --rsa-key-size 4096