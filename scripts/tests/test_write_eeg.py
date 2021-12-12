import pytest
from scripts.data import write, load

import os
import mne_bids


@pytest.fixture
def overwrite_params(default_params):
    default_params["load_data"]["overwrite"] = False
    return default_params


@pytest.fixture
def non_path_params(default_params, tmp_path):
    default_params["output_root"] = tmp_path / "CMI"
    return default_params


@pytest.fixture
def tmp_func():
    return "TEMP"


def test_write(default_params, tmp_func):
    data_params = default_params["load_data"]

    ch_type = data_params["channel_type"]
    write_root = data_params["output_root"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        write.write_eeg_data(eeg_obj, tmp_func, file, ch_type, 0, write_root)
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1


def test_non_path(non_path_params, tmp_func):
    data_params = non_path_params["load_data"]

    ch_type = data_params["channel_type"]
    write_root = data_params["output_root"]

    data = load.load_files(data_params)
    for file in data:
        eeg_obj = mne_bids.read_raw_bids(file)
        # first write
        write.write_eeg_data(eeg_obj, tmp_func, file,
                             ch_type, 0, write_root)
        # assert file exists even if path initially does not
        for _, dirnames, filenames in os.walk(write_root):
            # if at bottom-most directory, assert one file has been written
            if not dirnames:
                assert len(filenames) == 1
