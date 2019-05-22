import os
from unittest import TestCase

import magda_tools

CASDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/casdata")


class TestCalculations(TestCase):
    @classmethod
    def setUpClass(self):
        self.df = magda_tools.DataFile(
            os.path.join(CASDATA, "y17/17051/processed/17051_mrdcd_sdfgmc_ksm_1m.ffd")
        )

    def test_saturn_local_time(self):
        """Test conversion of time and positional coordinates into
        saturn local time."""

        # These test values were generated from the SLTChannel java
        # implementation applied to the first 5 rows of the datafile
        # 17051_mrdcd_sdfgmc_ksm_1m.ffd
        target_values = [
            8749.28808594,
            8750.88867188,
            8752.66601563,
            8754.44433594,
            8756.22558594,
        ]

        N = len(target_values)
        calculated = magda_tools.saturn_local_time(
            self.df["TIME"].data[:N],
            self.df["X_KSM"].data[:N],
            self.df["Y_KSM"].data[:N],
            self.df["Z_KSM"].data[:N],
        )

        for t, c in zip(target_values, calculated):
            self.assertAlmostEqual(t, c.seconds + c.microseconds / 1e6, places=3)

    def test_latitude(self):
        """Test conversion of time and positional coordinates into
        saturn local time."""

        # These test values were generated from the SLTChannel java
        # implementation applied to the first 5 rows of the datafile
        # 17051_mrdcd_sdfgmc_ksm_1m.ffd
        target_values = [
            50.51605225,
            50.52217484,
            50.52896500,
            50.53575516,
            50.54255295,
        ]

        N = len(target_values)
        calculated = magda_tools.latitude(
            self.df["X_KSM"].data[:N],
            self.df["Y_KSM"].data[:N],
            self.df["Z_KSM"].data[:N],
        )
        for t, c in zip(target_values, calculated):
            self.assertAlmostEqual(t, c, places=3)
