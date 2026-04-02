#!/bin/sh

(source ../.env && pg_restore \
  -h ${DB_HOST} \
  -p ${DB_PORT} \
  -U ${DB_USER} \
  --clean \
  --if-exists \
  -d ${DB_NAME} \
  $1