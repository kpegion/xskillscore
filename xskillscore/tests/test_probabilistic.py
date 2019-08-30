import numpy as np
import pandas as pd
import pytest

import xarray as xr
from properscoring import crps_ensemble, crps_gaussian, threshold_brier_score
from xarray.tests import assert_identical, assert_allclose
from xskillscore.core.probabilistic import (xr_crps_ensemble, xr_crps_gaussian,
                                            xr_threshold_brier_score)


@pytest.fixture
def o_dask():
    lats = np.arange(4)
    lons = np.arange(5)
    data = np.random.rand(len(lats), len(lons))
    return xr.DataArray(data,
                        coords=[lats, lons],
                        dims=['lat', 'lon']).chunk()


@pytest.fixture
def f_dask():
    members = np.arange(3)
    lats = np.arange(4)
    lons = np.arange(5)
    data = np.random.rand(len(members), len(lats), len(lons))
    return xr.DataArray(data,
                        coords=[members, lats, lons],
                        dims=['member', 'lat', 'lon']).chunk()


def test_xr_crps_ensemble_dask(o_dask, f_dask):
    actual = xr_crps_ensemble(o_dask, f_dask)
    expected = crps_ensemble(o_dask, f_dask, axis=0)
    expected = xr.DataArray(expected, coords=o_dask.coords)
    # test for numerical identity of xr_crps and crps
    assert_allclose(actual, expected)
    # test that xr_crps_ensemble returns chunks
    assert actual.chunks is not None
    # show that crps_ensemble returns no chunks
    assert expected.chunks is None


def test_xr_crps_gaussian_dask(o_dask, f_dask):
    mu = f_dask.mean('member')
    sig = f_dask.std('member')
    actual = xr_crps_gaussian(o_dask, mu, sig)
    expected = crps_gaussian(o_dask, mu, sig)
    expected = xr.DataArray(expected, coords=o_dask.coords)
    # test for numerical identity of xr_crps and crps
    assert_allclose(actual, expected)
    # test that xr_crps_ensemble returns chunks
    assert actual.chunks is not None
    # show that crps_ensemble returns no chunks
    assert expected.chunks is None


def test_xr_threshold_brier_score_dask(o_dask, f_dask):
    threshold = .5
    actual = xr_threshold_brier_score(o_dask, f_dask, threshold)
    expected = threshold_brier_score(o_dask, f_dask, threshold, axis=0)
    expected = xr.DataArray(expected, coords=o_dask.coords)
    # test for numerical identity of xr_threshold and threshold
    assert_identical(actual, expected)
    # test that xr_crps_ensemble returns chunks
    assert actual.chunks is not None
    # show that crps_ensemble returns no chunks
    assert expected.chunks is None


def test_xr_crps_gaussian_dask_b_int(o_dask):
    mu = 0
    sig = 1
    actual = xr_crps_gaussian(o_dask, mu, sig)
    assert actual is not None


def test_xr_threshold_brier_score_dask_b_float(o_dask, f_dask):
    threshold = .5
    actual = xr_threshold_brier_score(o_dask, f_dask, threshold)
    assert actual is not None


def test_xr_threshold_brier_score_dask_b_int(o_dask, f_dask):
    threshold = 0
    actual = xr_threshold_brier_score(o_dask, f_dask, threshold)
    assert actual is not None


@pytest.mark.skip(reason="multiple thresholds not implemented")
def test_xr_threshold_brier_score_multiple_thresholds(o_dask, f_dask):
    threshold = [.1, .3, .5]
    actual = xr_threshold_brier_score(
        o_dask.compute(), f_dask.compute(), threshold)
    assert actual.chunks is None


@pytest.mark.skip(reason="multiple thresholds not implemented")
def test_xr_threshold_brier_score_multiple_thresholds_dask(o_dask, f_dask):
    threshold = xr.DataArray([.1, .3, .5]).chunk()
    actual = xr_threshold_brier_score(o_dask, f_dask, threshold)
    assert actual.chunks is not None
