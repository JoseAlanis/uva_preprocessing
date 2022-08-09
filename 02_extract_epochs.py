"""
==================================
Extract EEG segments from the data
==================================

Segment EEG data around experimental events

Authors: José C. García Alanis <alanis.jcg@gmail.com>

License: BSD (3-clause)
"""
# %%
# imports
import sys
import os

from pathlib import Path

import numpy as np
import pandas as pd

from mne import events_from_annotations, Epochs
from mne.io import read_raw_fif
from mne.utils import logger

from config import (
    FPATH_DATA_DERIVATIVES,
    FPATH_DERIVATIVES_NOT_FOUND_MSG,
    SUBJECT_IDS
)

from utils import parse_overwrite

# %%
# default settings (use subject 1, don't overwrite output files)
subj = 1
overwrite = False

# %%
# When not in an IPython session, get command line inputs
# https://docs.python.org/3/library/sys.html#sys.ps1
if not hasattr(sys, "ps1"):
    defaults = dict(
        sub=subj,
        overwrite=overwrite,
    )

    defaults = parse_overwrite(defaults)

    subj = defaults["sub"]
    overwrite = defaults["overwrite"]

# %%
# paths and overwrite settings
if subj not in SUBJECT_IDS:
    raise ValueError(f"'{subj}' is not a valid subject ID.\nUse: {SUBJECT_IDS}")

# check if derivatives exists
if not os.path.exists(FPATH_DATA_DERIVATIVES):
    raise RuntimeError(
        FPATH_DERIVATIVES_NOT_FOUND_MSG.format(FPATH_DATA_DERIVATIVES)
    )

if overwrite:
    logger.info("`overwrite` is set to ``True`` ")

# %%
# create bids path for import
str_subj = str(subj).rjust(3, '0')
raw_fname = os.path.join(FPATH_DATA_DERIVATIVES,
                         'preprocessing',
                         'preprocessed',
                         'sub-%s' % str_subj,
                         'sub-%s_preprocessed-raw.fif' % str_subj)
# get the data
raw = read_raw_fif(raw_fname, preload=True)

# only keep EEG channels
raw.pick_types(eeg=True)

# %%
events, event_ids = events_from_annotations(raw, regexp=None)

# get the correct trigger channel values for each event category
cue_vals = []
for key, value in event_ids.items():
    if key.startswith('cue'):
        cue_vals.append(value)

cue_b_vals = []
for key, value in event_ids.items():
    if key.startswith('cue_b'):
        cue_b_vals.append(value)

probe_vals = []
for key, value in event_ids.items():
    if key.startswith('probe'):
        probe_vals.append(value)

probe_y_vals = []
for key, value in event_ids.items():
    if key.startswith('probe_y'):
        probe_y_vals.append(value)

correct_reactions = []
for key, value in event_ids.items():
    if key.startswith('correct'):
        correct_reactions.append(value)

incorrect_reactions = []
for key, value in event_ids.items():
    if key.startswith('incorrect'):
        incorrect_reactions.append(value)

# %%
# global variables
trial = 0
broken = []
sfreq = raw.info['sfreq']
block_end = events[events[:, 2] == event_ids['EDGE boundary'], 0] / sfreq

# placeholders for results
block = []
probe_ids = []
reaction = []
rt = []

# copy of events
new_evs = events.copy()

# loop trough events and recode them
for event in range(len(new_evs[:, 2])):
    # --- if event is a cue stimulus ---
    if new_evs[event, 2] in cue_vals:

        # save block based on onset (before or after break)
        if (new_evs[event, 0] / sfreq) < block_end:
            block.append(0)
        else:
            block.append(1)

        # --- 1st check: if next event is a false reaction ---
        if new_evs[event + 1, 2] in incorrect_reactions:
            # if event is an A-cue
            if new_evs[event, 2] == event_ids['cue_a']:
                # recode as too soon A-cue
                new_evs[event, 2] = 118
            # if event is a B-cue
            elif new_evs[event, 2] in cue_b_vals:
                # recode as too soon B-cue
                new_evs[event, 2] = 119

            # look for next probe
            i = 2
            while new_evs[event + i, 2] not in probe_vals:
                if new_evs[event + i, 2] in cue_vals:
                    broken.append(trial)
                    break
                i += 1

            # if probe is an X
            if new_evs[event + i, 2] == event_ids['probe_x']:
                # recode as too soon X-probe
                new_evs[event + i, 2] = 120
            # if probe is an Y
            elif new_evs[event + i, 2] in probe_y_vals:
                # recode as too soon Y-probe
                new_evs[event + i, 2] = 121

            # save trial information as NaN
            trial += 1
            rt.append(np.nan)
            reaction.append(np.nan)
            # go on to next trial
            continue

        # --- 2nd check: if next event is a probe stimulus ---
        elif new_evs[event + 1, 2] in probe_vals:

            # if event after probe is a reaction
            if new_evs[event + 2, 2] in correct_reactions + incorrect_reactions:

                # save reaction time
                rt.append(
                    (new_evs[event + 2, 0] - new_evs[event + 1, 0]) / sfreq)

                # if reaction is correct
                if new_evs[event + 2, 2] in correct_reactions:

                    # save response
                    reaction.append(1)

                    # if cue was an A
                    if new_evs[event, 2] == event_ids['cue_a']:
                        # recode as correct A-cue
                        new_evs[event, 2] = 122

                        # if probe was an X
                        if new_evs[event + 1, 2] == event_ids['probe_x']:
                            # recode as correct AX probe combination
                            new_evs[event + 1, 2] = 123

                        # if probe was a Y
                        else:
                            # recode as correct AY probe combination
                            new_evs[event + 1, 2] = 124

                        # go on to next trial
                        trial += 1
                        continue

                    # if cue was a B
                    else:
                        # recode as correct B-cue
                        new_evs[event, 2] = 125

                        # if probe was an X
                        if new_evs[event + 1, 2] == event_ids['probe_x']:
                            # recode as correct BX probe combination
                            new_evs[event + 1, 2] = 126
                        # if probe was a Y
                        else:
                            # recode as correct BY probe combination
                            new_evs[event + 1, 2] = 127

                        # go on to next trial
                        trial += 1
                        continue

                # if reaction was incorrect
                else:

                    # save response
                    reaction.append(0)

                    # if cue was an A
                    if new_evs[event, 2] == event_ids['cue_a']:
                        # recode as incorrect A-cue
                        new_evs[event, 2] = 128

                        # if probe was an X
                        if new_evs[event + 1, 2] == event_ids['probe_x']:
                            # recode as incorrect AX probe combination
                            new_evs[event + 1, 2] = 129

                        # if probe was a Y
                        else:
                            # recode as incorrect AY probe combination
                            new_evs[event + 1, 2] = 130

                        # go on to next trial
                        trial += 1
                        continue

                    # if cue was a B
                    else:
                        # recode as incorrect B-cue
                        new_evs[event, 2] = 131

                        # if probe was an X
                        if new_evs[event + 1, 2] == event_ids['probe_x']:
                            # recode as incorrect BX probe combination
                            new_evs[event + 1, 2] = 132

                        # if probe was a Y
                        else:
                            # recode as incorrect BY probe combination
                            new_evs[event + 1, 2] = 133

                        # go on to next trial
                        trial += 1
                        continue

            # if no reaction followed cue-probe combination
            elif new_evs[event + 2, 2] not in \
                    correct_reactions + correct_reactions:

                # save reaction time as NaN
                rt.append(99999)
                reaction.append(np.nan)

                # if cue was an A
                if new_evs[event, 2] == event_ids['cue_a']:
                    # recode as missed A-cue
                    new_evs[event, 2] = 134

                    # if probe was an X
                    if new_evs[event + 1, 2] == event_ids['probe_x']:
                        # recode as missed AX probe combination
                        new_evs[event + 1, 2] = 135

                    # if probe was a Y
                    else:
                        # recode as missed AY probe combination
                        new_evs[event + 1, 2] = 136

                    # go on to next trial
                    trial += 1
                    continue

                # if cue was a B
                else:
                    # recode as missed B-cue
                    new_evs[event, 2] = 137

                    # if probe was an X
                    if new_evs[event + 1, 2] == event_ids['probe_x']:
                        # recode as missed BX probe combination
                        new_evs[event + 1, 2] = 138

                    # if probe was a Y
                    else:
                        # recode as missed BY probe combination
                        new_evs[event + 1, 2] = 139

                    # go on to next trial
                    trial += 1
                    continue

    # skip other events
    else:
        continue

# %%
# cue events
cue_event_id = {'Too_soon A': 118,
                'Too_soon B': 119,

                'Correct A': 122,
                'Correct B': 125,

                'Incorrect A': 128,
                'Incorrect B': 131,

                'Missed A': 134,
                'Missed B': 137}

# probe events
probe_event_id = {'Too_soon X': 120,
                  'Too_soon Y': 121,

                  'Correct AX': 123,
                  'Correct AY': 124,

                  'Correct BX': 126,
                  'Correct BY': 127,

                  'Incorrect AX': 129,
                  'Incorrect AY': 130,

                  'Incorrect BX': 132,
                  'Incorrect BY': 133,

                  'Missed AX': 135,
                  'Missed AY': 136,

                  'Missed BX': 138,
                  'Missed BY': 139}

# %%
# only keep cue events
cue_events = new_evs[np.where((new_evs[:, 2] == 118) |
                              (new_evs[:, 2] == 119) |
                              (new_evs[:, 2] == 122) |
                              (new_evs[:, 2] == 125) |
                              (new_evs[:, 2] == 128) |
                              (new_evs[:, 2] == 131) |
                              (new_evs[:, 2] == 134) |
                              (new_evs[:, 2] == 137))]

# only keep probe events
probe_events = new_evs[np.where((new_evs[:, 2] == 120) |
                                (new_evs[:, 2] == 121) |
                                (new_evs[:, 2] == 123) |
                                (new_evs[:, 2] == 124) |
                                (new_evs[:, 2] == 126) |
                                (new_evs[:, 2] == 127) |
                                (new_evs[:, 2] == 129) |
                                (new_evs[:, 2] == 130) |
                                (new_evs[:, 2] == 132) |
                                (new_evs[:, 2] == 133) |
                                (new_evs[:, 2] == 135) |
                                (new_evs[:, 2] == 136) |
                                (new_evs[:, 2] == 138) |
                                (new_evs[:, 2] == 139))]

# %%

# reversed event_id dict
cue_event_id_rev = {val: key for key, val in cue_event_id.items()}
probe_event_id_rev = {val: key for key, val in probe_event_id.items()}

# check if events shape match
if cue_events.shape[0] != probe_events.shape[0]:
    cue_events = np.delete(cue_events, broken, 0)

# create list with reactions based on cue and probe event ids
same_stim, reaction_cues, reaction_probes, cues, probes, reaction = \
    [], [], [], [], [], []

for cue, probe in zip(cue_events[:, 2], probe_events[:, 2]):
    response, cue = cue_event_id_rev[cue].split(' ')
    reaction_cues.append(response)
    # save cue
    cues.append(cue)

    # save response
    response, probe = probe_event_id_rev[probe].split(' ')
    reaction_probes.append(response)

    if response == 'Correct':
        reaction.append(probe)
    elif response == 'Incorrect':
        if probe == 'AX' and response == 'Incorrect':
            reaction.append('AY')
        elif probe in ['BX', 'BY', 'AY'] and response == 'Incorrect':
            reaction.append('AX')
    else:
        reaction.append(np.nan)

    # check if same type of combination was shown in the previous trail
    if len(probes):
        stim = same_stim[-1]
        if probe == probes[-1] \
                and response == 'Correct' \
                and reaction_probes[-2] == 'Correct':
            stim += 1
            same_stim.append(stim)
        else:
            same_stim.append(0)
    else:
        stim = 0
        same_stim.append(0)

    # save probe
    probes.append(probe)

# create data frame with epochs metadata
metadata = {'block': np.delete(block, broken, 0),
            'trial': np.delete(np.arange(0, trial), broken, 0),
            'cue': cues,
            'probe': probes,
            'run': same_stim,
            'reaction_cues': reaction_cues,
            'reaction_probes': reaction_probes,
            'cond_reaction': reaction,
            'rt': np.delete(rt, broken, 0)}
metadata = pd.DataFrame(metadata)

# save RT measures for later analyses
rt_data = metadata.copy()
rt_data = rt_data.assign(subject=subj)

# create path for preprocessed dara
FPATH_RT = os.path.join(FPATH_DATA_DERIVATIVES,
                            'rt',
                            'sub-%s' % str_subj,
                            'sub-%s_rt.tsv' % str_subj)

# check if directory exists
if not Path(FPATH_RT).exists():
    Path(FPATH_RT).parent.mkdir(parents=True, exist_ok=True)

# save to disk
rt_data.to_csv(FPATH_RT,
               sep='\t',
               index=False)

# %%
# extract the epochs

# rejection threshold
reject = dict(eeg=300e-6)
decim = 1

if raw.info['sfreq'] == 256.0:
    decim = 2
elif raw.info['sfreq'] == 512.0:
    decim = 4
elif raw.info['sfreq'] == 1024.0:
    decim = 8

# extract cue epochs
cue_epochs = Epochs(raw, cue_events, cue_event_id,
                    metadata=metadata,
                    on_missing='ignore',
                    tmin=-2.0,
                    tmax=5.0,
                    baseline=None,
                    preload=True,
                    reject_by_annotation=True,
                    reject=reject,
                    decim=decim
                    )

# clean cue epochs
clean_cues = cue_epochs.selection
bad_cues = [x for x in set(list(range(0, trial)))
            if x not in set(cue_epochs.selection)]

# %%
# save epochs to disk

# create path for preprocessed dara
FPATH_EPOCHS = os.path.join(FPATH_DATA_DERIVATIVES,
                        'epochs',
                        'sub-%s' % str_subj,
                        'sub-%s_cue-epo.fif' % str_subj)

# check if directory exists
if not Path(FPATH_EPOCHS).exists():
    Path(FPATH_EPOCHS).parent.mkdir(parents=True, exist_ok=True)

# resample and save cue epochs to disk
cue_epochs.save(FPATH_EPOCHS, overwrite=overwrite)
