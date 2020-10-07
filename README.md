# mist_report_generator
 
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
