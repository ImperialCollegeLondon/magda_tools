import argparse
import matplotlib.pyplot as plt

from magda_tools import DataFile

parser = argparse.ArgumentParser(
    description="Plot the magnetic field strength data from a Magda flat file"
)
parser.add_argument("FFD_file", type=str, help="Path to a Magda flat file")
args = parser.parse_args()

df = DataFile(args.FFD_file)
coord = df.coord.upper()
plt.plot(df["TIME"].data.datetime, df[f"BX_{coord}"].data)
plt.plot(df["TIME"].data.datetime, df[f"BY_{coord}"].data)
plt.plot(df["TIME"].data.datetime, df[f"BZ_{coord}"].data)

plt.xlabel("Date and Time")
plt.ylabel("Magnetic Field Strength (nT)")
plt.show()
