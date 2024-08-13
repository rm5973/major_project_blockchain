import json
import qrcode
import os
from flask import Flask

app = Flask(__name__)

class Blockchain:
    def __init__(self):
        self.chain = []  # Initialize an empty chain

def url_to_qr(url, filename='product_qr_code.png', save_path='static'):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Construct the file path for saving the image
    file_path = os.path.join(save_path, filename)

    # Save the image
    img.save(file_path)
    print(f"QR Code saved as {file_path}")

    return file_path

def generate_qr_codes_from_blockchain(filename):
    qr_codes = {}
    with open(filename, "r") as file:
        blockchain_data = json.load(file)

    for index, block_data in enumerate(blockchain_data[1:], start=1):  # Iterate over blockchain data starting from index 1
        url = f"http://192.168.50.166:5000/qr/{index}"
        img_path = url_to_qr(url, f"{index}_qr_code.png")
        qr_codes[index] = img_path

    return qr_codes

@app.route('/qr/<int:block_index>')
def show_qr_page(block_index):
    # Load data from blockchain.json
    with open('blockchain.json', 'r') as file:
        blockchain_data = json.load(file)

    # Get the block data for the specified index
    if 0 <= block_index < len(blockchain_data):
        block_data = blockchain_data[block_index]
    else:
        return "Invalid block index"

    # Get product data from the block
    product_name = block_data.get('ProductName', '')
    manufacturer_name = block_data.get('Manufacturer', '')
    product_price = block_data.get('ProductPrice', '')
    product_size = block_data.get('ProductSize', '')
    product_release_date = block_data.get('ProductManufacturedDate', '')

    # Construct HTML content with product data and QR code image
    html_content = f"""
    <div>
        <h2>Product Details:</h2>
        <p><b>Manufacturer:</b> {manufacturer_name}</p>
        <p><b>ProductName:</b> {product_name}</p>
        <p><b>ProductPrice:</b> {product_price}</p>
        <p><b>ProductSize:</b> {product_size}</p>
        <p><b>ProductManufacturedDate:</b> {product_release_date}</p>
        <img src="/static/{block_index}_qr_code.png" alt="QR Code">
    </div>
    """

    return html_content

if __name__ == "__main__":
    filename = "blockchain.json"
    qr_codes = generate_qr_codes_from_blockchain(filename)
    app.run(debug=True)
