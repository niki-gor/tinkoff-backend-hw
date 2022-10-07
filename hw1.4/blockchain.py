import itertools
import pickle
from multiprocessing import Process, Queue, cpu_count
from hashlib import sha256
from datetime import datetime
from dataclasses import dataclass
from threading import Thread
from typing import List, Dict, Iterator, Optional
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue
from http import HTTPStatus


def math_func(proof: int, previous_proof: int) -> int:
    return proof ** 2 - previous_proof ** 2


def get_sha256(proof: int, previous_proof: int) -> str:
    calculation = math_func(proof, previous_proof)
    encoded = str(calculation).encode()
    return sha256(encoded).hexdigest()


@dataclass
class Block:
    index: int
    timestamp: datetime
    proof: Optional[int]
    previous_hash: Optional[str]


class Blockchain:
    INITIAL_PROOF = 1
    INITIAL_HASH = "0"

    def __init__(self, calc_complex="00000"):
        self.processes_amount = cpu_count()
        self.complex: str = calc_complex
        self.chain: List[Block] = []
        self.future_blocks_chan: Queue[Block] = Queue()
        self.index_counter: Iterator = itertools.count(1)

        initial_block = Block(
            index=next(self.index_counter),
            timestamp=datetime.now(),
            proof=self.INITIAL_PROOF,
            previous_hash=self.INITIAL_HASH,
        )
        self.chain.append(initial_block)

        Thread(target=self._future_blocks_worker, daemon=True).start()
        # join'ить его не нужно, т.к. пока работает сервер, работает и поток
        # следовательно, хранить его тоже не обязательно

        # Почему не процесс?
        # Потому что при использовании процесса GIL'ом блочится self.chain

    def create_block(self) -> Dict:
        future_block = Block(
            index=next(self.index_counter),
            timestamp=datetime.now(),
            proof=None,
            previous_hash=None,
        )
        report = {
            "index": future_block.index,
            "timestamp": future_block.timestamp,
        }
        self.future_blocks_chan.put(future_block)

        return report

    @property
    def previous_block(self):
        return self.chain[-1]

    def _future_blocks_worker(self):
        while True:
            block = self.future_blocks_chan.get()
            block.previous_hash = self.hash(self.previous_block)
            block.proof = self.proof_of_work(self.previous_block.proof)
            self.chain.append(block)

    def _proof_of_work_worker(self,
                              chan_in: Queue,
                              chan_out: Queue,
                              previous_proof: int) -> None:
        while new_proof := chan_in.get():
            hash_operation = get_sha256(new_proof, previous_proof)
            is_valid = self.is_hash_complex_valid(hash_operation)
            result = new_proof, is_valid
            chan_out.put(result)

    def proof_of_work(self, previous_proof: int) -> int:
        in_chan = Queue()
        out_chan = Queue()
        processes = []
        for _ in range(self.processes_amount):
            process = Process(target=self._proof_of_work_worker,
                              args=(out_chan,
                                    in_chan,
                                    previous_proof))
            process.start()
            processes.append(process)

        proof_gen = itertools.count(1)
        for _ in range(self.processes_amount):
            new_proof = next(proof_gen)
            out_chan.put(new_proof)

        result, check_proof = None, False
        while not check_proof:
            result, check_proof = in_chan.get()
            new_proof = next(proof_gen)
            out_chan.put(new_proof)

        for _ in range(self.processes_amount):
            out_chan.put(None)

        for process in processes:
            process.join()

        return result

    def hash(self, block: Block) -> str:
        encoded_block = pickle.dumps(block)
        return sha256(encoded_block).hexdigest()

    def is_hash_complex_valid(self, hash_operation) -> bool:
        return hash_operation[:len(self.complex)] == self.complex

    def get_block_status(self, index: int) -> str:
        ready = len(self.chain)
        in_progress = self.future_blocks_chan.qsize()
        if 1 <= index <= ready:
            return 'completed'
        if ready < index <= ready + in_progress:
            return "in_progress"
        return "not_found"

    def chain_valid(self) -> bool:
        previous_block = self.chain[0]

        for block in self.chain[1:]:
            if block.previous_hash != self.hash(previous_block):
                return False

            previous_proof = previous_block.proof
            proof = block.proof
            hash_operation = get_sha256(proof, previous_proof)
            if not self.is_hash_complex_valid(hash_operation):
                return False

            previous_block = block

        return True


app = Flask(__name__)
blockchain = Blockchain(calc_complex="00000")


# POST - create new product
# PUT - change product
# PATCH - change small product
# GET - get list product

# создаем новый блок => метод POST
@app.route("/mine_block", methods=["POST"])
def mine_block() -> ResponseReturnValue:
    response = blockchain.create_block()
    response["message"] = "mine_block request accepted"
    return jsonify(response), HTTPStatus.ACCEPTED
    # мы не создали новый блок, а лишь приняли запрос на создание блока


@app.route("/valid", methods=["GET"])
def valid() -> ResponseReturnValue:
    response = {
        "chain_valid": "OK" if blockchain.chain_valid() else "NOT OK"
    }
    return jsonify(response), HTTPStatus.OK


@app.route("/get_chain", methods=["GET"])
def get_chain() -> ResponseReturnValue:
    response = {
        "chain": blockchain.chain
    }
    return jsonify(response), HTTPStatus.OK


@app.route("/block/<int:index>/status", methods=["GET"])
def get_block_status(index: int) -> ResponseReturnValue:
    response = {
        "status": blockchain.get_block_status(index)
    }
    return jsonify(response), HTTPStatus.OK


app.run(host="127.0.0.1", debug=True, port=5000)
