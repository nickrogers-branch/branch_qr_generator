# Branch QR Generator
A script for generating QR codes with Branch links behind them.


## Configuration
Use the `config.json` file to define a mapping between columns in your CSV file and Branch parameters (e.g. analytics tags). Also use this file to configure your Branch `live_key` and domain.

## Usage

To turn a CSV file into QR codes:

`python main.py -i path/to/input/csv/file -o path/to/output/directory`

If an `-o` flag isn't specified, it will default to the path `../output`.
