import os
from unittest import TestCase
from unittest.mock import patch

import numpy as np

from magda_tools import BFieldModel, DataFile

CASDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/casdata")


# update value of SATURN_RADIUS_KM here as we are testing against a
# reference model that used a different value
@patch("magda_tools.model.SATURN_RADIUS_KM", 60330.0)
class TestModel(TestCase):
    @classmethod
    def setUpClass(self):
        self.df = DataFile(
            os.path.join(CASDATA, "y17/17051/processed/17051_mrdcd_sdfgmc_krtp_1m.ffd")
        )
        # truncate data series as we only need to check a subset of values
        self.df["X_KG"].data = self.df["X_KG"].data[:5]
        self.df["Y_KG"].data = self.df["Y_KG"].data[:5]
        self.df["Z_KG"].data = self.df["Z_KG"].data[:5]

    def test_three_degree_model(self):
        target_r_hat_values = np.array(
            [5.68907928, 5.69458485, 5.70067310, 5.70677090, 5.71288443]
        )
        target_theta_hat_values = np.array(
            [4.74245548, 4.74528885, 4.74842024, 4.75155592, 4.75469828]
        )
        target_phi_hat_values = np.array([0, 0, 0, 0, 0])

        gn0s = [21160.0, 1560.0, 2320.0]
        model = BFieldModel(gn0s)

        r_hat_values, theta_hat_values, phi_hat_values = model.process_datafile(self.df)

        self.assertTrue((np.abs(r_hat_values - target_r_hat_values) < 1e-5).all())
        self.assertTrue(
            (np.abs(theta_hat_values - target_theta_hat_values) < 1e-5).all()
        )
        self.assertTrue((np.abs(phi_hat_values - target_phi_hat_values) < 1e-5).all())
