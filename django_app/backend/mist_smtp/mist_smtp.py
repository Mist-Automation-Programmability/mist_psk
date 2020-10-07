import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from .mist_qrcode import get_qrcode_as_html

def _load_conf(conf_obj, conf_val, conf_type):
    if conf_val in conf_obj: return conf_obj[conf_val]
    else: 
        print('\033[31m\u2716\033[0m')
        print("Unable to load {0} \"{1}\" from the configuration file.. Exiting...".format(conf_type, conf_val))
        exit(1)

class Mist_SMTP():
    def __init__(self, smtp_config):
        print("Loading SMTP settings ".ljust(79, "."), end="", flush=True)
        if smtp_config:
            self.host = _load_conf(smtp_config, "host", "SMTP")
            self.port = _load_conf(smtp_config, "port", "SMTP")
            self.use_ssl = _load_conf(smtp_config, "use_ssl", "SMTP")
            self.username = _load_conf(smtp_config, "username", "SMTP")
            self.password = _load_conf(smtp_config, "password", "SMTP")
            self.from_name = _load_conf(smtp_config, "from_name", "SMTP")
            self.from_email = _load_conf(smtp_config, "from_email", "SMTP")
            self.logo_url = _load_conf(smtp_config, "logo_url", "SMTP")            
            # if self.use_ssl:
            #     self.smtp = smtplib.SMTP_SSL
            # else: self.smtp = smtplib.SMTP
            self.smtp = smtplib.SMTP
            print("\033[92m\u2714\033[0m")
        else:
            print('\033[31m\u2716\033[0m')
            print("SMTP DISABLED")
            self.email_psk_to_users = False
            self.report_enabled = False  

    def _send_email(self, receivers, msg, log_message):
        print(log_message, end="", flush=True)
        #try:             
        with self.smtp(self.host, self.port) as smtp:
            if self.use_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
            if self.username and self.password:
                smtp.login(self.username, self.password)
            smtp.sendmail(self.from_email, receivers, msg)   
        print("\033[92m\u2714\033[0m")
        return True
        # except:              
        #     print('\033[31m\u2716\033[0m')
        #     return False


    def send_psk(self, psk, ssid, user_name, user_email):    
        msg = MIMEMultipart('alternative')
        msg["Subject"] = "Your Personal Wi-Fi access code"
        msg["From"] = "{0} <{1}>".format(self.from_name, self.from_email)
        msg["To"] = "{0} <{1}>".format(user_name, user_email)
    
        qr_info = "You can also scan the QRCode below to configure your device:"
        qr_html = get_qrcode_as_html(ssid, psk)                
        
        with open("./backend/mist_smtp/template.html", "r") as template:
            html = template.read()
        html = html.format(self.logo_url, user_name, ssid, psk, qr_info, qr_html)
        msg_body = MIMEText(html, "html")
        msg.attach(msg_body)

        return self._send_email(user_email, msg.as_string(), "    Sending the email ".ljust(79, "."))

