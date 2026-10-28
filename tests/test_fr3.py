from math import hypot, log10

import pytest

from fr3.budget import Carrier, cell_edge_range, snr_db, throughput_mbps
from fr3.pathloss import o2i_loss, p_los, uma_los, uma_nlos, umi_los, umi_nlos


def test_umi_los_before_breakpoint_matches_formula():
    d3d = hypot(100, 8.5)
    assert umi_los(100, 10.0) == pytest.approx(32.4 + 21 * log10(d3d) + 20)


@pytest.mark.parametrize("model", [uma_los, umi_los])
def test_los_continuous_at_breakpoint(model):
    h_bs = 25.0 if model is uma_los else 10.0
    dbp = 4 * (h_bs - 1) * 0.5 * 3.5e9 / 299_792_458.0
    assert model(dbp - 1e-6, 3.5) == pytest.approx(model(dbp + 1e-6, 3.5), abs=0.05)


@pytest.mark.parametrize("los,nlos", [(uma_los, uma_nlos), (umi_los, umi_nlos)])
def test_nlos_never_below_los(los, nlos):
    for d in (20, 100, 500, 2000):
        for f in (3.5, 7, 15):
            assert nlos(d, f) >= los(d, f)


def test_los_probability_bounds():
    assert p_los("UMa", 10) == 1.0
    assert 0 < p_los("UMi", 200) < p_los("UMi", 50) < 1


def test_o2i_high_loss_exceeds_low_loss_and_grows_with_frequency():
    assert o2i_loss(7, "high") > o2i_loss(7, "low")
    assert o2i_loss(15, "low") > o2i_loss(3.5, "low")


def test_same_aperture_scaling_quadruples_elements_at_double_frequency():
    assert Carrier.same_aperture("x", 7.0, 200).bs_elements == 4 * 192


def test_same_aperture_recovers_most_of_the_frequency_loss():
    fr1 = Carrier("a", 3.5, 100)
    fr3 = Carrier.same_aperture("b", 7.0, 100)
    # +6 dB path loss from 20log10(f), +6 dB array gain from 4x elements
    assert snr_db(fr3, "UMa", False, 300) == pytest.approx(snr_db(fr1, "UMa", False, 300), abs=0.5)


def test_cell_edge_and_throughput_monotonic():
    c = Carrier("a", 3.5, 100)
    assert cell_edge_range(c, "UMa", True) > cell_edge_range(c, "UMa", False)
    assert throughput_mbps(c, 20) > throughput_mbps(c, 0) > 0
