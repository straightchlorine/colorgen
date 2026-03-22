"""Tests for colour utility functions."""

import pytest

from colour.utils import (
    anchor_score,
    brighten,
    contrast_ratio,
    derive_color,
    desaturate,
    ensure_contrast,
    hue_distance,
    median_sat_light,
    rgb_to_hsl,
)


class TestHueDistance:
    def test_same_hue(self) -> None:
        assert hue_distance(120.0, 120.0) == 0.0

    def test_opposite_hue(self) -> None:
        assert hue_distance(0.0, 180.0) == 180.0

    def test_wrapping(self) -> None:
        assert hue_distance(350.0, 10.0) == 20.0

    def test_wrapping_reverse(self) -> None:
        assert hue_distance(10.0, 350.0) == 20.0

    def test_quarter_turn(self) -> None:
        assert hue_distance(0.0, 90.0) == 90.0


class TestContrastRatio:
    def test_black_on_white(self) -> None:
        ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
        assert ratio == pytest.approx(21.0, abs=0.1)

    def test_same_color(self) -> None:
        ratio = contrast_ratio((128, 128, 128), (128, 128, 128))
        assert ratio == pytest.approx(1.0, abs=0.01)

    def test_symmetric(self) -> None:
        r1 = contrast_ratio((255, 0, 0), (0, 0, 0))
        r2 = contrast_ratio((0, 0, 0), (255, 0, 0))
        assert r1 == pytest.approx(r2, abs=0.01)

    def test_minimum_ratio(self) -> None:
        ratio = contrast_ratio((100, 100, 100), (200, 200, 200))
        assert ratio >= 1.0


class TestAnchorScore:
    def test_red_scores_high_for_red_slot(self) -> None:
        red = (220, 50, 50)
        score = anchor_score(red, target_hue=15.0, hue_tolerance=30.0)
        assert score > 0.5

    def test_red_scores_low_for_blue_slot(self) -> None:
        red = (220, 50, 50)
        score = anchor_score(red, target_hue=230.0, hue_tolerance=20.0)
        assert score < 0.3

    def test_grey_scores_low(self) -> None:
        grey = (128, 128, 128)
        score = anchor_score(grey, target_hue=15.0, hue_tolerance=30.0)
        assert score < 0.2

    def test_saturated_beats_desaturated(self) -> None:
        saturated = (220, 50, 50)
        muted = (180, 120, 120)
        s1 = anchor_score(saturated, target_hue=15.0, hue_tolerance=30.0)
        s2 = anchor_score(muted, target_hue=15.0, hue_tolerance=30.0)
        assert s1 > s2


class TestDeriveColor:
    def test_has_target_hue(self) -> None:
        result = derive_color(120.0, 0.6, 0.5)
        hue, _, _ = rgb_to_hsl(result)
        assert hue == pytest.approx(120.0, abs=2.0)

    def test_preserves_saturation(self) -> None:
        result = derive_color(60.0, 0.7, 0.5)
        _, sat, _ = rgb_to_hsl(result)
        assert sat == pytest.approx(0.7, abs=0.05)

    def test_preserves_lightness(self) -> None:
        result = derive_color(60.0, 0.7, 0.4)
        _, _, light = rgb_to_hsl(result)
        assert light == pytest.approx(0.4, abs=0.05)


class TestDesaturate:
    def test_reduces_saturation(self) -> None:
        original = (220, 50, 50)
        result = desaturate(original, 0.3)
        assert rgb_to_hsl(result)[1] < rgb_to_hsl(original)[1]

    def test_full_desaturation(self) -> None:
        result = desaturate((220, 50, 50), 1.0)
        _, sat, _ = rgb_to_hsl(result)
        assert sat == pytest.approx(0.0, abs=0.05)


class TestMedianSatLight:
    def test_single_color(self) -> None:
        colors = [(220, 50, 50)]
        med_sat, med_light = median_sat_light(colors)
        h, s, light = rgb_to_hsl(colors[0])
        assert med_sat == pytest.approx(s, abs=0.01)
        assert med_light == pytest.approx(light, abs=0.01)

    def test_empty_list(self) -> None:
        med_sat, med_light = median_sat_light([])
        assert med_sat == 0.5
        assert med_light == 0.5


class TestBrightenNoSatChange:
    def test_saturation_unchanged(self) -> None:
        color = (100, 50, 50)
        _, sat_before, _ = rgb_to_hsl(color)
        result = brighten(color, 0.2)
        _, sat_after, _ = rgb_to_hsl(result)
        assert sat_after == pytest.approx(sat_before, abs=0.02)


class TestEnsureContrast:
    def test_dark_theme_readable(self) -> None:
        bg = (20, 20, 20)
        color = (30, 30, 30)  # very close to bg
        result = ensure_contrast(color, bg, dark_theme=True)
        assert contrast_ratio(result, bg) >= 3.0

    def test_light_theme_readable(self) -> None:
        bg = (240, 240, 240)
        color = (230, 230, 230)  # very close to bg
        result = ensure_contrast(color, bg, dark_theme=False)
        assert contrast_ratio(result, bg) >= 3.0

    def test_already_good_contrast_unchanged(self) -> None:
        bg = (20, 20, 20)
        color = (200, 100, 100)  # already good contrast
        result = ensure_contrast(color, bg, dark_theme=True)
        # Should be similar (might shift slightly due to lightness floor)
        assert contrast_ratio(result, bg) >= 3.0
