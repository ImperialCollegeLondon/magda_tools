from typing import Union

from astropy.time import Time, TimeDelta
import numpy as np

# Fitted parameters for calculation of saturn local time
SLT_OMEGA: float = 26.75
SLT_ALPHA: float = 10759.5
SLT_PHI: float = 4.1
SLT_K: float = 0.0

SECS_PER_DAY: int = 86400

# standard value for Saturn equitorial radius
SATURN_RADIUS_KM: float = 60268.0


def saturn_local_time(
    time: Time,
    x_ksm: Union[float, np.ndarray],
    y_ksm: Union[float, np.ndarray],
    z_ksm: Union[float, np.ndarray],
) -> TimeDelta:
    """For the given `time` and positions in the ksm coordinate
    system return an estimated value for Saturn local time.

    Parameters
    ----------
    time: astropy.time
    x_ksm: float or array of floats
      x position coordinate in KSM system in km
    y_ksm: float or array of floats
      y position coordinate in KSM system in km
    z_ksm: float or array of floats
      z position coordinate in KSM system in km

    Returns
    -------
    float:
      saturn local time in seconds from midnight
    """
    days_since_epoch = time.utc.unix / SECS_PER_DAY

    lambda_ = (
        SLT_OMEGA * np.sin((2 * np.pi * days_since_epoch / SLT_ALPHA) + SLT_PHI) - SLT_K
    )
    X = (x_ksm * np.cos(lambda_ * np.pi / 180)) - (
        z_ksm * np.sin(lambda_ * np.pi / 180)
    )

    phi = (np.arctan2(y_ksm, X) * 180 / np.pi) % 360

    return TimeDelta(((12 + (phi * 24 / 360)) % 24) * 3600, format="sec")


def latitude(
    x: Union[float, np.ndarray],
    y: Union[float, np.ndarray],
    z: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """For the given x, y and z coordinates provided from a cartesian
    system aligned with the spin-axis of Saturn return the
    corresponding latitude in degrees. If this function is used with a
    coordinate not aligned with the spin access then the returned
    value will not be correct.

    """
    dist = distance(x, y, z)
    return np.arcsin(z / dist) / np.pi * 180


def distance(
    x: Union[float, np.ndarray],
    y: Union[float, np.ndarray],
    z: Union[float, np.ndarray],
    radius: float = None,
) -> Union[float, np.ndarray]:
    """For the given x, y and z coordinates calculate the distance from
    the system origin. If a value is provided for radius the distance
    will be returned as multiples of this value.

    """
    dist = np.sqrt(x * x + y * y + z * z)
    if radius is not None:
        return dist / radius
    else:
        return dist
