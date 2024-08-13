import json
import hashlib

class Block:
    def __init__(self, index, timestamp, data, previous_hash, hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = hash

    def calculate_hash(self):
        data_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

def verify_blockchain(filename):
    blockchain = []
    with open(filename, "r") as file:
        blockchain_data = json.load(file)
        for block_data in blockchain_data:
            block = Block(
                block_data["index"],
                block_data["timestamp"],
                block_data["data"],
                block_data["previous_hash"],
                block_data["hash"]
            )
            blockchain.append(block)

    # Verify each block in the blockchain
    for i in range(1, len(blockchain)):
        current_block = blockchain[i]
        previous_block = blockchain[i - 1]

        # Check if the stored hash matches the calculated hash
        if current_block.hash != current_block.calculate_hash():
            print(f"Block {current_block.index}: Hash mismatch!")
            return False

        # Check if the previous hash is correct
        if current_block.previous_hash != previous_block.hash:
            print(f"Block {current_block.index}: Previous hash mismatch!")
            return False

    print("Blockchain is valid!")
    return True

if __name__ == "__main__":
    filename = "blockchain.json"
    verify_blockchain(filename)
