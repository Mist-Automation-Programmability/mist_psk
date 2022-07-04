# Mist Psk Dashboard
This application provides a single page app to manage, create, edit and delete Personal PSKs from Mist Cloud. It is required to have a Mist account to get access to this app.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

<img src="https://github.com/tmunzer/mist_psk/blob/master/._readme/img/main.png?raw=true" width="50%"/>

## MIT LICENSE
 
Copyright (c) 2021 Thomas Munzer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the  Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Features
- Retrieve and display Org and Site PPSKs 
- Edit Org or Site PPSK
- Create new Org or Site PPSK
- Delete Org or Site PPSK
- Display Configuration QRCode for smartphone
- Send email to user with SSID and PPSK information, and QRCode for smartphone configuration

<img src="https://github.com/tmunzer/mist_psk/blob/master/._readme/img/create.png?raw=true" width="30%" />
<img src="https://github.com/tmunzer/mist_psk/blob/master/._readme/img/qrcode.png?raw=true" width="30%" />


## Installation

This is a demo application using the Mist APIs.

You can run it as a strandalone Python application, or deploy it as a Docker container.

**Note**: The application is not providing secured HTTPS connections. It is highly recommended to deploy it behind a reverse proxy providing HTTPS encryption.

### Standalone deployment
1. download the github repository
2. from the project folder, install the python dependencies (ex: `pip3 install -r requirements.txt`)
3. create a `config.py` file in the directory `django/backend/` with the required settings. A configuration example with explanation is avaiable in  `django/backend/config_example.py`. 
4. from the `django_app`folder, start the app with `python3 ./manage.py runserver` (please see Djano server options with `python3 ./manage.py runserver -h`)

### Docker Image
The docker image is available on docker hub: https://hub.docker.com/repository/docker/tmunzer/mist_psk.


The Docket image is listening on port TCP8000


## Configuration
You can configure the settings through a configuration file or through Environment Variables.

### Environment Variables
| Variable Name | Type | Default Value | Comment |
| ------------- | ---- | ------------- | ------- |
MIST_SMTP_ENABLED | Boolean | False | Whether or not to allow to send PSK by email |
MIST_SMTP_HOST | String |	None | SMTP Server IP or hostname |
MIST_SMTP_PORT | Number | 587 | SMTP Server Port  |
MIST_SMTP_SSL | Boolean | True | Whether or not to use SSL to talk with the SMTP Server |
MIST_SMTP_USER | String | None | If SMTP server requires authentication, the username to use |
MIST_SMTP_PASSWORD | String | None | If SMTP server requires authentication, the password to use |
MIST_SMTP_FROM_NAME | String | Wi-Fi Access | Email sender name |
MIST_SMTP_FROM_EMAIL | String | None | Sender email address  |
MIST_SMTP_LOGO_URL | String | https://cdn.mist.com/wp-content/uploads/logo.png | Logo displayed in the email header |
MIST_SMTP_QRCODE | Boolean | True | Whether or not add an autoconfiguration QRCode for smartphones to the email |
MIST_PSK_SALT | String | $2b$12$SIGWr574/7OggDO4BBJ1D. | Salt for "renewable" PSK generation |
MIST_PSK_LENGTH | Number | 12 | Size for "renewable" PSK length (must be between 8 and 63 |
MIST_PSK_DEFAULT_EXPIRE_TIME | Number | 0 | Default Expire time for PSK creation, in hours. 0 to disable |
DJANGO_DEBUG | Number | 0 | Whether or not Django starts in Debug Mode (0=Production, 1=Debug) |
DJANGO_ALLOWED_HOSTS | String |  | FQDN on which Django is listening. Only used in Production Mode |
