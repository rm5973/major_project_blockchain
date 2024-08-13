import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import json
import hashlib
import datetime
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "alkdjfalkdjf"


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(json.dumps({
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_from_json()  # Load blockchain from JSON file

    def create_genesis_block(self):
        return Block(0, datetime.datetime.now(), {"info": "Genesis Block"}, "0")

    def load_from_json(self):
        filename = "blockchain.json"

        if os.path.exists(filename):
            with open(filename, "r") as file:
                blockchain_data = json.load(file)
                for block_data in blockchain_data:
                    block = Block(
                        block_data["index"],
                        datetime.datetime.fromisoformat(block_data["timestamp"]),
                        block_data["data"],
                        block_data["previous_hash"]
                    )
                    self.chain.append(block)
        else:
            # If the file does not exist, create genesis block
            self.chain.append(self.create_genesis_block())

    def save_to_json(self):
        filename = "blockchain.json"
        blockchain_data = []

        for block in self.chain:
            block_data = {
                "index": block.index,
                "timestamp": block.timestamp.isoformat(),
                "data": block.data,
                "previous_hash": block.previous_hash,
                "hash": block.hash  # Include hash in block data
            }
            blockchain_data.append(block_data)

        with open(filename, "w") as file:
            json.dump(blockchain_data, file, indent=4)

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), datetime.datetime.now(), data, previous_block.hash)
        self.chain.append(new_block)
        self.save_to_json()  # Save to JSON after adding the new block
        return new_block

    def is_blockchain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


@app.route("/")
def home():
    if session.get("user"):
        return render_template('home.html')
    else:
        flash("Please login to access Verifier")
        return redirect(url_for('login'))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pswd = request.form["password"]

        if user == "Admin":
            if pswd == "password":
                session["user"] = "Admin"
                return render_template("admin.html")

        elif user == "Nike":
            if pswd == "password":
                session["user"] = "Nike"
                return redirect(url_for("nike_data"))

        elif user == "Musigny":
            if pswd == "password":
                session["user"] = "Musigny"
                return redirect(url_for("wine"))

        elif user == "Lupin":
            if pswd == "password":
                session["user"] = "Lupin"
                return redirect(url_for("medicine"))

        elif user == "Kisan":
            if pswd == "password":
                session["user"] = "Kisan"
                return redirect(url_for("fertilizer"))
        else:
            flash("Invalid Login details")
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route("/verify_blockchain")
def verify_blockchain():
    # Run hashcheck.py script using subprocess
    hashcheck_result = subprocess.run(["python", "hashcheck.py"], capture_output=True, text=True)
    qrc_result = subprocess.run(["python", "qrc.py"], capture_output=True, text=True)
    print(qrc_result)
    if hashcheck_result.returncode == 0 and "Blockchain is valid!" in hashcheck_result.stdout:
        # If blockchain is valid, redirect to a new page to display blockchain data with QR codes
        return redirect(url_for("display_blockchain_data", qr_data=qrc_result.stdout))
    else:
        # If blockchain is not valid, redirect back to the admin page or show an error message
        flash("Blockchain verification failed")
        return redirect(url_for("admin"))


@app.route("/display_blockchain_data")
def display_blockchain_data():
    qr_data = request.args.get("qr_data")  # Get QR data from the URL query parameters
    qr_codes = qr_data.splitlines()  # Split the QR data into individual QR codes

    file_paths = [message.split('saved as ')[1] for message in qr_codes]
    print(file_paths)
    # Render the HTML page with QR code file paths
    return render_template("qr_codes.html", file_paths=file_paths)


@app.route("/addproduct", methods=["POST", "GET"])
def addproduct():
    if request.method == "POST":
        # Collect product data from the form
        brand = request.form["brand"]
        name = request.form["name"]
        batch = request.form["batch"]
        pid = request.form["id"]
        manfdate = request.form["manfdate"]
        price = request.form["price"]
        size = request.form["size"]
        ptype = request.form["type"]

        # Convert manfdate to a string
        manfdate = str(manfdate)

        # Prepare product data as a dictionary
        product_data = {
            "Manufacturer": brand,
            "ProductName": name,
            "ProductBatch": batch,
            "ProductId": pid,
            "ProductManufacturedDate": manfdate,
            "ProductPrice": price,
            "ProductSize": size,
            "ProductType": ptype
        }
        for i in range(1, 5):
            image = request.files[f"image{i}"]
            if image:
                filename = secure_filename(image.filename)
                filepath = os.path.join("static", "prodimage", "shoes", name, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                image.save(filepath)

        # Convert product data to JSON format
        product_json = json.dumps(product_data)

        # Initialize Blockchain instance
        blockchain = Blockchain()

        # Add the product data to the blockchain
        new_block = blockchain.add_block(product_data)

        flash("Product added successfully to the Blockchain")
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route("/admin")
def admin():
    return render_template('admin.html')


@app.route("/medicine")
def medicine():
    return render_template('MedicinePage.html')


@app.route("/fertilizer")
def fertilizer():
    return render_template('FertilizersPage.html')


@app.route("/shoes")
def shoes():
    return render_template('ShoesPage.html')


@app.route("/wine")
def wine():
    return render_template('WinePage.html')


@app.route("/logout")
def logout():
    session["user"] = ""
    return redirect(url_for('login'))


@app.route("/nike_data")
def nike_data():
    with open('./NODES/N1/blockchain.json', 'r') as file:
        data = json.load(file)
    return data



from flask import Flask, url_for
import os
import json




@app.route('/qr/<int:block_index>')
def show_qr_page(block_index):
    # Load data from blockchain.json
    with open('blockchain.json', 'r') as file:
        blockchain_data = json.load(file)
        
    # Check if the block index is valid
    if 0 <= block_index < len(blockchain_data):
        block_data = blockchain_data[block_index]
        print(block_data)
    else:
        return "Invalid block index"

    # Get the product data from the block
    product_name = blockchain_data[block_index]["data"]["ProductName"]
    print(product_name)
    manufacturer_name = blockchain_data[block_index]["data"]['Manufacturer']
    product_price = blockchain_data[block_index]["data"]['ProductPrice']
    product_size = blockchain_data[block_index]["data"]['ProductSize'] 
    product_release_date = blockchain_data[block_index]["data"]['ProductManufacturedDate']
    product_type = blockchain_data[block_index]["data"]['ProductType']

    # Define the directory where product images are stored
    image_dir = os.path.join('static', 'prodimage', 'shoes', product_name)
    print(image_dir)
    # Get the list of image files in the product directory
    image_files = os.listdir(image_dir)
    print(image_files)
    # Create the carousel indicators
    carousel_indicators = ''.join([f'<li data-target="#carouselExampleIndicators" data-slide-to="{i}" {"class=active" if i == 0 else ""}></li>' for i in range(len(image_files))])

    # Create the carousel items with product images
    # Create the carousel items with product images
    carousel_items = ''.join([f'<div class="carousel-item {"active" if i == 0 else ""}"><img src="/static/prodimage/shoes/{product_name}/{image}" class="d-block w-100" alt="{image}"></div>' for i, image in enumerate(image_files)])

    # Construct the HTML content with the carousel
    carousel_html = f"""
    <section class="carousel" aria-label="Gallery">
        <ol class="carousel__viewport">
            {carousel_indicators}
            {carousel_items}
        </ol>
        <aside class="carousel__navigation">
            <ol class="carousel__navigation-list">
                {''.join([f'<li class="carousel__navigation-item"><a href="#carousel__slide{i + 1}" class="carousel__navigation-button">Go to slide {i + 1}</a></li>' for i in range(len(image_files))])}
            </ol>
        </aside>
    </section>
    """

    # Construct the HTML content with blockchain data inside the parent div container
    blockchain_html = f"""
    <div style="margin-top: 20px;">
        <p><b>Manufacturer:</b> {manufacturer_name}</p>
        <p><b>ProductName:</b> {product_name}</p>
        <p><b>ProductPrice:</b> {product_price}</p>
        <p><b>ProductSize:</b> {product_size}</p>
        <p><b>ReleaseDate:</b> {product_release_date}</p>
    </div>
    """

    # Define where-to-buy HTML content based on product type
    if product_type == 'shoes':
        where_to_buy_html = """
        <div class="where-to-buy">
            <div class="heading">
                <h2>Shop Now On</h2>
            </div>
            <div class="icons">
                <a href="https://www.amazon.com/"><img class="buy-icon" src="https://img.icons8.com/color/30/000000/amazon.png" alt="Amazon"></a>
                <a href="https://www.nike.com/"><img class="buy-icon" src="https://img.icons8.com/color/30/000000/nike.png" alt="Nike"></a>
                <a href="https://www.myntra.com/"><img class="buy-icon" src="../static/myntra.png" alt="Myntra"></a>
                <a href="https://www.flipkart.com/"><img class="buy-icon" src="../static/flipkart-icon.png" alt="Flipkart"></a>
            </div>
        </div>
        """
    else:
        where_to_buy_html = ""  # No specific information for other product types

    # Construct the HTML content with carousel, blockchain data, and where-to-buy information inside the parent div container
    html_content = f"""
    <h1 style="text-align: center;">WELCOME TO THE VERYFICTION</h1>
    <div class="container" style="height: 75%; width: 60%; padding: 10px; background-color: #ffff4d; margin: 0 auto;">
        {carousel_html}
        {blockchain_html}
        {where_to_buy_html}
    </div>
    """

    # Add a link to the external CSS file
    html_content += """
    <link rel="stylesheet" type="text/css" href="../static/main.css">
    """

    # Serve the HTML content
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    session["user"] = ""
