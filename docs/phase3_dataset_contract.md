# Phase 3.4 Dataset Contract

**Schema version:** `phase3-contract-v1` (immutable; tied to no future phase number)

---

## LabelVector Field List and Order

Fields are LOCKED. HDF5 dataset names are derived by prepending `label__`.

| # | Field | HDF5 Dataset | dtype | Notes |
|---|-------|-------------|-------|-------|
| 1 | `event_class` | `label__event_class` | uint8 | PSPL=0, FSPL_STAR=1, PLANETARY_CAUSTIC=2, STELLAR_BINARY=3, HIGH_MAGNIFICATION_CUSP=4 |
| 2 | `log_tE` | `label__log_tE` | float32 | log₁₀ of Einstein ring crossing time (days) |
| 3 | `log_u0` | `label__log_u0` | float32 | log₁₀ of impact parameter |
| 4 | `log_rho` | `label__log_rho` | float32 | log₁₀ of source size (θ_*/θ_E) |
| 5 | `alpha_rad` | `label__alpha_rad` | float32 | Binary axis angle (radians) |
| 6 | `log_q` | `label__log_q` | float32 | log₁₀ of binary mass ratio |
| 7 | `log_s` | `label__log_s` | float32 | log₁₀ of binary separation |
| 8 | `t0_mjd_normalized` | `label__t0_mjd_normalized` | float32 | Peak time, normalized to [0, 1] over survey window |
| 9 | `source_mag_F146_ab` | `label__source_mag_F146_ab` | float32 | Source magnitude, F146 band, AB system |
| 10 | `lens_mass_msun` | `label__lens_mass_msun` | float32 | Lens mass (M☉) |
| 11 | `source_distance_kpc` | `label__source_distance_kpc` | float32 | Source distance (kpc) |
| 12 | `lens_distance_kpc` | `label__lens_distance_kpc` | float32 | Lens distance (kpc) |

---

## HDF5 Flat Shard Layout

One HDF5 file per shard. All datasets are flat arrays (no compound dtypes, no per-event groups).
Compression: `("gzip", 4)` (h5py built-in). No BLOSC, no pyarrow, no parquet.

| Dataset | Shape | dtype | Chunks | Notes |
|---------|-------|-------|--------|-------|
| `/science_stamps` | `(N, n_epochs, 64, 64)` | float32 | `(1, n_epochs, 64, 64)` | DataLoader-friendly row chunking |
| `/saturation_stamps` | `(N, n_epochs, 64, 64)` | uint8 | — | Omit per-shard if Phase 2 did not produce |
| `/cr_stamps` | `(N, n_epochs, 64, 64)` | uint8 | — | Omit per-shard if Phase 2 did not produce |
| `/label__event_class` | `(N,)` | uint8 | — | |
| `/label__log_tE` … `/label__lens_distance_kpc` | `(N,)` | float32 | — | 11 fields, see table above |
| `/event_id` | `(N,)` | variable-length str | — | |
| `/starfield_seed` | `(N,)` | uint64 | — | Values < 2⁵³ (JSON-safe) |
| `/shard_row_index` | `(N,)` | uint32 | — | O(1) intra-shard lookup |

**File attributes:**

| Attribute | Type | Value / Example |
|-----------|------|-----------------|
| `schema_version` | str | `"phase3-contract-v1"` |
| `shard_id` | int | e.g. `0` |
| `n_epochs` | int | per-dataset integer; stored here, not compile-time |
| `smig_version` | str | package version string |
| `writer_backend` | str | `"h5py"` |

---

## Manifest JSON Shape

Must match `scripts/validate_splits.py` exactly.

```json
{
  "events": [
    {
      "event_id": "ob230001",
      "split": "train",
      "starfield_seed": 42,
      "params": {
        "t_E": 30.0,
        "u_0": 0.1,
        "s": 1.0,
        "q": 0.001
      }
    }
  ]
}
```

**Required event keys:** `event_id`, `split`, `starfield_seed`, `params`

**Serialization rules:**
- All dict keys sorted (`sort_keys=True` throughout)
- `starfield_seed` is a JSON integer (not float, not bool)
- No NaN or Inf in `params`
- Parquet sidecar: FORBIDDEN in Phase 3.4 (may be added in Phase 4)

---

## Split Rule Algorithm

Assignment is **purely a function of `starfield_seed`**. All events sharing a `starfield_seed` land in the same split (required by `validate_splits.py` leakage check).

```python
import hashlib

def assign_split(starfield_seed: int, ratios=(0.8, 0.1, 0.1)):
    digest = hashlib.sha256(f"{starfield_seed}".encode()).digest()
    bucket = int.from_bytes(digest[:8], "little") % 10000
    train_end = int(ratios[0] * 10000)   # 8000
    val_end   = train_end + int(ratios[1] * 10000)  # 9000
    if bucket < train_end:  return "train"
    if bucket < val_end:    return "val"
    return "test"
```

`catalog_tile_id` and `source_star_id` are accepted by `assign_split()` for Phase 4 auditing via `manifest.params` but **do not affect the bucket computation**.

---

## Schema Version

`DATASET_SCHEMA_VERSION = "phase3-contract-v1"` — not tied to phase numbering; this string is immutable going forward. A structural change requires a new version string and explicit sign-off.
