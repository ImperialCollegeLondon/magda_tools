import json
import os
from copy import deepcopy
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from pytz import UTC

from magda_tools import (
    MAGDA_PATH_REGEX_TEMPLATE,
    MAGDA_TIME_FMT_MS,
    DataFile,
    get_metadata_from_header_file,
)

CASDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/casdata")

MAGDA_HEADER_PATH_REGEX = MAGDA_PATH_REGEX_TEMPLATE.substitute(
    casdata=CASDATA, ext="ffh"
)


@patch("magda_tools.header.CASDATA", CASDATA)
@patch("magda_tools.header.MAGDA_HEADER_PATH_REGEX", MAGDA_HEADER_PATH_REGEX)
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
        # Override mtime for data files and update target mtime correspondingly
        override_last_modified = {
            "y17/17051/processed/17051_mrdcd_hkfgmn_rtn_1m.ffh": "2017 133 May 13 18:35:46.000000",
            "y17/17051/processed/17051_mrdcd_hkfgmn_rtn_1m.ffd": "2017 133 May 13 18:35:46.000000",
            "y17/17051/processed/17051_mrdcd_hkfgmn_rtn_60m.ffh": "2017 133 May 13 18:42:18.000000",
            "y17/17051/processed/17051_mrdcd_hkfgmn_rtn_60m.ffd": "2017 133 May 13 19:42:18.000000",
            "y17/17051/processed/17051_mrdcd_sdfgmc_ksm_1m.ffh": "2017 133 May 13 19:38:35.000000",
        }
        for k, v in override_last_modified.items():
            if k in self.target_metadata:
                self.target_metadata[k]["last_modified"] = v
            path = os.path.join(CASDATA, k)
            dt = datetime.strptime(v, MAGDA_TIME_FMT_MS)
            dt = UTC.localize(dt)
            timestamp = dt.timestamp()
            os.utime(path, times=(timestamp, timestamp))

        assert set(self.ffh_rel_paths) == set(self.target_metadata.keys())

    def test_get_metadata_from_header_file(self):
        """Test that metadata is extracted correctly from .ffh header file.
        """
        target_metadata = deepcopy(self.target_metadata[self.ffh_rel_ffd_exists])
        target_metadata.pop("has_ffd")
        target_metadata.pop("name")
        target_metadata.pop("size")
        for k, v in target_metadata.items():
            if isinstance(v, str):
                target_metadata[k] = v.lower()

        ffh = os.path.join(CASDATA, self.ffh_rel_ffd_exists)

        metadata = get_metadata_from_header_file(ffh)
        metadata.pop("calibrated")
        metadata.pop("end")
        metadata.pop("n_rows")
        for k, v in metadata.items():
            if isinstance(v, str):
                metadata[k] = v.lower()

        self.assertDictEqual(metadata, target_metadata)

    def test_datafile(self):
        ffd = self.ffh_rel_ffd_exists.replace(".ffh", ".ffd")
        ffd = os.path.join(CASDATA, ffd)
        datafile = DataFile(ffd)
        target_metadata = self.target_metadata[self.ffh_rel_ffd_exists]
        target_metadata.pop("has_ffd")
        target_metadata.pop("name")
        target_metadata.pop("size")
        for k, v in target_metadata.items():
            if isinstance(v, str):
                target_metadata[k] = v.lower()

        # metadata items should be set as datafile attributes
        for k, v in target_metadata.items():
            attr = getattr(datafile, k)
            if isinstance(attr, str):
                attr = attr.lower()
            self.assertEqual(attr, v)

        # check the right amount of data has been pulled out
        self.assertEqual(datafile.n_cols, 8)

        for c in datafile.columns:
            self.assertEqual(len(c.data), datafile.n_rows)

        self.assertEqual(datafile["TIME_TAI"], datafile.columns[0])
        self.assertEqual(datafile.timebase, 946727968000)
