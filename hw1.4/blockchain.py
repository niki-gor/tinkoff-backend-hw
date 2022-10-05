import datetime
import json
from hashlib import sha256
from datetime import datetime
from dataclasses import dataclass
from typing import List

from flask import Flask, jsonify


def math_func(proof: int, previous_proof: int) -> int:
    return proof ** 2 - previous_proof ** 2


def get_sha256(proof, previous_proof) -> str:
    return sha256(str(math_func(proof, previous_proof)).encode()).hexdigest()


@dataclass
class Block:
    index: int
    timestamp: datetime
    proof: str
    previous_hash: str


class Blockchain:
    """
    BlockChain
        [data1] -> [data2, hash(data1)] -> [data3, hash(data2)]
        proof-of-work --
        blockchain - nodes(компы)
    """

    def __init__(self, calc_complex="00000"):
        self.chain: List[Block] = []
        self.create_block(1, "0")
        self.complex: str = calc_complex

    def create_block(self, proof, previous_hash) -> Block:
        block = Block(
            index=len(self.chain) + 1,
            timestamp=datetime.now(),
            proof=proof,
            previous_hash=previous_hash,
        )
        self.chain.append(block)

        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            hash_operation = get_sha256(new_proof, previous_proof)

            if self.is_hash_complex_valid(hash_operation):
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block: Block) -> str:
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return sha256(encoded_block).hexdigest()

    def is_hash_complex_valid(self, hash_operation) -> bool:
        return hash_operation[:len(self.complex)] == self.complex

    def chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block["prev_hash"] != self.hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = get_sha256(proof, previous_proof)

            if not self.is_hash_complex_valid(hash_operation):
                return False

            previous_block = block
            block_index += 1

        return True


# user -> www.vk.ru -> login(eyes) - front -> POST username, password ==> backend - АПИ

app = Flask(__name__)
blockchain = Blockchain(calc_complex="000000000")


# Graphql, GRPC

# Shop - product API - REST
# POST - create new product
# PUT - change product
# PATCH - change small product
# GET - get list product

@app.route("/mine_block", methods=["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block.proof

    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)

    response = {
        "message": "Block created",
        "index": block.index,
        "timestamp": block.timestamp,
        "proof": block.proof,
        "previous_hash": block.previous_hash,
    }

    return jsonify(response), 200


@app.route("/valid", methods=["GET"])
def valid():
    return jsonify({
        "chain_valid": "OK" if blockchain.chain_valid() else "NOT OK"
    }), 200


@app.route("/get_chain", methods=["GET"])
def get_chain():
    return jsonify({
        "chain": blockchain.chain
    })


app.run(host="127.0.0.1", debug=True, port=5000)
