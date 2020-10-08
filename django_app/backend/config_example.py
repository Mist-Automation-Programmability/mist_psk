
smtp_config = {
    "host": "", # SMTP Server IP or hostname
    "port": 587, # SMTP Server Port 
    "use_ssl": True, # Whether or not to use SSL to talk with the SMTP Server
    "username": "", # If SMTP server requires authentication, the username to use
    "password": "", # If SMTP server requires authentication, the password to use
    "from_name": "Wi-Fi Access", # Sender name of the email
    "from_email": "", # Sender email address 
    "logo_url": "https://cdn.mist.com/wp-content/uploads/logo.png", # URL to the logo to display in the email
    "enable_qrcode": True # Whether or not to display the QRcode to configuration smartphones
}
psk_config = {
    "salt": "$2b$12$SIGWr574/7OggDO4BBJ1D.", # Salt for "renewable" PSK generation
    "length": 12 # Size for "renewable" PSK length (must be between 8 and 63
}