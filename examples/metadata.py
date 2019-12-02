import argparse

from magda_tools import DataFile

parser = argparse.ArgumentParser(
    description="Print the metadata extracted from an flat file header (ffh)"
)
parser.add_argument("FFH_file", type=str, help="Path to a Magda flat file header")
args = parser.parse_args()

metadata = DataFile.parse_header(args.FFH_file)

for key, item in metadata.items():
    print(f"{key}: {item}")
