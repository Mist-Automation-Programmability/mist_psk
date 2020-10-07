import qrcode

def get_qrcode(ssid, psk):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data("WIFI:S:{0};T:WPA;P:{1};;".format(ssid, psk))
    qr.make(fit=True)
    return qr.get_matrix()

def get_qrcode_as_html(ssid, psk):
    qr = get_qrcode(ssid, psk)
    qr_html = ""
    fg_color = "#ffffff"
    bg_color = "#000000"
    for i in qr:
        qr_html+="<tr>"
        for j in i:
            if j: color = bg_color
            else: color = fg_color
            qr_html +="<td style=\"background-color:{0}; height:5px; width: 5px; padding: 0px; margin: 0px\"></td>\r\n".format(color)
        qr_html+="</tr>\r\n"
    return qr_html