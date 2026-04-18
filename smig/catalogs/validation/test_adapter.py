"""Tests for smig.catalogs.adapter — ProjectedStarTable DataFrame emitter."""
from __future__ import annotations

import numpy as np
import pytest

pandas = pytest.importorskip("pandas", reason="pandas not installed")
astropy = pytest.importorskip("astropy", reason="astropy not installed")

from smig.catalogs.adapter import project_to_sca_dataframe
from smig.catalogs.base import StarRecord
from smig.catalogs.synthetic import SyntheticCatalogProvider

# Import the authoritative column tuple from the renderer (not hardcoded here).
from smig.rendering.crowding import _REQUIRED_COLUMNS as _RENDERER_COLS


def _make_stars(n: int = 5) -> list[StarRecord]:
    rng = np.random.default_rng(42)
    provider = SyntheticCatalogProvider(n_stars=n)
    return provider.sample_field(l_deg=1.0, b_deg=-3.0, fov_deg=0.28, rng=rng)


class TestAdapterColumns:
    def test_columns_match_renderer_required(self):
        """Output DataFrame columns must equal _REQUIRED_COLUMNS exactly."""
        stars = _make_stars()
        df = project_to_sca_dataframe(stars, sca_id=1, field_center_l_deg=1.0,
                                      field_center_b_deg=-3.0, exposure_s=139.8)
        assert tuple(df.columns) == _RENDERER_COLS

    def test_columns_are_not_hardcoded_subset(self):
        """Verify the columns we check come from the renderer import, not a literal."""
        assert "x_pix" in _RENDERER_COLS
        assert "y_pix" in _RENDERER_COLS
        assert "flux_e" in _RENDERER_COLS
        assert "mag_w146" in _RENDERER_COLS

    def test_empty_stars_valid_dataframe(self):
        df = project_to_sca_dataframe([], sca_id=1, field_center_l_deg=1.0,
                                      field_center_b_deg=-3.0, exposure_s=139.8)
        assert tuple(df.columns) == _RENDERER_COLS
        assert len(df) == 0


class TestAdapterDtypes:
    def test_all_float64(self):
        stars = _make_stars()
        df = project_to_sca_dataframe(stars, sca_id=1, field_center_l_deg=1.0,
                                      field_center_b_deg=-3.0, exposure_s=139.8)
        for col in _RENDERER_COLS:
            assert df[col].dtype == np.float64, f"Column {col!r} is not float64"


class TestAdapterValues:
    def test_flux_e_positive(self):
        stars = _make_stars(20)
        df = project_to_sca_dataframe(stars, sca_id=1, field_center_l_deg=1.0,
                                      field_center_b_deg=-3.0, exposure_s=139.8)
        assert (df["flux_e"] > 0.0).all()

    def test_mag_w146_matches_star_mag(self):
        """mag_w146 must equal StarRecord.mag_F146_ab."""
        rng = np.random.default_rng(0)
        provider = SyntheticCatalogProvider(n_stars=10)
        stars = provider.sample_field(1.0, -3.0, 0.28, rng)
        df = project_to_sca_dataframe(stars, sca_id=1, field_center_l_deg=1.0,
                                      field_center_b_deg=-3.0, exposure_s=139.8)
        for i, star in enumerate(stars):
            assert df["mag_w146"].iloc[i] == pytest.approx(star.mag_F146_ab)

    def test_row_count_matches_input(self):
        stars = _make_stars(15)
        df = project_to_sca_dataframe(stars, sca_id=1, field_center_l_deg=1.0,
                                      field_center_b_deg=-3.0, exposure_s=139.8)
        assert len(df) == 15
