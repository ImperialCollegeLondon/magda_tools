import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from unittest import TestCase

from magda_tools import MAGDA_TIME_FMT_MS, DataFile


DATA_ROOT = Path(__file__).parent.absolute() / "data"
CASDATA = DATA_ROOT / "casdata"


# once finalised version of the data for public release is available
# get a more broad range of header files to test against
class TestDataParser(TestCase):
    def setUp(self):
        self.ffh_rel_path = "y08/08100/processed/08100_mrdcd_hkfgmn_kg_1m.ffh"
        target_metadata_file = Path(DATA_ROOT, "target_extracted_casdata.json")
        with open(target_metadata_file, "r") as f:
            self.target_metadata = json.load(f)

    def test_get_metadata_from_header_file(self):
        """Test that metadata is extracted correctly from .ffh header file.
        """
        target_metadata = deepcopy(self.target_metadata)
        target_metadata.pop("name")
        target_metadata.pop("size")
        target_metadata["start"] = datetime.strptime(
            target_metadata["start"], MAGDA_TIME_FMT_MS
        )
        target_metadata.pop("last_modified")
        target_column_data = target_metadata.pop("columns")
        for k, v in target_metadata.items():
            if isinstance(v, str):
                target_metadata[k] = v.lower()

        ffh = Path(CASDATA, self.ffh_rel_path)

        metadata = DataFile.parse_header(ffh)
        columns = metadata.pop("columns")
        metadata.pop("end")
        metadata.pop("timebase")
        for k, v in metadata.items():
            if isinstance(v, str):
                metadata[k] = v.lower()

        self.assertDictEqual(metadata, target_metadata)
        for attr, values in target_column_data.items():
            for col, target_val in zip(columns, values):
                self.assertEqual(getattr(col, attr), target_val)

    def test_datafile(self):
        ffd = self.ffh_rel_path.replace(".ffh", ".ffd")
        datafile = DataFile(Path(CASDATA, ffd))
        target_metadata = deepcopy(self.target_metadata)
        target_metadata.pop("name")
        target_metadata.pop("size")
        target_metadata.pop("last_modified")
        target_metadata.pop("columns")
        target_metadata["start"] = datetime.strptime(
            target_metadata["start"], MAGDA_TIME_FMT_MS
        )
        for k, v in target_metadata.items():
            if isinstance(v, str):
                target_metadata[k] = v.lower()

        # metadata items should be set as datafile attributes
        for k, v in target_metadata.items():
            attr = getattr(datafile, k)
            if isinstance(attr, str):
                attr = attr.lower()
            self.assertEqual(attr, v, k)

        for c in datafile.columns:
            self.assertEqual(len(c.data), datafile.n_rows)

        self.assertEqual(datafile["TIME"], datafile.columns[0])
        # should add below value to json metadata file
        self.assertAlmostEqual(datafile.timebase.unix, 946727968.0, places=5)

        self.assertEqual(datafile.start, datafile["TIME"].data[0].datetime)
        self.assertEqual(datafile["TIME"].data[-1].datetime, datafile.end)

    def test_decode_sensor_status(self):
        """Test the bit shift operations used to decode sensor data"""

        # raw and target status data were derived by applying the reference
        # implementation provided by SensorRangeChannel.decode (from the
        # original Magda Java based system) to 17002_mrdcd_sdfgmc_c.ffd.
        # The below lists contain all unique pairings between raw sensor
        # status data and decoded status values
        raw_data = [
            -1879046909,
            -1879046653,
            -1845492477,
            268436995,
            301991427,
            1073742851,
            1073743363,
            1107297283,
            1107297795,
            1342178307,
            1342178563,
            1342178819,
            1358956035,
            1375732739,
            1375733251,
        ]
        target_status_data = [2, 2, 2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        status_data = DataFile.decode_sensor_status(raw_data)
        for s, t in zip(status_data, target_status_data):
            self.assertEqual(s, t)
