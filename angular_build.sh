#!/bin/bash

cd angular_src/
ng build --deploy-url static/
cp dist/psk/* ../django_app/pskGen/static
cp dist/psk/index.html ../django_app/pskGen/templates
cd ..
