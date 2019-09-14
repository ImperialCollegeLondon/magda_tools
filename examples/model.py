import argparse
import matplotlib.pyplot as plt

from magda_tools import DataFile, BFieldModel

parser = argparse.ArgumentParser(
    description="Plot the magnetic field strength data from a Magda flat file"
)
parser.add_argument("FFD_file", type=str, help="Path to a Magda flat file")
args = parser.parse_args()


model = BFieldModel([21160.0, 1560.0, 2320.0])
df = DataFile(args.FFD_file)

r, theta, phi = model.process_datafile(df)
plt.plot(df["TIME"].data.datetime, r)
plt.plot(df["TIME"].data.datetime, theta)
plt.plot(df["TIME"].data.datetime, phi)

plt.xlabel("Date and Time")
plt.ylabel("Predicted Magnetic Field Strength (nT)")
plt.show()
