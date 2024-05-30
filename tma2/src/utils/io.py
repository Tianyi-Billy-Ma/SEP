import pandas as pd
import json


def read_xpt(file_path):
    with open(file_path, "rb") as f:
        file = pd.read_sas(f, format="xport")
    return file


def read_json(file_path):
    with open(file_path, "r") as f:
        file = json.load(f)
    return file


def save_json(file, file_path):
    with open(file_path, "w") as f:
        json.dump(file, f)
