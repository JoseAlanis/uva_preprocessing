"""Script to prepare directory for results.

NOTE: This script only needs to be run once **before** running the preprocessing
and analysis pipelines.

The script will create:
1. The `derivatives/` directory at the location specified in the `paths.json`
file.

**The script will throw and error if there is a directory with the same name
at the same location.**
"""
# %%
# imports
from os import path
from pathlib import Path

from config import (
    FPATH_DATA_DERIVATIVES
)

# check if derivatives dir is already there, if not, create it.
if FPATH_DATA_DERIVATIVES.exists():
    raise RuntimeError("The derivatives directory is already there,"
                       "stopping execution.")
else:
    # create derivatives directory along with subdirectories
    FPATH_DATA_DERIVATIVES.mkdir(exist_ok=True)
    # preprocessing
    FPATH_PREPROCESSING = path.join(FPATH_DATA_DERIVATIVES, 'preprocessing')
    Path(FPATH_PREPROCESSING).mkdir(exist_ok=True)
    # bad channels
    FPATH_BADS = path.join(FPATH_PREPROCESSING, 'bad_channels')
    Path(FPATH_BADS).mkdir(exist_ok=True)
    # preprocessed data
    FPATH_PREPROCESSED = path.join(FPATH_PREPROCESSING, 'preprocessed')
    Path(FPATH_PREPROCESSED).mkdir(exist_ok=True)
    # ICA
    FPATH_ICA = path.join(FPATH_PREPROCESSING, 'ICA')
    Path(FPATH_ICA).mkdir(exist_ok=True)
    # RT
    FPATH_RT = path.join(FPATH_DATA_DERIVATIVES, 'rt')
    Path(FPATH_RT).mkdir(exist_ok=True)
    # EPOCHS
    FPATH_EPOCHS = path.join(FPATH_DATA_DERIVATIVES, 'epochs')
    Path(FPATH_EPOCHS).mkdir(exist_ok=True)
