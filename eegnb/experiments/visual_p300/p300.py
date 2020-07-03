import os
from time import time
from glob import glob
from random import choice

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.stimuli import CAT_DOG


def present(duration=120, eeg=None, save_fn=None):
    n_trials = 2010
    iti = 0.4
    soa = 0.3
    jitter = 0.2
    record_duration = np.float32(duration)
    markernames = [1, 2]

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, 'visual_p300', 'unnamed')
            print(f'No path for a save file was passed to the experiment. Saving data to {save_fn}')
        eeg.start(fn=save_fn)

    # Setup trial list
    image_type = np.random.binomial(1, 0.5, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor='testMonitor', units="deg", fullscr=True)

    targets = list(map(load_image, glob(os.path.join(CAT_DOG, 'target-*.jpg'))))
    nontargets = list(map(load_image, glob(os.path.join(CAT_DOG, 'nontarget-*.jpg'))))
    stim = [nontargets, targets]

    # Iterate through the events
    start = time()
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select and display image
        label = trials['image_type'].iloc[ii]
        image = choice(targets if label == 1 else nontargets)
        image.draw()

        # Push sample
        if eeg: eeg.push_sample(marker=markernames[label], timestamp=time())
        mywin.flip()

        # offset
        core.wait(soa)
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()

    # Cleanup
    if eeg: eeg.stop()
    mywin.close()
