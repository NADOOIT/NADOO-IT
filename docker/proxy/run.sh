#!/bin/bash


set -e

echo "Checking for dhparams.pem"

if [ ! -f "/vol/proxy/ssl-dhparams.pem"]; then
    echo "dhparams.pem does not exist, generating"
    openssl dhparam -out /vol/proxy/ssl-dhparams.pem 2048
fi

# Acoid replacing these with envsubst, as it will replace the $ in the dhparams file

export host=\$host
export request_uri=\$request_uri

echo "Checking for fullchain.pem"

if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "No SSL cert, enabling HTTP only..."
    envsubset < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
else
    echo "SSL cert found, enabling HTTPS..."
    envsubst < /etc/nginx/default-ssl.conf.tpl > /etc/nginx/conf.d/default.conf
fi

nginx -g "daemon off;"
