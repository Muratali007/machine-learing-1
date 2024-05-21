import pandas as pd
import logging as log

def read_csv_to_dict(file_path):
    log.info("start read_csv_to_dict")
    csv_book_mapping = {}
    with open(file_path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            csv_id, book_id = line.strip().split(",")
            csv_book_mapping[csv_id] = book_id
    return csv_book_mapping

def read_interactions(file_path):
    log.info("start read interactions")
    interactions = []
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            interactions.append(line.strip().split(","))
    return interactions

def read_json(file_path):
    return pd.read_json(file_path)
