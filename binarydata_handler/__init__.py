"""Classes and functions related to handling binary data files."""

import os
import subprocess
import sys
from string import Template

from astropy.time import Time

BDDIR = os.path.dirname(os.path.abspath(__file__))
HEADER_COMMAND_TEMPLATE = Template(f"java -jar {BDDIR}/HeaderFileParser.jar $ffd_path")


def command_executor(command):
    """Executes ``command`` in external process and returns stdout if successful
    otherwise raises subprocess.SubprocessError containing stderr.
    """
    try:
        cp = subprocess.run(  # blocking call
            command.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise subprocess.SubprocessError(e.stderr.decode(sys.getfilesystemencoding()))
    return cp.stdout.decode(sys.getfilesystemencoding()).strip()


def bd_header(dataset):
    """Blocking call of BinaryDataJoiner java code in external process to
    construct ``VirtualMagdaDataFile`` specified by ``dataset``.
    :param dataset: valid ``VirtualMagdaDataFile`` dataset name (str).
    :returns: named tuple containing data from header file
    """

    command = HEADER_COMMAND_TEMPLATE.substitute({"ffd_path": dataset})
    stdout = command_executor(command)
    metadata = dict(s.split(" = ") for s in stdout.split("\n"))
    metadata["timebase"] = Time(
        int(metadata["timebase"]) / 1000, format="unix", scale="tai"
    )  # astropy time object for convenience
    return metadata
