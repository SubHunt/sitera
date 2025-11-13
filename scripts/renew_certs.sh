#!/bin/bash

# Script to renew SSL certificates using Certbot

# Navigate to the project directory
cd /var/www/sitera

# Renew certificates
docker-compose -f docker-compose.prod.yml exec certbot renew

# Reload nginx to apply new certificates
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "SSL certificates renewal process completed: $(date)"