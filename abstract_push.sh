#!/usr/bin/env bash

FILENAME=$( echo $1 |cut -d"." -f1)
HANDLER_NAME=$( echo $2 |cut -d"." -f1)
AWS_ROLE=$( echo $3 )

zip -r $PWD/${FILENAME}.zip $PWD/$1

aws lambda create-function \
--region eu-central-1 \
--function-name $FILENAME \
--zip-file resturant_get_raiting.zip \
--role $AWS_ROLE  \
--handler $FILENAME.$HANDLER_NAME \
--runtime python3.6 \
--timeout 15 \
--memory-size 512