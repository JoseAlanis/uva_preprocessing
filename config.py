"""
========================
Study configuration file
========================

Configuration parameters and global values that will be used across scripts.

Authors: Jose C. Garcia Alanis <alanis.jcg@gmail.com>
License: BSD (3-clause)
"""
import os

from pathlib import Path

import numpy as np

import json

from mne.channels import make_standard_montage

# get path to current file
parent = Path(__file__).parent.resolve()

# -----------------------------------------------------------------------------
# file paths
with open(os.path.join(parent, 'paths.json')) as paths:
    paths = json.load(paths)

# the root path of the dataset
FPATH_DATA = paths['root']
# path to sourcedata (biosemi files)
FPATH_DATA_SOURCEDATA = Path(paths['sourcedata'])
# path to BIDS compliant directory structure
FPATH_DATA_BIDS = Path(paths['bidsdata'])
# path to derivatives
FPATH_DATA_DERIVATIVES = Path(paths['derivatives'])

# -----------------------------------------------------------------------------
# file templates
# the path to the sourcedata directory
FNAME_SOURCEDATA_TEMPLATE = os.path.join(
    str(FPATH_DATA_SOURCEDATA),
    "sub-{subj:03}",
    "{dtype}",
    "sub-{subj:03}_dpx_{dtype}{ext}"
)

# -----------------------------------------------------------------------------
# problematic subjects
NO_DATA_SUBJECTS = {}

# originally, subjects from 1 to 151, but some subjects should be excluded
SUBJECT_IDS = np.array(list(set(np.arange(1, 53)) - set(NO_DATA_SUBJECTS)))

# -----------------------------------------------------------------------------
# default messages
FPATH_SOURCEDATA_NOT_FOUND_MSG = (
    "Did not find the path:\n\n>>> {}\n"
    "\n>>Did you define the path to the data on your system in `config.py`? "
    "See the FPATH_DATA_SOURCEDATA variable!<<\n"
)

FPATH_BIDS_NOT_FOUND_MSG = (
    "Did not find the path:\n\n>>> {}\n"
    "\n>>Did you define the path to the data on your system in `config.py`? "
    "See the FPATH_DATA_BIDS variable!<<\n"
)

FPATH_DERIVATIVES_NOT_FOUND_MSG = (
    "Did not find the path:\n\n>>> {}\n"
    "\n>>Did you define the path to the data on your system in `config.py`? "
    "See the FPATH_DATA_DERIVATIVES variable!<<\n"
)

EOG_COMPONENTS_NOT_FOUND_MSG = (
    "No {type} ICA components found for subject {subj}"
)

# -----------------------------------------------------------------------------
# eeg parameters

# import eeg markers
with open(os.path.join(parent, 'eeg_markers.json')) as event_id:
    event_id = json.load(event_id)
event_id = event_id['dpx']['markers']

# create eeg montage
montage = make_standard_montage(kind='biosemi64')

# relevant events
task_events = {
    'cue_a': 1,
    'cue_b1': 2,
    'cue_b2': 3,
    'cue_b3': 4,
    'cue_b4': 5,
    'cue_b5': 6,
    'probe_x': 7,
    'probe_y1': 8,
    'probe_y2': 9,
    'probe_y3': 10,
    'probe_y4': 11,
    'probe_y5': 12,
    'correct_target_button': 12,
    'correct_non_target_button': 13,
    'incorrect_target_button': 15,
    'incorrect_non_target_button': 16,
    'start_record': 17,
    'pause_record': 18,
}

# -----------------------------------------------------------------------------
# templates
# import eeg markers
with open(os.path.join(parent, './ica_templates.json')) as temp:
    ica_templates = json.load(temp)
