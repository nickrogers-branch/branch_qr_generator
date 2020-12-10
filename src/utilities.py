import os
import json

# Load config file for this Branch link and QR code generator.
def load_config():
    dir_name = os.path.dirname(__file__)
    config_file_path = os.path.join(dir_name, '../config/config.json')
    with open(config_file_path) as config_file:
        return json.load(config_file)
