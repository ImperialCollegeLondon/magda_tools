import argparse
import matplotlib.pyplot as plt

from magda_tools import DataFile, distance, latitude

parser = argparse.ArgumentParser(
    description="Plot the position data from a Magda flat file in the kg coordinate system"
)
parser.add_argument("FFD_file", type=str, help="Path to a Magda flat file")
args = parser.parse_args()

df = DataFile(args.FFD_file)
coord = df.coord.upper()

assert coord == "KG"

x, y, z = df[f"BX_{coord}"].data, df[f"BY_{coord}"].data, df[f"BZ_{coord}"].data
lat = latitude(x, y, z)
dist = distance(x, y, z)

l1 = plt.plot(df["TIME"].data.datetime, lat)[0]
plt.ylabel("Latitude (degrees)")
plt.twinx()
l2 = plt.plot(df["TIME"].data.datetime, dist, "r")[0]
plt.ylabel("Distance (km)")
plt.legend((l1, l2), ("latitude", "distance"))

plt.xlabel("Date and Time")
plt.show()
