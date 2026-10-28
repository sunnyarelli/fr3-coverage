"""Downlink link budget and cell-edge range for FR1 vs. 6G FR3 carriers."""
from __future__ import annotations

from dataclasses import dataclass
from math import log10, log2

from .pathloss import o2i_loss, pathloss

KT_DBM_HZ = -174.0
MAX_RANGE_M = 5_000.0


@dataclass
class Carrier:
    name: str
    fc_ghz: float
    bandwidth_mhz: float
    bs_power_dbm: float = 53.0          # 200 W
    bs_elements: int = 192              # active elements behind the panel
    bs_element_gain_dbi: float = 8.0
    ue_gain_dbi: float = 0.0
    ue_nf_db: float = 9.0
    margin_db: float = 12.0             # shadowing (~1.28 sigma), body loss, interference rise
    overhead: float = 0.25              # RS / control / guard overhead
    max_se: float = 7.4                 # 256QAM, ~0.93 code rate

    @classmethod
    def same_aperture(cls, name, fc_ghz, bandwidth_mhz, ref_fc_ghz=3.5, ref_elements=192, **kw):
        """Keep the physical panel size: element count grows with (f / f_ref)^2."""
        n = int(round(ref_elements * (fc_ghz / ref_fc_ghz) ** 2))
        return cls(name, fc_ghz, bandwidth_mhz, bs_elements=n, **kw)

    @property
    def eirp_dbm(self) -> float:
        # Array gain on the beam; total conducted power is fixed across bands.
        return self.bs_power_dbm + self.bs_element_gain_dbi + 10 * log10(self.bs_elements)

    @property
    def noise_dbm(self) -> float:
        return KT_DBM_HZ + 10 * log10(self.bandwidth_mhz * 1e6) + self.ue_nf_db


def snr_db(c: Carrier, scenario: str, los: bool, d2d: float, indoor: str | None = None) -> float:
    pl = pathloss(scenario, los, d2d, c.fc_ghz)
    if indoor:
        pl += o2i_loss(c.fc_ghz, indoor)
    return c.eirp_dbm + c.ue_gain_dbi - pl - c.margin_db - c.noise_dbm


def throughput_mbps(c: Carrier, snr: float) -> float:
    """Attenuated Shannon (TR 36.942 style, alpha = 0.6) with SE cap and overhead."""
    se = min(0.6 * log2(1 + 10 ** (snr / 10)), c.max_se) if snr > -10 else 0.0
    return c.bandwidth_mhz * se * (1 - c.overhead)


def cell_edge_range(c: Carrier, scenario: str, los: bool, min_snr_db: float = -5.0,
                    indoor: str | None = None) -> float:
    """Largest 2D distance with SNR >= threshold (path loss is monotonic in distance).

    Capped at MAX_RANGE_M, the upper validity limit of the TR 38.901 UMa/UMi models.
    """
    lo, hi = 10.0, MAX_RANGE_M
    if snr_db(c, scenario, los, lo, indoor) < min_snr_db:
        return 0.0
    if snr_db(c, scenario, los, hi, indoor) >= min_snr_db:
        return hi
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if snr_db(c, scenario, los, mid, indoor) >= min_snr_db else (lo, mid)
    return lo


DEFAULT_CARRIERS = [
    Carrier("FR1 n78 3.5 GHz", 3.5, 100),
    Carrier.same_aperture("FR3 7 GHz", 7.0, 200),
    Carrier.same_aperture("FR3 10 GHz", 10.0, 400),
    Carrier.same_aperture("FR3 15 GHz", 15.0, 400),
    Carrier("FR2 n257 28 GHz", 28.0, 400, bs_power_dbm=40.0, bs_elements=256, bs_element_gain_dbi=5.0),
]
