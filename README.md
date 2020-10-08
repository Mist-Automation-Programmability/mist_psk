# Mist Psk Web UI
 
This application provides a single page app to manage, create, edit and delete Personal PSKs from Mist Cloud. It is required to have a Mist account to get access to this app.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

<img src="https://github.com/tmunzer/mist_psk_stateless_web_ui/blob/master/._readme/main.png?raw=true"/>

## Features
- Retrieve and display Org and Site PPSKs 
- Edit Org or Site PPSK
- Create new Org or Site PPSK
- Delete Org or Site PPSK
- Display Configuration QRCode for smartphone
- Send email to user with SSID and PPSK information, and QRCode for smartphone configuration

<img src="https://github.com/tmunzer/mist_psk_stateless_web_ui/blob/master/._readme/create.png" width="30%" />
<img src="https://github.com/tmunzer/mist_psk_stateless_web_ui/blob/master/._readme/qrcode.png?" width="30%" />


## Installation

This is a demo application using the Mist APIs.

You can run it as a strandalone Python application, or deploy it as a Docker container.

**Note**: The application is not providing secured HTTPS connections. It is highly recommended to deploy it behind a reverse proxy providing HTTPS encryption.


## Configuration
You can configure the settings through a configuration file or through Environment Variables.
### Configuration File
A configuration example with explanation is avaiable in the `django/backend/config_example.py`. This file must be edited and renamed `config.py`.

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
DJANGO_DEBUG | Number | 0 | Whether or not Django starts in Debug Mode (0=Production, 1=Debug) |
DJANGO_ALLOWED_HOSTS | String |  | FQDN on which Django is listening. Only used in Production Mode |
