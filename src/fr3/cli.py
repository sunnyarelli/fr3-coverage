"""Compare FR1, FR3 (6G candidate) and FR2 coverage and throughput."""
from __future__ import annotations

import argparse

from .budget import DEFAULT_CARRIERS, MAX_RANGE_M, cell_edge_range, snr_db, throughput_mbps


def _range(m: float) -> str:
    return f">{MAX_RANGE_M:.0f}m" if m >= MAX_RANGE_M else f"{m:.0f}m"


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="FR3 (7-24 GHz) link budget vs FR1/FR2, TR 38.901")
    p.add_argument("--scenario", choices=["UMa", "UMi"], default="UMa")
    p.add_argument("--distance", type=float, default=300.0, help="2D distance for throughput [m]")
    p.add_argument("--min-snr", type=float, default=-5.0, help="cell-edge SNR threshold [dB]")
    a = p.parse_args(argv)

    print(f"Scenario {a.scenario}, throughput at {a.distance:.0f} m, cell edge at SNR >= {a.min_snr} dB\n")
    head = (f"{'carrier':<18}{'BW':>6}{'elem':>6}{'EIRP':>7}"
            f"{'SNR NLOS':>10}{'Mbps NLOS':>11}{'edge NLOS':>11}{'edge LOS':>10}{'edge O2I':>10}")
    print(head)
    print("-" * len(head))
    for c in DEFAULT_CARRIERS:
        s = snr_db(c, a.scenario, False, a.distance)
        print(f"{c.name:<18}{c.bandwidth_mhz:>6.0f}{c.bs_elements:>6}{c.eirp_dbm:>7.1f}"
              f"{s:>10.1f}{throughput_mbps(c, s):>11.0f}"
              f"{_range(cell_edge_range(c, a.scenario, False, a.min_snr)):>11}"
              f"{_range(cell_edge_range(c, a.scenario, True, a.min_snr)):>10}"
              f"{_range(cell_edge_range(c, a.scenario, False, a.min_snr, indoor='low')):>10}")


if __name__ == "__main__":
    main()
