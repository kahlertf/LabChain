import json
import time
import logging
from labchain.cryptoHelper import CryptoHelper


class Consensus:

    def __init__(self):

        self.crypto_helper = CryptoHelper.instance()
        self.max_diff = 12  # Threshold to be defined
        self.kill_mine = 0
        self.last_mine_time_sec = time.time()

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty(self, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = int(((latest_timestamp - earliest_timestamp) / num_of_blocks))

        if difficulty >= self.max_diff:
            difficulty = self.max_diff - 1
        return self.max_diff - difficulty

        # global difficulty should not be updated, instead return difficulty,
        # because if validate is called during mining, it would update difficulty

    def validate(self, block, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)

        zeros_array = "0" * difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # Assumed that hash is str
        logging.debug('#INFO:Consensus-> Block: ' + block.block_id + 'is validated')
        return block_hash[:difficulty] == zeros_array

    def mine(self, block, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)
        start_time = time.time()
        zeros_array = "0" * difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # nonce is zero (we need to check that)
        counter = block.nonce
        while block_hash[:difficulty] != zeros_array:
            if self.kill_mine == 1:
                self.kill_mine = 0
                # need a boolean return to check if mine got killed
                logging.debug('#INFO:Consensus-> Block: ' + block.block_id + ' mining process has been killed')
                return False
            block.nonce += 1
            counter = counter + 1
            if counter%1000 == 0:
                logging.debug('#INFO:Consensus-> Block: ' + block.block_id + ' is in mining process')
            data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
                str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
            message = json.dumps(data)
            block_hash = self.crypto_helper.hash(message)
        block.timestamp = time.time()
        self.last_mine_time_sec = start_time
        logging.debug('#INFO:Consensus-> Block: ' + block.block_id + 'is mined successfully')
        # need a boolean return to check if mine got killed
        return True

    #    Code for updating the difficulty to be implemented by Blockchain component
    #    if self.blocks_counter % self.blocks_threshold  == 0 & self.recalculate == 1:
    #        self.blocks_counter = 0
    #        self.recalculate = 0;
    #        self.difficulty = self.calculate_difficulty(time.time())
