from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import hashlib
import datetime
import os
import subprocess
import json
import hashlib
import datetime
import os

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




class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()


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



app = Flask(__name__)
app.secret_key = "alkdjfalkdjf"


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



import json

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


if __name__ == "__main__":
    app.run(debug=True)
    session["user"] = ""
