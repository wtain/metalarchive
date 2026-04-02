#!/bin/sh

mkdir ./backups

(source ../.env && pg_dump \
  -h ${DB_HOST} \
  -p ${DB_PORT} \
  -U ${DB_USER} \
  -Fc \
  -f ./backups/metrics_$(date +%Y%m%d_%H%M%S).dump \
  ${DB_NAME})