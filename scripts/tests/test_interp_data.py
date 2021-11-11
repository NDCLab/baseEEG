import pytest
from scripts.preprocess import preprocess as pre
from mne import Epochs

from scripts.constants import ERROR_KEY


@pytest.fixture
def error_obj():
    return None


def test_return_values(default_params, bids_test_epoch_data):
    # get interpolate params
    feature_params = default_params["preprocess"]
    interp_params = feature_params["interpolate_data"]

    epoch_data = bids_test_epoch_data
    interp_eeg, output_dict = pre.interpolate_data(epoch_data, **interp_params)

    # assert that all data is valid
    assert ERROR_KEY not in output_dict.keys()
    assert isinstance(interp_eeg, Epochs)


def test_bad_object(default_params, error_obj):
    feature_params = default_params["preprocess"]
    interp_param = feature_params["interpolate_data"]

    # attempt to interpolate an invalid object type
    _, output = pre.interpolate_data(error_obj, **interp_param)
    assert ERROR_KEY in output.keys()
