"""3GPP TR 38.901 (v17/v18) UMa / UMi-Street Canyon path loss, LOS probability and O2I loss.

Frequencies are in GHz and distances in metres, as in the TR tables. The UMa
effective environment height h_E is fixed to 1 m (the TR draws it randomly
for UT heights above 13 m).
"""
from __future__ import annotations

from math import exp, hypot, log10

C = 299_792_458.0


def _breakpoint(h_bs: float, h_ut: float, fc_ghz: float, h_e: float = 1.0) -> float:
    return 4 * (h_bs - h_e) * (h_ut - h_e) * fc_ghz * 1e9 / C


def uma_los(d2d: float, fc: float, h_bs: float = 25.0, h_ut: float = 1.5) -> float:
    d3d = hypot(d2d, h_bs - h_ut)
    dbp = _breakpoint(h_bs, h_ut, fc)
    if d2d <= dbp:
        return 28.0 + 22 * log10(d3d) + 20 * log10(fc)
    return 28.0 + 40 * log10(d3d) + 20 * log10(fc) - 9 * log10(dbp ** 2 + (h_bs - h_ut) ** 2)


def uma_nlos(d2d: float, fc: float, h_bs: float = 25.0, h_ut: float = 1.5) -> float:
    d3d = hypot(d2d, h_bs - h_ut)
    pl = 13.54 + 39.08 * log10(d3d) + 20 * log10(fc) - 0.6 * (h_ut - 1.5)
    return max(uma_los(d2d, fc, h_bs, h_ut), pl)


def umi_los(d2d: float, fc: float, h_bs: float = 10.0, h_ut: float = 1.5) -> float:
    d3d = hypot(d2d, h_bs - h_ut)
    dbp = _breakpoint(h_bs, h_ut, fc)
    if d2d <= dbp:
        return 32.4 + 21 * log10(d3d) + 20 * log10(fc)
    return 32.4 + 40 * log10(d3d) + 20 * log10(fc) - 9.5 * log10(dbp ** 2 + (h_bs - h_ut) ** 2)


def umi_nlos(d2d: float, fc: float, h_bs: float = 10.0, h_ut: float = 1.5) -> float:
    d3d = hypot(d2d, h_bs - h_ut)
    pl = 22.4 + 35.3 * log10(d3d) + 21.3 * log10(fc) - 0.3 * (h_ut - 1.5)
    return max(umi_los(d2d, fc, h_bs, h_ut), pl)


def p_los(scenario: str, d2d: float) -> float:
    if d2d <= 18:
        return 1.0
    if scenario == "UMa":                   # h_UT <= 13 m
        return 18 / d2d + exp(-d2d / 63) * (1 - 18 / d2d)
    if scenario == "UMi":
        return 18 / d2d + exp(-d2d / 36) * (1 - 18 / d2d)
    raise ValueError(scenario)


SHADOW_STD_DB = {("UMa", True): 4.0, ("UMa", False): 6.0, ("UMi", True): 4.0, ("UMi", False): 7.82}

_MODELS = {("UMa", True): uma_los, ("UMa", False): uma_nlos,
           ("UMi", True): umi_los, ("UMi", False): umi_nlos}


def pathloss(scenario: str, los: bool, d2d: float, fc: float, **heights) -> float:
    return _MODELS[(scenario, los)](d2d, fc, **heights)


def o2i_loss(fc: float, model: str = "low", d2d_in: float = 12.5) -> float:
    """Building penetration (TR 38.901 Table 7.4.3-2) + indoor loss, mean values only."""
    l_glass, l_irr, l_concrete = 2 + 0.2 * fc, 23 + 0.3 * fc, 5 + 4 * fc
    if model == "low":
        tw = 5 - 10 * log10(0.3 * 10 ** (-l_glass / 10) + 0.7 * 10 ** (-l_concrete / 10))
    elif model == "high":
        tw = 5 - 10 * log10(0.7 * 10 ** (-l_irr / 10) + 0.3 * 10 ** (-l_concrete / 10))
    else:
        raise ValueError(model)
    return tw + 0.5 * d2d_in
