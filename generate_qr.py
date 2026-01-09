import qrcode

# The local network URL for your app
url = "http://192.168.245.99:5000"

# Generate QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("static/images/app_download_qr.png")

print(f"QR Code generated for {url}")
