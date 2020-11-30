#!/bin/bash

app="vidulum.dev"
docker build -f ./dev.Dockerfile -t ${app} .
docker run --rm -it \
       -p $VIDULUM_DEV_PORT:80 \
       -e DB_USER_USERNAME=$DB_USER_USERNAME \
       -e DB_USER_PASSWORD=$DB_USER_PASSWORD \
       -e DB_MONGO_LINK=$DB_MONGO_LINK \
       -e DB_MONGO_DATABASE=$DB_MONGO_DATABASE \
       --name ${app} \
       -v $PWD:/app \
       ${app} python /app/Vidulum/app.py
