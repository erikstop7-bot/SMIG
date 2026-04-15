# SMIG v2 Phase 2: Optical Modeling & Scene Rendering — Implementation Plan

## Context

Phase 1 (detector physics) is complete: the `smig/sensor/` package implements a star-topology detector chain (`H4RG10Detector` orchestrator + leaf modules for charge diffusion, IPC, readout, nonlinearity, persistence, noise). All sensor modules receive/return plain `np.ndarray` — GalSim is never imported in `smig/sensor/`.

Phase 2 builds the **upstream rendering pipeline** that generates the ideal electron-count images Phase 1 consumes. It introduces field-varying polychromatic PSFs (STPSF), finite-source rendering, crowded-field scene composition, and corrected difference image analysis (DIA). These modules live in new packages (`smig/optics/`, `smig/rendering/`) and **do** use GalSim.

The work is divided into **7 sequential prompts**, each self-contained enough for a single coding session, with clear deliverables and acceptance criteria.

---

## Dependency Graph

```
Prompt 1  (Infrastructure + pyproject.toml)
    │
    v
Prompt 2  (Config schemas + seed derivation)
    │          Prompt 2 → 3 dependency: PSFConfig only
    v
Prompt 3  (PSF provider)
    │
    v
Prompt 4  (FiniteSourceRenderer + CrowdedFieldRenderer)
    │
    v
Prompt 5  (DIA pipeline — MVP kernel matching)
    │
    v
Prompt 6  (Provenance extension + end-to-end pipeline orchestrator)
    │
    v
Prompt 7  (Validation suite + data leakage contract)
```
All prompts are strictly sequential. No parallel branches.

---

## Prompt 1: Project Infrastructure & Package Skeleton

### Scope
Create `pyproject.toml` (the project has none), declare all dependencies, and set up the directory skeleton for `smig/optics/` and `smig/rendering/`.

### Files to create
- `pyproject.toml` — build system config, package `smig` v2.0.0a1
- `smig/optics/__init__.py` — docstring-only package init
- `smig/rendering/__init__.py` — docstring-only package init

### Files to verify exist
- `smig/__init__.py` — already exists (empty). Confirm it is present so `import smig` works with normal packaging. If missing, create it.

### Files to modify
- `.gitignore` — add `.eggs/`, `dist/`, `*.egg-info/`, `build/`

### Key decisions
- **Base runtime deps** (always installed): `numpy`, `scipy`, `pydantic>=2.0`, `pyyaml`, `h5py`
- **Phase 2 optional extra** `[phase2]`: `galsim`, `webbpsf` (this is the actual PyPI package name — STScI added Roman WFI support into the existing `webbpsf` library; there is no separate `stpsf` package on PyPI), `synphot`, `poppy`, `pandas`, `astropy`
- **Dev extra** `[dev]`: `pytest`
- `pip install -e .` installs base only (Phase 1 CI stays fast). `pip install -e ".[phase2]"` adds GalSim/WebbPSF. `pip install -e ".[phase2,dev]"` adds both.
- Do NOT create `requirements.txt` — `pyproject.toml` only
- In code, guard Phase 2 imports with `try: import webbpsf` / `try: import galsim` and raise clear errors when missing

### Acceptance criteria
1. `pip install -e .` succeeds (base deps only)
2. `python -c "import smig; import smig.optics; import smig.rendering"` works
3. `python -m pytest smig/sensor/validation/ -v` still passes (no regressions)
4. `pip install -e ".[phase2]"` installs GalSim + WebbPSF (may skip in CI if data files unavailable)

---

## Prompt 2: Phase 2 Configuration Schemas & Reproducibility Seed Derivation

### Scope
Define frozen Pydantic v2 config models for all Phase 2 modules. Implement the deterministic hierarchical seed derivation contract from the spec. No physics — only data structures and utilities.

### Files to create
- `smig/config/optics_schemas.py` — `PSFConfig`, `RenderingConfig`, `CrowdedFieldConfig`, `DIAConfig`, `SimulationConfig`
- `smig/config/seed.py` — `derive_event_seed()`, `derive_stage_seed()`
- `smig/config/simulation.yaml` — **single self-contained YAML file** that embeds a full `detector:` block (copy values from `roman_wfi.yaml`) plus new `psf:`, `rendering:`, `crowded_field:`, `dia:` sections. No YAML cross-file references — one file, one `SimulationConfig`.
- `smig/config/validation/test_seed.py` — seed derivation and config round-trip tests

### Files to modify
- `smig/config/utils.py` — add `load_simulation_config(path) -> SimulationConfig` and `get_simulation_config_sha256(config: SimulationConfig) -> str` (uses same `model_dump_json` + SHA-256 pattern as `get_config_sha256`)

### Critical architectural decision
**Do NOT modify `DetectorConfig`**. It is the sensor-only config; changing its structure would break the SHA-256 canary hash in `test_config_utils.py`. Instead, create a new `SimulationConfig` that composes:
```python
class SimulationConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    detector: DetectorConfig = Field(default_factory=DetectorConfig)
    psf: PSFConfig = Field(default_factory=PSFConfig)
    rendering: RenderingConfig = Field(default_factory=RenderingConfig)
    crowded_field: CrowdedFieldConfig = Field(default_factory=CrowdedFieldConfig)
    dia: DIAConfig = Field(default_factory=DIAConfig)
```

**Geometry default warning**: `DetectorConfig` defaults to `nx=ny=4096`. Phase 2 stamp-based runs use smaller geometries (256x256 for DIA context, 64x64 for science output). The `simulation.yaml` file MUST override detector geometry to match the context stamp size: `detector.geometry.nx: 256`, `detector.geometry.ny: 256`. A `model_validator` on `SimulationConfig` should check that `detector.geometry.nx >= dia.context_stamp_size` and `detector.geometry.ny >= dia.context_stamp_size`.

### Config fields (from spec)
- **PSFConfig**: `filter_name='W146'`, `oversample=4`, `n_wavelengths=10`, `jitter_rms_mas=5.0`, `cache_dir: str | None = None`, `wavelength_range_um=(0.93, 2.00)`
- **CrowdedFieldConfig**: `stamp_size=64`, `pixel_scale_arcsec=0.11`, `brightness_cap_mag: float | None = None`, `neighbor_mag_limit=26.0`
- **DIAConfig**: `n_reference_epochs=30`, `context_stamp_size=256`, `science_stamp_size=64`, `subtraction_method: Literal['alard_lupton', 'sfft'] = 'alard_lupton'`

### Seed derivation
- Use `hashlib.sha256` (NOT Python's `hash()` which varies with `PYTHONHASHSEED`)
- **Domain separation** to prevent accidental collisions:
  - `derive_event_seed(master_seed: int, event_id: str, namespace: str = "smig/v2/event") -> int`
  - `derive_stage_seed(event_seed: int, stage_name: str, namespace: str = "smig/v2/stage") -> int`
- **Truncate to 32-bit positive integer** (`% (2**31 - 1)`) to guarantee compatibility with GalSim's `galsim.BaseDeviate(seed)` C++ bindings which are strict about integer sizes
- Contract: same inputs always produce same seed; different inputs produce different seeds

### Acceptance criteria
1. All new models use `ConfigDict(frozen=True, extra="forbid")`
2. `simulation.yaml` loads cleanly: `load_simulation_config()` -> `model_validate` -> `model_dump_json` -> hash is stable
3. Seed determinism and independence tests pass
4. Seed output is always a positive 32-bit int (`0 < seed < 2**31`)
5. `SimulationConfig` validator rejects geometry smaller than `dia.context_stamp_size`
6. Existing Phase 1 tests unaffected (DetectorConfig canary hash unchanged)

---

## Prompt 3: STPSFProvider — Field-Varying Polychromatic PSF

### Scope
Implement the PSF provider that computes wavelength-dependent, field-position-varying PSFs via WebbPSF (which includes Roman WFI support). This is the heaviest single module in Phase 2.

### Files to create
- `smig/optics/psf.py` — `STPSFProvider` class
- `smig/optics/validation/test_psf.py` — unit tests

### Files to modify
- `smig/optics/__init__.py` — export `STPSFProvider`

### Class design (from spec)
```python
class STPSFProvider:
    def __init__(self, config: PSFConfig): ...
    def get_psf(self, sca_id, field_position, source_sed='flat',
                jitter_seed: int | None = None) -> galsim.InterpolatedImage: ...
    def get_psf_at_wavelength(self, sca_id, field_position, wavelength_um) -> np.ndarray: ...
```
The `jitter_seed` parameter allows different jitter realizations per epoch (needed by DIA reference construction in Prompt 5). When `None`, uses the config default jitter; when set, produces a deterministic but distinct jitter realization.

### Key design decisions
- **Import name**: Use `import webbpsf` (the actual PyPI package). The class name references "STPSF" per the spec nomenclature but the implementation uses the `webbpsf` library.
- **Fallback mode**: WebbPSF requires large data files (~300 MB). Use `try: import webbpsf` with a fallback to an **analytic Airy+Gaussian PSF** when unavailable. **The fallback must also vary with field position** (e.g., scale FWHM by a smooth polynomial across the field) and wavelength (FWHM scales as lambda/D) so that tests exercising variation are meaningful in both modes. Document which mode is active via a `._backend` attribute (`'webbpsf'` or `'analytic'`).
- **Lazy computation**: PSF grid precomputed on first access, NOT at `__init__` time (avoids 10-min startup)
- **Disk cache key**: Use a **deterministic SHA-256 hash** of `(sca_id, quantized_field_position, wavelength_um, oversample, jitter_rms_mas, filter_name, config_hash, backend_mode)` as the cache key — NOT float-formatted HDF5 path names. Quantize field positions to 4 decimal places to prevent float formatting instability from exploding cache cardinality. Store the hash as the HDF5 dataset name, with metadata attributes recording the human-readable parameters.
- **Polychromatic assembly**: `PSF_poly = sum(w_i * PSF_mono_i)` where `w_i = SED(lambda_i) * throughput(lambda_i) * QE(lambda_i) * d_lambda`, weights normalized to 1. Throughput/QE curves must come from versioned data (WebbPSF built-in filter curves or a bundled HDF5 file) — not hardcoded.
- **PSF normalization convention**: Sum over pixels = 1.0 (total flux normalization). Document this explicitly and test it.
- **Wavelength grid**: Log-spaced (PSF changes faster at shorter wavelengths)
- **Initial SED support**: `'flat'` only; extensible to blackbody/template later
- **Jitter**: Convolved as Gaussian kernel, 5 mas/axis per config

### Acceptance criteria
1. Constructs without error from `PSFConfig` defaults (in either backend mode)
2. Monochromatic PSF normalized: sum over pixels = 1.0 (±10^-6)
3. `get_psf()` returns `galsim.InterpolatedImage`
4. PSF varies with wavelength (FWHM differs at 0.93 vs 2.0 um) — **in both webbpsf and analytic fallback modes**
5. PSF varies with field position — **in both modes**
6. Jitter convolution increases FWHM
7. Disk cache works: second call with same params loads from cache (faster); altered config hash invalidates cache
8. Single PSF computation < 500 MB memory (test on small grid: 2 wavelengths, 1 field position)
9. WebbPSF-dependent tests marked `@pytest.mark.skipif(not _WEBBPSF_AVAILABLE)`

---

## Prompt 4: FiniteSourceRenderer & CrowdedFieldRenderer

### Scope
Implement source rendering (point source vs finite limb-darkened disk) and crowded-field scene composition using GalSim.

### Files to create
- `smig/rendering/source.py` — `FiniteSourceRenderer`
- `smig/rendering/crowding.py` — `CrowdedFieldRenderer`
- `smig/rendering/validation/test_source.py`
- `smig/rendering/validation/test_crowding.py`

### FiniteSourceRenderer (from spec)
```python
class FiniteSourceRenderer:
    UNRESOLVED_THRESHOLD_ARCSEC = 0.33  # ~3 Roman pixels
    def __init__(self, psf_provider: STPSFProvider): ...
    def render_source(self, flux_e, centroid_offset_pix, rho_star_arcsec,
                      limb_darkening_coeffs, psf, stamp) -> None: ...
```
- Unresolved regime (rho* < 0.33"): `galsim.DeltaFunction(flux)` — correct for >99.9% of events
- Resolved regime (rho* > 0.33"): limb-darkened disk profile via GalSim
- Centroid offset applied via GalSim `shift()`, NOT integer pixel shifts
- **Stamp ownership**: The caller allocates a `galsim.Image` stamp buffer and passes it to `render_source()`, which draws into it in-place. Document the GalSim coordinate convention used (image center vs pixel indices). The method returns `None`; flux is added to the existing stamp contents.

### CrowdedFieldRenderer (from spec)
```python
class CrowdedFieldRenderer:
    def __init__(self, neighbor_catalog: pd.DataFrame, psf_provider, stamp_size=64,
                 pixel_scale=0.11, brightness_cap_mag=None): ...
    def render_static_field(self, psf) -> np.ndarray: ...
```
- Neighbor catalog: DataFrame with required columns `[x_pix, y_pix, flux_e, mag_w146]`, validated at init (columns present, no NaN in coordinates, float dtypes for positions, magnitudes in [0, 40] range)
- **Catalog provenance**: For Phase 2 tests, use synthetic uniform-random neighbors. File-based catalogs from Galaxia/SPISEA are a Phase 3 deliverable. Document this in a docstring.
- `render_static_field()` result cached (computed once per event)
- **Must NOT import any `smig/sensor/` module** — returns `np.ndarray` of ideal electrons
- 200-star stamp renders in < 2 seconds on CPU (machine-dependent; use `@pytest.mark.slow` and generous CI margin)

### Acceptance criteria
1. Point source: flux concentrated at centroid, total flux conserved within 0.1%
2. Finite disk: extended emission visible, flux conserved within 0.1%
3. Crowded field: correct stamp shape `(stamp_size, stamp_size)`
4. Edge neighbors contribute PSF wings correctly
5. Static field cached on second call
6. **Forbidden imports check**: `grep -r "from smig.sensor" smig/rendering/` returns zero matches. `grep -r "import smig.sensor" smig/rendering/` returns zero matches. Add this as an automated test.

---

## Prompt 5: Corrected DIA Pipeline (MVP Scope)

### Scope
Implement realistic reference image construction (multi-epoch, variable-PSF coadd) and **MVP** Alard-Lupton subtraction. Extracts the central 64x64 science stamp from the 256x256 context stamp. Scope is deliberately narrow to reduce schedule risk — full polynomial basis expansion is a future enhancement.

### Files to create
- `smig/rendering/dia.py` — `DIAPipeline` class
- `smig/rendering/validation/test_dia.py`

### Class design (from spec)
```python
class DIAPipeline:
    def __init__(self, config: DIAConfig, detector_config: DetectorConfig): ...
    def build_reference(self, epochs, psfs, backgrounds) -> np.ndarray:  # (256, 256)
        """Inverse-variance weighted coadd of n_reference_epochs baseline epochs."""
    def subtract(self, science_image, reference_image) -> np.ndarray:  # (256, 256)
        """Alard-Lupton fixed-kernel convolution matching (MVP)."""
    def extract_stamp(self, difference_image) -> np.ndarray:  # (64, 64)
        """Central crop: diff_image[96:160, 96:160]."""
```

### Key design decisions
- **MVP Alard-Lupton**: Start with **2-3 fixed Gaussian basis functions, no polynomial spatial variation, no spatial kernel interpolation**. Fixed kernel size, single stamp, least-squares solve. This is the minimum viable implementation that produces valid difference images. Full AL basis expansion (higher-order polynomials, spatially varying kernels, regularization) is a later enhancement. Document the MVP limitations.
- **No external DIA dependencies**: Implement from scratch for reproducibility. Do NOT pull in `hotpants`, `sfft`, or `properimage` as runtime deps.
- **Detector config access**: `DIAPipeline.__init__` takes `detector_config: DetectorConfig` to access `read_noise_e_effective`, `dark_current_e_per_s`, and `exposure_time_s` for accurate Gaussian noise injection in the reference.
- **DIA input/output representation**: Both science and reference images are in **detector output rate space** (e-/s), matching the output of `H4RG10Detector.process_epoch().rate_image`. The reference is a pragmatic approximation: ideal electrons converted to rate + Gaussian noise matching the expected detector noise floor. Document this as a known mixed-fidelity simplification.
- **Reference construction**: `n_reference_epochs` (default 30) baseline frames, each with a different PSF jitter realization (via `STPSFProvider.get_psf(jitter_seed=...)`) and sky background level. Inverse-variance weighted coadd where weights come from `sqrt(read_noise^2 + dark_current * t_exp + sky_background * t_exp)`.
- **SFFT**: Stubbed with `NotImplementedError` — reserved for validation subset per spec
- **Crop**: Centered at `[96:160, 96:160]` (for default 256->64)
- **No masking / bad pixels**: MVP assumes clean stamps. Masking is a later enhancement.

### Acceptance criteria
1. Reference is 2D `(context_stamp_size, context_stamp_size)` from `n_reference_epochs` frames
2. Injected point source recovered in difference image within 10% flux accuracy (relaxed from 5% for MVP — tighten after full AL)
3. Static-field difference has residuals consistent with noise (mean < 1 sigma of expected noise, RMS within 2x expected)
4. SFFT raises `NotImplementedError`
5. `science_stamp_size` x `science_stamp_size` crop correctly extracted from context stamp
6. Noise injection uses actual detector config parameters (not hardcoded values)

---

## Prompt 6: Provenance Extension & End-to-End Pipeline Orchestrator

### Scope
Create the top-level `SceneSimulator` orchestrator that wires: STPSFProvider -> CrowdedFieldRenderer -> FiniteSourceRenderer -> H4RG10Detector -> DIAPipeline. Extend provenance for Phase 2 metadata. Implement seed derivation in the pipeline flow.

### Files to create
- `smig/rendering/pipeline.py` — `SceneSimulator` orchestrator
- `smig/rendering/validation/test_pipeline.py` — integration tests

### Files to modify
- `smig/provenance/schema.py` — add Phase 2 optional fields with defaults (follows existing pattern at lines 256-325):
  - `psf_config_hash: str | None = Field(default=None, ...)`
  - `n_neighbors_rendered: int = Field(default=0, ...)`
  - `dia_method: str | None = Field(default=None, ...)`
  - `reference_n_epochs: int = Field(default=0, ...)`

### SceneSimulator design
```python
class SceneSimulator:
    """Phase 2 top-level orchestrator. Wraps H4RG10Detector, does NOT replace it."""
    def __init__(self, config: SimulationConfig, master_seed: int): ...
    def simulate_event(self, event_id, source_params_sequence, timestamps_mjd, ...) -> EventSceneOutput: ...
```
**No public `simulate_epoch` method.** The orchestrator builds the complete `ideal_cube_e` (3D array: n_epochs x ny x nx) by rendering all epochs, then passes the entire cube to `H4RG10Detector.process_event(event_id, ideal_cube_e, timestamps_mjd)`. This preserves Phase 1's memory management contract — `process_event()` handles aggressive GC of intermediate ramp arrays internally.

### Data flow
```
SceneSimulator.simulate_event(event_id, source_params_seq, timestamps_mjd)
  1. Build DIA reference (lazily, cached for event duration):
     -> STPSFProvider.get_psf(jitter_seed=per_ref_epoch_seed)  x n_reference_epochs
     -> CrowdedFieldRenderer.render_static_field()
     -> DIAPipeline.build_reference()
  2. For each epoch i, render ideal_cube_e[i]:
     -> STPSFProvider.get_psf(jitter_seed=per_epoch_seed)
     -> CrowdedFieldRenderer.render_static_field()  (cached)
     -> FiniteSourceRenderer.render_source(source_params_seq[i])
     -> ideal_cube_e[i] = static_field + source_image
  3. Pass full cube to detector:
     -> H4RG10Detector.process_event(event_id, ideal_cube_e, timestamps_mjd)
     -> returns EventOutput with rate_cube, masks, provenance
  4. For each epoch, run DIA:
     -> DIAPipeline.subtract(rate_cube[i], reference)
     -> DIAPipeline.extract_stamp()  -> science_stamp (64x64)
  5. Assemble final output with DIA cubes + provenance
```

### Key design decisions
- **Memory contract preserved**: `SceneSimulator` builds `ideal_cube_e` then delegates to `H4RG10Detector.process_event()` which handles GC. SceneSimulator does NOT call `process_epoch()` in its own loop.
- **Geometry = context stamp size**: Detector config geometry is set to `(context_stamp_size, context_stamp_size)` = `(256, 256)` by default. The full rendering + detector chain operates at 256x256. DIA subtraction happens at 256x256, then `extract_stamp()` crops to 64x64 for the final training output.
- Rendering modules produce `np.ndarray` -> detector chain consumes it (GalSim boundary enforced)
- New provenance fields are **optional with defaults** so existing Phase 1 tests remain unbroken
- **Provenance hashing**: `get_config_sha256()` stays detector-only. Add `get_simulation_config_sha256()` for full config. `psf_config_hash` in provenance uses the same `model_dump_json` + SHA-256 pattern applied to `PSFConfig`.

### RNG wiring table (explicit seed-to-consumer mapping)
```
derive_event_seed(master_seed, event_id)
  ├── derive_stage_seed(event_seed, "detector")     -> np.random.default_rng() -> H4RG10Detector(rng=...)
  │                                                     (detector spawns its own child RNGs internally)
  ├── derive_stage_seed(event_seed, "crowding")      -> np.random.default_rng() -> CrowdedFieldRenderer
  ├── derive_stage_seed(event_seed, "psf_jitter")    -> used to derive per-epoch jitter seeds:
  │                                                     jitter_seed_i = hash(psf_jitter_seed, epoch_index)
  ├── derive_stage_seed(event_seed, "dia_reference")  -> np.random.default_rng() -> reference noise injection
  └── derive_stage_seed(event_seed, "dia_jitter")    -> per-reference-epoch jitter seeds
```
This ensures: (a) detector gets one seed passed to `H4RG10Detector(rng=...)` with internal spawn unchanged, (b) no double-seeding, (c) adding a new stage does not change existing stage seeds (positional stability via name-based derivation).

### Acceptance criteria
1. Full pipeline runs: PSF -> crowding -> source -> detector (via `process_event`) -> DIA -> 64x64 output
2. Provenance records include new Phase 2 fields
3. Seed derivation produces deterministic outputs; same `(master_seed, event_id)` = same output
4. Existing Phase 1 tests still pass
5. Smoke test: 3 epochs, small stamp (e.g., 32x32 context with 16x16 science crop)
6. **Memory**: `simulate_event` does NOT hold both `ideal_cube_e` and detector intermediates simultaneously — `del ideal_cube_e` after passing to detector

---

## Prompt 7: Comprehensive Validation Suite & Data Leakage Contract

### Scope
Write physics validation tests, performance benchmarks, reproducibility regression tests, and the data leakage prevention script stub from the spec.

### Files to create
- `smig/rendering/validation/test_integration_phase2.py` — end-to-end Phase 2 integration tests (NOT in sensor/validation/)
- `scripts/validate_splits.py` — data leakage prevention script (stub per spec Section C)

### Files to modify
- None in `smig/sensor/validation/` — Phase 2 smoke tests belong in `smig/rendering/validation/`, not in the sensor test suite. Keep sensor tests detector-focused.

### Acceptance criteria
1. **PSF physics**: monochromatic FWHM increases with wavelength (diffraction limit ~ lambda/D)
2. **Flux conservation**: total flux through rendering chain (before detector) conserved within 0.1%. Total flux through rendering + detector conserved within 5% (detector applies NL, noise, IPC — strict conservation is not physical). Define "flux" as sum of `ideal_image_e` before detector vs aperture-photometry flux of the source in `rate_image * exposure_time`.
3. **DIA null test**: static-field difference residual mean < 1 sigma of expected noise; RMS within 2x expected noise level
4. **DIA recovery**: injected point source recovered within 10% (MVP AL tolerance)
5. **Seed determinism**: two runs with same `(master_seed, event_id)` produce outputs matching within `np.allclose(rtol=0, atol=0)` for integer masks (bit-identical) and `np.allclose(rtol=1e-12, atol=1e-12)` for float arrays. Pure-Python + fixed-seed paths only. Do NOT claim bit-identical across BLAS/FFT library versions.
6. **Seed independence**: different `event_id` values produce statistically different outputs (Kolmogorov-Smirnov p-value < 0.01 on pixel distributions)
7. **Memory**: full pipeline on 32x32 context stamp, 3 epochs, stays under 1 GB (scaled test)
8. **Forbidden imports**: automated test that `grep -r "from smig.sensor" smig/rendering/` and `grep -r "import galsim" smig/sensor/` both return zero matches
9. **Leakage guard stub**: `validate_splits.py` accepts a path to a **JSON manifest** with schema: `{"events": [{"event_id": str, "split": "train"|"val"|"test", "starfield_seed": int, "params": {"t_E": float, "u_0": float, "s": float, "q": float}}]}`. Checks: (a) no `event_id` appears in multiple splits, (b) no `starfield_seed` shared across splits, (c) events with all params within 5% of each other are in the same split. Returns exit code 0 on pass, 1 on fail. Full implementation deferred to Phase 4.
10. All Phase 1 tests still pass (`python -m pytest smig/sensor/validation/ -v`)
11. WebbPSF-dependent tests marked `@pytest.mark.skipif(not _WEBBPSF_AVAILABLE)`

---

## Files Summary

| Prompt | New Files | Modified Files |
|--------|-----------|----------------|
| 1 | `pyproject.toml`, `smig/optics/__init__.py`, `smig/rendering/__init__.py` | `.gitignore` |
| 2 | `smig/config/optics_schemas.py`, `smig/config/seed.py`, `smig/config/simulation.yaml`, `smig/config/validation/test_seed.py` | `smig/config/utils.py` |
| 3 | `smig/optics/psf.py`, `smig/optics/validation/test_psf.py` | `smig/optics/__init__.py` |
| 4 | `smig/rendering/source.py`, `smig/rendering/crowding.py`, tests | `smig/rendering/__init__.py` |
| 5 | `smig/rendering/dia.py`, `smig/rendering/validation/test_dia.py` | — |
| 6 | `smig/rendering/pipeline.py`, `smig/rendering/validation/test_pipeline.py` | `smig/provenance/schema.py` |
| 7 | `smig/rendering/validation/test_integration_phase2.py`, `scripts/validate_splits.py` | — (no sensor/ modifications) |

## Critical Existing Files (Do Not Break)
- `smig/config/schemas.py` — `DetectorConfig` is sensor-only; do NOT modify its structure
- `smig/sensor/detector.py` — `H4RG10Detector` is wrapped, not replaced; `process_event()` is the sole entry point for multi-epoch processing (preserves GC contract)
- `smig/provenance/schema.py` — extend with optional fields only (lines 256-325 show the pattern)
- `smig/sensor/validation/test_config_utils.py` — contains SHA-256 canary hash for `DetectorConfig`

## Verification
After all prompts are complete, run:
```bash
# Phase 1 regression (must pass unchanged)
python -m pytest smig/sensor/validation/ -v

# Phase 2 unit tests
python -m pytest smig/optics/validation/ -v
python -m pytest smig/rendering/validation/ -v
python -m pytest smig/config/validation/ -v

# Config round-trip
python -c "
import yaml; from pathlib import Path
from smig.config.optics_schemas import SimulationConfig
cfg = SimulationConfig.model_validate(yaml.safe_load(Path('smig/config/simulation.yaml').read_text()))
print(cfg.model_dump_json(indent=2))
"

# Seed determinism + 32-bit bounds
python -c "
from smig.config.seed import derive_event_seed, derive_stage_seed
s1 = derive_event_seed(42, 'ob230001')
s2 = derive_event_seed(42, 'ob230001')
assert s1 == s2, 'Seed derivation is not deterministic'
assert 0 < s1 < 2**31, f'Seed out of GalSim-safe range: {s1}'
print(f'OK: seed={s1}')
"

# Forbidden imports
python -c "
import subprocess, sys
r1 = subprocess.run(['grep', '-r', 'import galsim', 'smig/sensor/'], capture_output=True, text=True)
r2 = subprocess.run(['grep', '-r', 'from smig.sensor', 'smig/rendering/'], capture_output=True, text=True)
assert not r1.stdout, f'GalSim imported in sensor/: {r1.stdout}'
assert not r2.stdout, f'sensor imported in rendering/: {r2.stdout}'
print('OK: no forbidden imports')
"

# Full pipeline smoke test
python -m pytest smig/rendering/validation/test_pipeline.py -v

# Data leakage stub
python scripts/validate_splits.py --help
```

---

## Reviewer Feedback Changelog (v1 → v2)

| # | Issue | Severity | Fix Applied |
|---|-------|----------|-------------|
| 1 | `SceneSimulator` calling `process_epoch()` in a loop bypasses Phase 1 GC contract | Critical | Prompt 6: `simulate_event()` builds full `ideal_cube_e` then passes to `process_event()` |
| 2 | PyPI package is `webbpsf`, not `stpsf` | High | Prompts 1, 3: use `webbpsf` everywhere |
| 3 | GalSim `BaseDeviate` requires 32-bit seed | High | Prompt 2: truncate to `% (2**31 - 1)` |
| 4 | `simulation.yaml` "references" `roman_wfi.yaml` undefined | High | Prompt 2: single self-contained YAML file with embedded detector block |
| 5 | PSF cache key with float-formatted paths is fragile | High | Prompt 3: deterministic SHA-256 hash of quantized params |
| 6 | Analytic PSF fallback must also vary with field/wavelength | High | Prompt 3: fallback scales FWHM by polynomial (field) and lambda/D (wavelength) |
| 7 | DIA "Alard-Lupton from scratch" too large for one prompt | High | Prompt 5: narrowed to MVP (2-3 Gaussians, no spatial variation) |
| 8 | DIA needs detector config for noise injection | High | Prompt 5: `DIAPipeline.__init__` takes `detector_config` |
| 9 | Geometry mismatch: 64x64 vs 256x256 for DIA | High | Prompt 6: detector runs at 256x256 (context size), DIA crops to 64x64 |
| 10 | `SimulationConfig` defaults to 4096x4096 geometry | Medium | Prompt 2: `simulation.yaml` overrides to 256x256; validator checks geometry >= context_stamp_size |
| 11 | Seed derivation needs namespace versioning | Medium | Prompt 2: added `namespace` parameter with domain separation |
| 12 | RNG wiring underspecified | Medium | Prompt 6: explicit seed-to-consumer table |
| 13 | "Bit-identical" unrealistic for floats across BLAS/FFT | Medium | Prompt 7: `np.allclose` for floats, bit-identical only for integer masks |
| 14 | Phase 2 smoke tests mixed into sensor/ validation | Low | Prompt 7: all Phase 2 tests in `rendering/validation/`, not `sensor/validation/` |
| 15 | Provenance hashing conventions unclear | Medium | Prompt 6: `get_simulation_config_sha256()` added, PSF hash uses same pattern |
| 16 | No forbidden imports check | Medium | Prompts 4, 7: automated grep tests for GalSim-in-sensor and sensor-in-rendering |
| 17 | `validate_splits.py` input format unspecified | Low | Prompt 7: JSON manifest schema defined |
| 18 | `render_source` stamp ownership ambiguous | Low | Prompt 4: caller allocates stamp, method draws in-place, returns None |
| 19 | Neighbor catalog provenance missing | Low | Prompt 4: synthetic for tests, file-based in Phase 3 |
| 20 | DIA input/output representation unclear | Medium | Prompt 5: both in rate space (e-/s), matching detector output |
| 21 | Heavy deps break base `pip install -e .` | Medium | Prompt 1: split into `[phase2]` optional extra |
