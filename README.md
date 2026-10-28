# fr3-coverage

[![CI](https://github.com/sunnyarelli/fr3-coverage/actions/workflows/ci.yml/badge.svg)](https://github.com/sunnyarelli/fr3-coverage/actions/workflows/ci.yml)

Link budget and coverage comparison for the **6G FR3 band (7–24 GHz)** against today's FR1 (3.5 GHz) and FR2 (28 GHz).
The Rel-19 study on 7–24 GHz and the Rel-20 6G study target FR3, especially 7.125–8.4 GHz and the upper bands
around 12.7–15.35 GHz, as the primary new 6G spectrum.

Pure Python + NumPy.

## What it does

| Module | Contents |
|---|---|
| `fr3.pathloss` | TR 38.901 UMa and UMi-Street-Canyon LOS/NLOS path loss with breakpoint, LOS probability, shadow-fading σ, O2I low/high-loss building penetration |
| `fr3.budget` | Downlink SNR, attenuated-Shannon throughput, cell-edge range search, and a **same-aperture** antenna scaling helper |

**Same aperture:** keeping the gNB panel the same physical size, the element count grows with (f/f₀)². The extra array
gain (+6 dB per frequency doubling) cancels the 20·log₁₀(f) free-space term. This is the core argument for FR3 reusing
FR1 sites.

## Quick start

```bash
pip install -e ".[dev]"
pytest -q
fr3-coverage
fr3-coverage --scenario UMi --distance 200 --min-snr 0
```

Sample output (UMa, 12 dB margin, noise-limited):

```
carrier               BW  elem   EIRP  SNR NLOS  Mbps NLOS  edge NLOS  edge LOS  edge O2I
-----------------------------------------------------------------------------------------
FR1 n78 3.5 GHz      100   192   83.8      35.6        532      3282m    >5000m     1075m
FR3 7 GHz            200   768   89.9      32.5        973      2749m    >5000m      852m
FR3 10 GHz           400  1567   93.0      29.5       1766      2302m    >5000m      688m
FR3 15 GHz           400  3527   96.5      29.5       1766      2302m    >5000m      649m
FR2 n257 28 GHz      400   256   69.1      -3.3        100       332m    >5000m       77m
```

Takeaways: with the same aperture, FR3 keeps most of FR1's outdoor coverage while delivering 2–3× the throughput.
**Outdoor-to-indoor loss** is what really separates the bands.

## Assumptions and limitations

- Single cell, noise-limited SNR. Inter-cell interference is folded into `margin_db`, not simulated.
- Full array gain is assumed on the served beam. Real per-beam EIRP depends on beam management and the number of TXRUs.
- UMa effective environment height h_E = 1 m. Ranges are capped at 5 km, the TR 38.901 validity limit.
- The FR3 carrier parameters (power, bandwidth, element count) are illustrative, not agreed 3GPP values.

## References

- 3GPP TR 38.901, *Channel model for frequencies from 0.5 to 100 GHz* (Tables 7.4.1-1, 7.4.2-1, 7.4.3-2)
- 3GPP TR 38.820, *7–24 GHz frequency range* (Rel-16 study)
- 3GPP TR 36.942 (attenuated Shannon throughput mapping)

## License

MIT
