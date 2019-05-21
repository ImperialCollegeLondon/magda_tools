import json
import os
from copy import deepcopy
from datetime import datetime
from unittest import TestCase

from magda_tools import MAGDA_TIME_FMT_MS, DataFile

CASDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/casdata")


# once finalised version of the data for public release is available
# get a more broad range of header files to test against
class TestDataParser(TestCase):
    def setUp(self):
        self.ffh_rel_paths = [
            "y17/17051/processed/17051_mrdcd_hkfgmn_rtn_1m.ffh",
            "y17/17051/processed/17051_mrdcd_hkfgmn_rtn_60m.ffh",
            "y17/17051/processed/17051_mrdcd_sdfgmc_ksm_1m.ffh",
        ]
        self.ffh_rel_ffd_exists = self.ffh_rel_paths[0]
        self.ffh_rel_ffd_not_exists = self.ffh_rel_paths[2]
        target_metadata_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/target_extracted_casdata.json",
        )
        with open(target_metadata_file, "r") as f:
            self.target_metadata = json.load(f)

        assert set(self.ffh_rel_paths) == set(self.target_metadata.keys())

    def test_get_metadata_from_header_file(self):
        """Test that metadata is extracted correctly from .ffh header file.
        """
        target_metadata = deepcopy(self.target_metadata[self.ffh_rel_ffd_exists])
        target_metadata.pop("has_ffd")
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

        ffh = os.path.join(CASDATA, self.ffh_rel_ffd_exists)

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
        ffd = self.ffh_rel_ffd_exists.replace(".ffh", ".ffd")
        # ffd = "y07/07062/processed/07062_mrdcd_sdfgmc_c.ffd"
        ffd = os.path.join(CASDATA, ffd)
        datafile = DataFile(ffd)
        target_metadata = self.target_metadata[self.ffh_rel_ffd_exists]
        target_metadata.pop("has_ffd")
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
            self.assertEqual(attr, v)

        for c in datafile.columns:
            self.assertEqual(len(c.data), datafile.n_rows)

        self.assertEqual(datafile["TIME"], datafile.columns[0])
        # should add below value to json metadata file
        self.assertAlmostEqual(datafile.timebase.unix, 946727968.0, places=5)

        self.assertLessEqual(datafile.start, datafile["TIME"].data[0])
        # # Should the below need to pass as well?
        # self.assertLessEqual(data_end + datafile.timebase, datafile.end)
