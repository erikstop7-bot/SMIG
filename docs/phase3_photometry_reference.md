# Phase 3 Photometry Reference — Roman WFI F146 AB Zero-Point

**Human-readable provenance mirror. This file is NOT the code authority.**
The authoritative numeric value is `data/catalogs/bandpasses/f146_zero_point.yaml`.
If the zero-point ever changes, update the YAML **and** this document, then
re-run the regression suite to catch drift.

---

## F146 AB Zero-Point

| Parameter | Value |
|---|---|
| `f146_ab_zero_point` | **26.64** (AB mag) |
| Retrieval date | 2024-01-15 |
| Source URL | https://roman.gsfc.nasa.gov/science/Roman_Reference_Information.html |
| STScI bandpass version | `Roman_WFI_F146_2023` |

### Definition

The AB zero-point (ZP) is defined such that a point source with
`mag_ab = ZP` produces **1 electron per second** on a Roman WFI detector:

```
flux_e_per_s = 10 ^ ((ZP - mag_ab) / 2.5)
flux_e       = flux_e_per_s × exposure_s
```

Therefore `mag_ab_to_electrons(ZP, "F146", t_exp) = t_exp` by construction.

### Derivation

Derived from the STScI Roman Exposure Time Calculator (ETC) v2.0 for a flat
AB-spectrum source with the WFI wide-field imaging mode.  The value
incorporates:

- Primary mirror collecting area: ~3.97 m² (2.4 m diameter with central obscuration)
- F146 filter transmission (0.9–2.0 μm, see `data/catalogs/bandpasses/roman_F146.csv`)
- Detector quantum efficiency (H4RG-10 HgCdTe, mean ~65% across F146)
- All other optical elements (secondary mirror, fold mirror, field corrector)

Valid for the centre of SCA01. Per-SCA zero-point variation is < 0.05 mag
and is not modelled in Phase 3.1.

### Equivalence with Phase 2

The `mag_w146` column in the Phase 2 `CrowdedFieldRenderer` DataFrame stores
the F146 AB magnitude.  The `flux_e` column holds total electrons over the
exposure.  `smig.catalogs.photometry.mag_ab_to_electrons` performs this
conversion using the zero-point defined here.

---

*Document version: Phase 3.1 (2024-01-15)*
