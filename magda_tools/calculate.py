from datetime import datetime, timedelta

import numpy as np

SLT_OMEGA = 26.75
SLT_ALPHA = 10759.5
SLT_PHI = 4.1
SLT_K = 0.0

SECS_PER_DAY = 86400

# standard value for Saturn equitorial radius
SATURN_RADIUS_KM = 60268.0


def saturn_local_time(time, x_ksm, y_ksm, z_ksm):
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
    timestamp = np.vectorize(datetime.timestamp)
    days_since_epoch = timestamp(time.utc.datetime) / SECS_PER_DAY

    lambda_ = (
        SLT_OMEGA * np.sin((2 * np.pi * days_since_epoch / SLT_ALPHA) + SLT_PHI) - SLT_K
    )
    X = (x_ksm * np.cos(lambda_ * np.pi / 180)) - (
        z_ksm * np.sin(lambda_ * np.pi / 180)
    )

    phi = (np.arctan2(y_ksm, X) * 180 / np.pi) % 360

    td = np.vectorize(timedelta)
    return td(seconds=((12 + (phi * 24 / 360)) % 24) * 3600)


def latitude(x, y, z):
    """For the given x, y and z coordinates provided from a cartesian
    system aligned with the spin-axis of Saturn return the
    corresponding latitude in degrees. If this function is used with a
    coordinate not aligned with the spin access then the returned
    value will not be correct.

    """
    dist = distance(x, y, z)
    return np.arcsin(z / dist) / np.pi * 180


def distance(x, y, z, radius=None):
    """For the given x, y and z coordinates calculate the distance from
    the system origin. If a value is provided for radius the distance
    will be returned as multiples of this value.

    """
    dist = np.sqrt(x * x + y * y + z * z)
    if radius is not None:
        return dist / radius
    else:
        return dist
