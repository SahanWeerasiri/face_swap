import requests
from bs4 import BeautifulSoup
from pyzbar.pyzbar import decode
from PIL import Image
import io

url = "http://hashx.destinyoo.com:8000/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

qr_images = soup.find_all('img')  # Assuming all images are QR codes
for img in qr_images:
    img_url = url + img['src'] if not img['src'].startswith('http') else img['src']
    img_data = requests.get(img_url).content
    image = Image.open(io.BytesIO(img_data))
    decoded_objects = decode(image)
    for obj in decoded_objects:
        print("Data:", obj.data.decode())