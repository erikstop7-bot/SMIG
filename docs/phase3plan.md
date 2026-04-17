# SMIG v2 — Phase 3 Prompt Pack

**Target executor:** Claude Code (Sonnet 4.6 default; Opus 4.7 in plan mode flagged per prompt).
**Assumption:** Phases 1 and 2 are locked. Detector physics and optics/DIA are untouchable foundations.

## Phase Map

| # | Phase | Deliverable | Model |
|---|---|---|---|
| 3.1 | Catalog ingestion + projection + crowding adapter | `smig/catalogs/*` + DataFrame adapter matching `crowding.py` | Sonnet 4.6 |
| 3.2 | Microlensing physics engine | PSPL / FSPL / 2L1S with pinned VBBL, interface freeze | **Opus 4.7 plan → Sonnet 4.6 impl** |
| 3.3 | Event-source binding adapter | `bind_event_to_source` + null/peak gates | Sonnet 4.6 |
| 3.4 | Dataset contract | `LabelVector`, splits, flat HDF5 layout, JSON manifest | Sonnet 4.6 |
| 3.5 | Orchestrator + atomic writer + checkpointing | `DatasetBuilder`, process pool, resumable | **Opus 4.7 plan → Sonnet 4.6 impl** |
| 3.6 | Validation + scientific regression + golden event | Risk-register gates + PNG report | Sonnet 4.6 |

## Global Rules (apply to every prompt)

These apply to all six prompts. The agent should internalize them once.

1. **Repo test layout:** existing tests live at `smig/<pkg>/validation/test_*.py` and `scripts/test_*.py`. Phase 3 tests MUST follow the same convention (e.g., `smig/catalogs/validation/test_adapter.py`). Run the full suite with `pytest -v`.
2. **Baseline regression:** before starting each phase, run `pytest -v` and record the pass count. After the phase, `pytest -v` must show `baseline_count + new_phase_tests` passing with **zero prior failures**. Do not assume a specific integer.
3. **Dependency policy:** no new runtime dependencies without explicit approval. Stdlib only for hashing (`hashlib.sha256`), immutable mappings (`types.MappingProxyType`), and memory profiling (`tracemalloc`). `astropy` is already under `[project.optional-dependencies].phase2`; Phase 3 catalog/orchestrator tests assume `pip install -e '.[phase2]'` in CI.
4. **Frozen upstream:** `smig/rendering/*`, `smig/optics/*`, `smig/detector/*`, `smig/config/seed.py`, `smig/provenance/schema.py` are frozen unless the prompt says otherwise. Phase 3.6 permits a single-line bugfix only with a justification note in the commit message.
5. **Seed utilities — use only what exists:** `derive_event_seed(master_seed, event_id)` and `derive_stage_seed(event_seed, stage_name)` in `smig/config/seed.py`. No invented `ns=...` namespaces, no worker seeds.
6. **Interface freezes:** every dataclass emitted by a phase that downstream phases depend on (`StarRecord`, `MicrolensingEvent`, `LabelVector`, `DatasetManifest`) MUST be declared `@dataclass(frozen=True)`. Mutations raise `FrozenInstanceError`. Default `Mapping` fields use `field(default_factory=lambda: MappingProxyType({}))`.
7. **Shell acceptance command hygiene:** `grep` checks that should return empty must be wrapped with `|| true` to avoid `set -e` script failures. Use `test -f <path>` for file existence, `pytest` for tests, `python -c` for import smokes.
8. **Output artifacts:** generated artifacts (PNGs, HDF5 shards, manifests) go to `outputs/` and `datasets/`. Both directories are gitignored. Only committed code, fixtures under `smig/*/validation/fixtures/`, and docs enter version control.
9. **Docs allowed:** prompts may create `docs/phase3_*.md` files. These are part of the deliverable, not scope creep.
10. **Scope exclusions (all phases):** no lens orbital motion, no xallarap, no 2L2S / binary sources, no astrometric microlensing centroid shifts, no non-zero annual parallax in smoke configs, no ML training, no live Roman cadence modeling. Parallax fields exist on the dataclass but default to 0. Single-band F146 for Phase 3.
11. **Stop-and-ask triggers:** adding any new dependency, deleting any existing file, modifying any frozen module, changing CI configuration, modifying `scripts/validate_splits.py`.

---

## Prompt 1 of 6 — Phase 3.1: Catalog Ingestion + Projection + Crowding Adapter

**Model: Claude Code Sonnet 4.6 (standard).**

### Role & Context
You are a senior astrophysics software engineer expert in Galactic population synthesis, WCS projections, and Roman Space Telescope photometric systems. You are executing **Phase 3.1 of 6** in the SMIG v2 build.

**Where we are:** Phases 1 and 2 are locked. `smig/rendering/crowding.py` defines `CrowdedFieldRenderer`, which validates its input as a `pandas.DataFrame` with exactly the columns `x_pix, y_pix, flux_e, mag_w146` (inspect the `_REQUIRED_COLUMNS` constant in that file before implementing). `smig/rendering/pipeline.py` contains a private `_generate_catalog` method that currently feeds synthetic stars into the simulator. **Neither file will be modified in this phase.**

**What this phase delivers:** A `CatalogProvider` abstraction plus Besançon and Roman core-bulge ingestors, an AB-system photometric converter (F146 primary), a Galactic → SCA-pixel projector, and an adapter that emits a **pandas DataFrame** with exactly the columns `CrowdedFieldRenderer` already validates. Phase 3.1 does NOT wire real catalogs into `SceneSimulator` — that integration happens in the Phase 3.5 worker. `_generate_catalog` inside `pipeline.py` remains the code path exercised by existing Phase 2 tests.

**What comes next:** Phase 3.2 consumes `StarRecord.mass_msun`, `teff_K`, `log_g`, `metallicity_feh` to derive microlensing source radii and Claret 2000 limb-darkening coefficients.

### Target Files

**IN SCOPE:**
- `smig/catalogs/__init__.py`
- `smig/catalogs/base.py` — abstract `CatalogProvider` + frozen `StarRecord`
- `smig/catalogs/besancon.py` — Besançon web-query ingestor (CSV/FITS)
- `smig/catalogs/roman_bulge.py` — Penny et al. 2019 catalog ingestor
- `smig/catalogs/photometry.py` — AB magnitude → total electrons over exposure
- `smig/catalogs/wcs.py` — Galactic → ICRS → SCA-pixel projection
- `smig/catalogs/adapter.py` — `ProjectedStarTable` emitter: pandas.DataFrame with columns matching `CrowdedFieldRenderer`
- `smig/catalogs/synthetic.py` — NEW `SyntheticCatalogProvider` (does NOT replace `_generate_catalog` in `pipeline.py` — that stays untouched)
- `smig/catalogs/sampler.py` — `sample_field(provider, l, b, fov, rng)` orchestrator + on-disk cache
- `smig/catalogs/__main__.py` — CLI entry for `python -m smig.catalogs.sampler` smoke invocation
- `smig/catalogs/validation/__init__.py`
- `smig/catalogs/validation/test_base.py`, `test_photometry.py`, `test_wcs.py`, `test_besancon.py`, `test_adapter.py`, `test_synthetic_provider.py`
- `smig/catalogs/validation/fixtures/besancon_smoke.csv` — small committed fixture
- `smig/catalogs/validation/fixtures/roman_bulge_smoke.fits` — small committed fixture
- `data/catalogs/bandpasses/roman_F146.csv` — committed Roman F146 throughput
- `docs/phase3_photometry_reference.md` — committed zero-point reference: pinned value, retrieval date, URL, STScI version

**OUT OF SCOPE (DO NOT MODIFY):**
- `smig/rendering/*`, `smig/optics/*`, `smig/detector/*` — frozen
- `smig/config/seed.py`, `smig/provenance/schema.py` — frozen
- `scripts/validate_splits.py` — read-only reference

### Rules of Engagement
- Minimal diffs. No refactors, no linting sweeps, no style changes outside new files.
- `StarRecord` MUST be `@dataclass(frozen=True)`. `mag_other_ab: Mapping[str, float] = field(default_factory=lambda: MappingProxyType({}))`. No `frozendict`, no new packages.
- `CatalogProvider` is an ABC. Concrete providers validate their expected column schema on load and raise `MissingColumnError(list[str])` with the missing names.
- Adapter output MUST be a `pandas.DataFrame` with EXACTLY the columns `CrowdedFieldRenderer._REQUIRED_COLUMNS` — inspect `smig/rendering/crowding.py` to read that constant; do not hardcode a guess.
- Phase 3.1 is **single-band (F146)**. Multi-band is an optional future extension; `StarRecord.mag_other_ab` defaults to an empty frozen mapping, and `data/catalogs/bandpasses/` commits only `roman_F146.csv` now.
- `mag_w146` column in the adapter DataFrame stores the **F146 AB magnitude** (matching the Phase 2 renderer's column name). Document this equivalence prominently in `adapter.py` and `photometry.py` module docstrings.
- **Photometry contract:** `mag_ab_to_electrons(mag_ab: float, band: str, exposure_s: float) -> float` returns **total integrated electrons over the exposure**, matching Phase 2's `flux_e` semantics (the value that goes into `source_params_sequence` and into the `flux_e` column of the crowding DataFrame). Implementation internally computes e⁻/s from the throughput integral and multiplies by `exposure_s`. Document this explicitly in the docstring.
- **Zero-point discipline:** `docs/phase3_photometry_reference.md` MUST contain (a) the pinned F146 AB zero-point numeric value, (b) the retrieval date, (c) the source URL, (d) the STScI Roman bandpass version. `photometry.py` loads the zero point from this doc-adjacent source (NOT a hardcoded magic number). If the reference value ever changes, the doc changes and a regression test catches it.
- WCS uses `astropy.coordinates.SkyCoord` for Galactic→ICRS. The affine SCA projection MUST reuse the existing Phase 2 plate-scale constant — search the repo (grep `plate_scale|pixel_scale|arcsec.*pix`) before defining any new constant; do not redefine.
- Hashing: `hashlib.sha256(repr(key).encode())` for cache keys. **No `xxhash`, no new dependencies.**
- Synthetic provider migration: do NOT move `_generate_catalog` out of `pipeline.py`. Build `SyntheticCatalogProvider` in `smig/catalogs/synthetic.py` as a **new** class matching the `CatalogProvider` interface. It may duplicate logic; that duplication resolves when Phase 3.5 wires catalogs through the worker.
- **Stop and ask before:** adding any new dependency (including `xxhash`, `frozendict`, any compression plugin), modifying `pipeline.py` or any frozen module, deleting any file.

### Execution Tasks

Complete in order:

1. **Read first, then code.** Before writing anything, `grep` the repo for: `_REQUIRED_COLUMNS` in `smig/rendering/crowding.py`; `_generate_catalog` in `smig/rendering/pipeline.py`; `plate_scale` or equivalent plate-scale constant. Paste the `_REQUIRED_COLUMNS` value as a doc comment at the top of `adapter.py`.
2. **`base.py` — frozen `StarRecord`** with fields: `galactic_l_deg: float`, `galactic_b_deg: float`, `distance_kpc: float`, `mass_msun: float`, `teff_K: float`, `log_g: float`, `metallicity_feh: float`, `mag_F146_ab: float`, `mag_other_ab: Mapping[str, float] = field(default_factory=lambda: MappingProxyType({}))`, `source_id: str`, `catalog_tile_id: str`. Abstract `CatalogProvider` with `sample_field(l_deg, b_deg, fov_deg, rng: np.random.Generator) -> list[StarRecord]` and `list_bands() -> tuple[str, ...]`. Define `MissingColumnError(Exception)`.
3. **`photometry.py`** — `mag_ab_to_electrons(mag_ab, band, exposure_s) -> float`. Module docstring references `docs/phase3_photometry_reference.md` and states: "Returns TOTAL integrated electrons over the exposure window, matching Phase 2 `flux_e` semantics." Loads throughput from `data/catalogs/bandpasses/roman_{band}.csv`. Raises `ValueError` with a helpful message if a non-F146 band is requested before additional bandpass files are committed.
4. **`docs/phase3_photometry_reference.md`** — pin the F146 AB zero point with retrieval date, URL, STScI version identifier.
5. **`wcs.py`** — `galactic_to_sca_pixel(l_deg, b_deg, sca_id, field_center_l_deg, field_center_b_deg) -> tuple[float, float]`. Uses `astropy.coordinates.SkyCoord` for Galactic→ICRS and the repo's existing plate-scale constant for the SCA affine.
6. **`besancon.py`** — `BesanconProvider(catalog_path: Path)` supporting CSV and FITS output from the Besançon web-form query. Document the exact expected column schema in the module docstring. Validate on load.
7. **`roman_bulge.py`** — `RomanBulgeProvider(catalog_path: Path)` with Penny et al. 2019 FITS column schema.
8. **`synthetic.py`** — `SyntheticCatalogProvider` exposing the `CatalogProvider` interface. Duplicates logic from `_generate_catalog` if needed. Document in the class docstring: "Phase 3.1 does NOT wire real catalogs into SceneSimulator. Phase 2's `pipeline._generate_catalog` remains the active code path until Phase 3.5 worker integration."
9. **`adapter.py`** — `project_to_sca_dataframe(stars: list[StarRecord], sca_id: int, field_center_l_deg: float, field_center_b_deg: float, exposure_s: float) -> pd.DataFrame`. Returns a DataFrame with columns exactly matching `CrowdedFieldRenderer._REQUIRED_COLUMNS` and appropriate dtypes. The `flux_e` column holds total integrated electrons (from `mag_ab_to_electrons`). The `mag_w146` column holds F146 AB magnitudes.
10. **`sampler.py`** — `sample_field(provider, l_deg, b_deg, fov_deg, rng)` orchestrator. Cache key via `hashlib.sha256(repr((provider.__class__.__name__, round(l_deg, 6), round(b_deg, 6), round(fov_deg, 6))).encode()).hexdigest()`. Cache root configurable via `SMIG_CATALOG_CACHE` env var (default `~/.smig/catalog_cache/`).
11. **`__main__.py`** — `python -m smig.catalogs --l 1.0 --b -3.0 --fov 0.28 --provider synthetic` prints the projected DataFrame's head and column dtypes.
12. **Validation tests `smig/catalogs/validation/`:**
    - `test_base.py`: `StarRecord` frozenness (mutation raises `FrozenInstanceError`); default `mag_other_ab` is an immutable view.
    - `test_photometry.py`: `mag_ab_to_electrons(zero_point_mag, "F146", 139.8)` returns ≈ `exposure_s` (by definition of AB zero point); unknown band raises `ValueError`.
    - `test_wcs.py`: Galactic ↔ pixel round-trip within 1e-6 pixels for a grid of offsets up to 1 deg.
    - `test_besancon.py`: ingest the committed `besancon_smoke.csv`; verify column schema and `StarRecord` construction.
    - `test_adapter.py`: output DataFrame has columns exactly equal to the `_REQUIRED_COLUMNS` tuple read from `crowding.py` (imported, not hardcoded); dtypes appropriate for each column; `flux_e` values positive.
    - `test_synthetic_provider.py`: smoke — generate 50 stars, project to SCA, dataframe validates.

### Acceptance Criteria

**DONE when ALL pass:**

- [ ] `pytest -v` — baseline pass count + new Phase 3.1 tests, zero prior-test failures
- [ ] `python -c "from smig.catalogs import CatalogProvider, StarRecord, BesanconProvider, RomanBulgeProvider, SyntheticCatalogProvider; from types import MappingProxyType; s = StarRecord(galactic_l_deg=0, galactic_b_deg=0, distance_kpc=8, mass_msun=1, teff_K=5800, log_g=4.4, metallicity_feh=0, mag_F146_ab=18, source_id='x', catalog_tile_id='t'); print(type(s.mag_other_ab).__name__)"` — prints `mappingproxy`
- [ ] `StarRecord` mutation raises `FrozenInstanceError`
- [ ] `grep -rnE "BLOSC|pyarrow|parquet|xxhash|frozendict" smig/catalogs/ || true` prints no matches
- [ ] `test -f docs/phase3_photometry_reference.md`
- [ ] `test -f data/catalogs/bandpasses/roman_F146.csv`
- [ ] `python -m smig.catalogs --l 1.0 --b -3.0 --fov 0.28 --provider synthetic` exits 0 and prints a DataFrame
- [ ] `git diff --stat smig/rendering/ smig/optics/ smig/detector/ smig/config/seed.py smig/provenance/schema.py` prints no changes

Run exactly:
```bash
pytest -v
python -c "from smig.catalogs.adapter import project_to_sca_dataframe; print('ok')"
python -m smig.catalogs --l 1.0 --b -3.0 --fov 0.28 --provider synthetic
grep -rnE "BLOSC|pyarrow|parquet|xxhash|frozendict" smig/catalogs/ || true
test -f docs/phase3_photometry_reference.md && test -f data/catalogs/bandpasses/roman_F146.csv
git diff --stat smig/rendering/ smig/optics/ smig/detector/ smig/config/seed.py smig/provenance/schema.py
```

After all pass: ✅ **Phase 3.1 complete. Ready for Phase 3.2.**

---

## Prompt 2 of 6 — Phase 3.2: Microlensing Physics Engine

**Model: Claude Opus 4.7 in plan mode for `docs/phase3_2_design.md` and `binary.py`. Hand off the remaining modules to Sonnet 4.6.** The library-choice audit, caustic failure taxonomy, and θ_E consistency analysis justify the stronger planner.

### Role & Context
You are a senior microlensing physicist and numerical-methods engineer. You are executing **Phase 3.2 of 6**.

**Where we are:** Phases 1, 2, 3.1 complete. `StarRecord` (frozen) provides `mass_msun`, `teff_K`, `log_g`, `metallicity_feh`, `distance_kpc`, `mag_F146_ab`, `catalog_tile_id`, `source_id`.

**What this phase delivers:** Validated magnification calculators for PSPL, FSPL (Yoo 2004 + Claret 2000 linear LD), and 2L1S (single pinned backend: VBBinaryLensing). A frozen `MicrolensingEvent` dataclass that carries its own backend provenance (no `smig/provenance/schema.py` changes). A frozen `SourceProperties` struct consumed by `event.magnification(...)`. Suzuki et al. 2016 reference-event JSON committed for Phase 3.6 regression.

**What comes next:** Phase 3.3 binds `MicrolensingEvent.magnification(...)` into the Phase 2 `SceneSimulator` via a thin adapter — no invasive rendering changes.

### Carry-Forward Context
- **Seed utilities (existing only):** `derive_event_seed(master_seed, event_id)`, `derive_stage_seed(event_seed, stage_name)`. `priors.py` uses `derive_stage_seed(event_seed, "microlensing_sample")`.
- **Catalog contract (frozen at 3.1):** `StarRecord` fields listed above.
- **Photometry contract:** `mag_ab_to_electrons(mag, band, exposure_s)` returns total integrated electrons. Magnification is dimensionless; physics does not touch photometry conversion.
- **Provenance scope:** `smig/provenance/schema.py` is OFF-LIMITS. Backend identification, version, and LD fallback flags MUST be carried on the `MicrolensingEvent` itself.
- **Scope exclusions:** no orbital motion, no xallarap, no 2L2S, no astrometric shifts. Parallax fields exist on the dataclass but default to 0.

### Target Files

**IN SCOPE:**
- `smig/microlensing/__init__.py`
- `smig/microlensing/event.py` — frozen `MicrolensingEvent`, `EventClass` enum, frozen `SourceProperties`
- `smig/microlensing/pspl.py`, `fspl.py`, `binary.py`
- `smig/microlensing/limb_darkening.py` — Claret 2000 trilinear interpolator
- `smig/microlensing/priors.py` — Kroupa IMF, Galactic density, velocity dispersion, q/s/α priors, θ_E derivation
- `smig/microlensing/backends.py` — VBBL version resolution + pin verification
- `smig/microlensing/errors.py` — `MicrolensingComputationError`, `ClaretGridError`
- `smig/microlensing/validation/test_event_api.py`, `test_pspl.py`, `test_fspl.py`, `test_binary.py`, `test_priors.py`, `test_backend_pin.py`
- `data/microlensing/claret2000_ld.csv` — committed Claret 2000 LD grid
- `data/microlensing/reference_events/suzuki2016_sample.json` — 5 events with published parameters + peak magnifications
- `docs/phase3_2_design.md` — 1-to-2-page design doc
- `pyproject.toml` — add **one** pinned VBBL package line; add optional `[project.optional-dependencies].phase3-test` with `MulensModel` for cross-check tests

**OUT OF SCOPE:**
- All Phase 1 / 2 / 3.1 modules — frozen
- `smig/provenance/schema.py` — frozen
- `scripts/validate_splits.py` — read-only

### Rules of Engagement
- **Single pinned backend.** VBBinaryLensing (Bozza 2010+) is the ONLY production 2L1S backend. **Do NOT hardcode a version string you cannot verify.** Instead: (a) resolve latest stable at install time, (b) pin the exact resolved version in `pyproject.toml`, (c) record it in `MicrolensingEvent.backend_version`, (d) verify import + version match in `backends.py` via an assertion that fails loudly on drift. Every event provenance records `backend="VBBinaryLensing"` and `backend_version=<exact resolved string>`.
- **No runtime silent fallback.** On VBBL numerical failure (classified per the taxonomy in the design doc), raise `MicrolensingComputationError` with the full parameter dict. Never substitute a different backend silently.
- **MulensModel appears ONLY in `smig/microlensing/validation/`** as a cross-check oracle. It is an optional test-only dependency (`[project.optional-dependencies].phase3-test`). Tests that import MulensModel MUST skip via `pytest.importorskip("MulensModel")` when unavailable.
- **FSPL LD policy:** `strict_ld_grid=True` is the default; out-of-grid raises `ClaretGridError`. `strict_ld_grid=False` permits nearest-neighbor fallback AND sets `MicrolensingEvent.ld_fallback_used = True` (the field lives on the event dataclass).
- **Interface freeze gate at end of phase.** `MicrolensingEvent` field list, `SourceProperties` field list, and `.magnification(t_mjd, band, source_props)` signature become LOCKED. State this explicitly in `event.py`'s module docstring. Any later change is a versioned migration.
- **θ_E single source of truth.** `priors.sample_event(...)` computes `theta_E_mas` from sampled `(M_lens, D_L, D_S)` exactly once and writes it to the frozen `MicrolensingEvent`. Consumers read, never re-compute.
- **ρ derivation:** use `log_g` (exact). Source physical radius `R_star = sqrt(G · M_star / g)` where `g = 10**log_g` (cgs). Angular source radius `θ_* = R_star / D_S`. Then `rho = θ_* / θ_E`. Document this chain in `priors.py` and in the design doc. **Do NOT use Stefan-Boltzmann** — mass and Teff alone do not determine radius.
- **`event_class` assignment logic:** PSPL when `q == 0` and `rho < 1e-3`; FSPL_STAR when `q == 0` and `rho >= 1e-3`; for `q > 0`, assign binary topology from (q, s) using Cassan 2008 close/resonant/wide boundaries as documented in the design doc. Map topologies to `PLANETARY_CAUSTIC` (q < 0.03) / `STELLAR_BINARY` (q >= 0.03). `HIGH_MAGNIFICATION_CUSP` when any binary event has peak u0 < 0.05. Design doc justifies every boundary with a citation.
- **Over-engineering guardrail:** implement only what this phase requires. No orbital motion, no xallarap, no 2L2S, no astrometric centroid shifts, no non-zero parallax activation.
- **Stop and ask before:** adding any runtime dependency beyond VBBinaryLensing (MulensModel is test-extra only), modifying `smig/config/seed.py` or `smig/provenance/schema.py`, deleting any existing file, modifying any file outside the IN SCOPE list.

### Execution Tasks

**Do NOT write production code until `docs/phase3_2_design.md` is committed. This design-doc pass is the Opus-4.7 plan-mode value driver.** The doc MUST cover:

1. Complete `MicrolensingEvent` field list with units, frozenness, provenance fields (`backend`, `backend_version`, `ld_fallback_used`), and the explicit statement that all fields are computed-once at event construction (no mutation, no lazy derivation).
2. Complete `SourceProperties` field list, including which fields are physics-relevant per event class (PSPL ignores `band`; FSPL uses `band` for LD; binary uses `band` only if LD applied to resolved-source tests).
3. Full chain for θ_E and ρ, including unit conversions and edge-case handling (e.g., `log_g` out of reasonable range).
4. VBBL failure classification taxonomy — enumerate every error mode the binding must translate to `MicrolensingComputationError`.
5. Cassan 2008 topology boundary definitions with citation, mapped to `EventClass` values.
6. `strict_ld_grid` policy and how `ld_fallback_used` propagates.

After the doc is committed:

7. **`event.py`** — frozen `MicrolensingEvent`:
   - Physics: `event_id: str`, `t0_mjd: float`, `tE_days: float`, `u0: float`, `rho: float`, `alpha_rad: float`, `q: float = 0.0`, `s: float = 0.0`, `pi_E_N: float = 0.0`, `pi_E_E: float = 0.0`, `theta_E_mas: float`
   - Classification: `event_class: EventClass`
   - Provenance: `backend: str`, `backend_version: str`, `ld_fallback_used: bool = False`
   - Method: `.magnification(t_mjd: np.ndarray, band: str, source_props: SourceProperties) -> np.ndarray`
   - `EventClass` enum: `{PSPL, FSPL_STAR, PLANETARY_CAUSTIC, STELLAR_BINARY, HIGH_MAGNIFICATION_CUSP}`
   - Frozen `SourceProperties`: `teff_K: float`, `log_g: float`, `metallicity_feh: float`, `distance_kpc: float`, `mass_msun: float`
   - Module docstring includes the explicit freeze notice.

8. **`backends.py`** — `get_primary_backend() -> tuple[str, str]` returns `("VBBinaryLensing", <exact version>)`. Module-level assertion fails loudly if the installed version differs from the pin. The pin lives in `pyproject.toml`; `backends.py` reads it via `importlib.metadata.version("VBBinaryLensing")` (or the actual PyPI distribution name resolved at install time) and cross-checks.

9. **`pspl.py`** — exact analytic Paczyński: `u(t) = sqrt(u0**2 + ((t - t0) / tE)**2)`, `A(u) = (u**2 + 2) / (u * sqrt(u**2 + 4))`. Band-agnostic.

10. **`limb_darkening.py`** — load `claret2000_ld.csv` (columns `Teff_K, log_g, FeH, band, a_linear`). Trilinear interpolation on (Teff, log_g, [Fe/H]) per band. Enforce `strict_ld_grid` policy.

11. **`fspl.py`** — Yoo et al. 2004 B₀(z), B₁(z) tabulation with Claret linear LD. `z = u / rho`. For the F146 smoke band, load the LD coefficient via `limb_darkening.get_coefficient(source_props, band="F146")`.

12. **`binary.py`** — import the VBBL Python binding per the library's actual documented API (do NOT hardcode `VBBinaryLensing.VBBinaryLensing()` as a fact — verify the actual class/function name on install and use it). Set `RelTol = 1e-3`, `Tol = 1e-3`. Function `magnification_2l1s(t, t0, tE, u0, rho, alpha, q, s) -> np.ndarray`. On library numerical failure, re-raise as `MicrolensingComputationError(params=..., cause=...)`.

13. **`priors.py`** — `sample_event(rng: np.random.Generator, source_star: StarRecord, event_class_target: EventClass | None = None) -> MicrolensingEvent`:
    - Lens mass: Kroupa 2001 IMF
    - Lens distance: Galactic density profile (document the exact profile in the design doc)
    - Source distance: `source_star.distance_kpc`
    - Relative proper motion: velocity-dispersion model
    - Derive `theta_E_mas` from `(M_L, D_L, D_S)` via the standard formula
    - `tE_days` follows from θ_E and μ_rel
    - If binary: log-uniform `q ∈ [1e-5, 1.0]`, log-uniform `s ∈ [0.3, 3.0]`, uniform `α ∈ [0, 2π)`
    - Uniform `u0 ∈ [0, 1.5]`
    - Source radius from `log_g`: `R_star = sqrt(G * mass_msun / 10**log_g)` in SI, convert to AU, then `θ_* = R_star / D_S`, then `rho = θ_* / theta_E`
    - Assign `event_class` per the logic in Rules of Engagement
    - Return the fully-populated frozen event

14. **Commit `data/microlensing/reference_events/suzuki2016_sample.json`** — 5 events from Suzuki et al. 2016 with published `(t0, tE, u0, rho, q, s, alpha)` plus published peak magnification.

15. **Validation tests `smig/microlensing/validation/`:**
    - `test_event_api.py`: `MicrolensingEvent` and `SourceProperties` frozen; `.magnification` signature matches the freeze notice exactly.
    - `test_pspl.py`: peak magnification `u0=1e-3` within 0.1% of `1/u0`; baseline asymptote `|t-t0|=10·tE` within `1e-4` of 1.0; time symmetry within `1e-12`.
    - `test_fspl.py`: `z ≫ 1` → PSPL limit within 0.1%; `z ≪ 1` plateau matches Yoo B₀(0) within 0.1%; out-of-grid + `strict_ld_grid=True` raises `ClaretGridError`; out-of-grid + `strict_ld_grid=False` sets `ld_fallback_used=True` on the returned event.
    - `test_binary.py`: load `suzuki2016_sample.json`; compute magnification at published peak time via pinned VBBL; assert within 1e-3 relative error. Cross-check two non-caustic-crossing events against MulensModel via `pytest.importorskip("MulensModel")`. Mark the full-suite run `@pytest.mark.slow`.
    - `test_priors.py`: moments of 10,000 sampled events match analytic priors within 2σ. `@pytest.mark.slow`.
    - `test_backend_pin.py`: `get_primary_backend()` returns the pinned version; tampering with `pyproject.toml` in a temp env causes the module-level assertion to raise (documented but not CI-enforced).

### Acceptance Criteria

- [ ] `test -f docs/phase3_2_design.md` and it covers the six mandated sections above
- [ ] `pytest smig/microlensing/validation/ -v -m "not slow"` green
- [ ] `pytest -v` green (all prior tests + new fast tests, zero regressions)
- [ ] `MicrolensingEvent(...)` and `SourceProperties(...)` mutations raise `FrozenInstanceError`
- [ ] `grep -rnE "mulensmodel|MulensModel" smig/microlensing/ --exclude-dir=validation || true` prints no matches
- [ ] `python -c "from smig.microlensing import MicrolensingEvent, SourceProperties, get_primary_backend; print(get_primary_backend())"` prints a `(name, version)` tuple with a non-empty version string
- [ ] `event.py` module docstring contains the literal freeze notice
- [ ] `test -f data/microlensing/reference_events/suzuki2016_sample.json` and it contains exactly 5 events

Run exactly:
```bash
test -f docs/phase3_2_design.md
pytest smig/microlensing/validation/ -v -m "not slow"
pytest -v
python -c "from smig.microlensing import MicrolensingEvent, SourceProperties, get_primary_backend; print(get_primary_backend())"
grep -rnE "mulensmodel|MulensModel" smig/microlensing/ --exclude-dir=validation || true
test -f data/microlensing/reference_events/suzuki2016_sample.json
```

After all pass: ✅ **Phase 3.2 complete. `MicrolensingEvent` API frozen. Ready for Phase 3.3.**

---

## Prompt 3 of 6 — Phase 3.3: Event-Source Binding Adapter

**Model: Claude Code Sonnet 4.6 (standard).**

### Role & Context
You are a senior integration engineer connecting astrophysical physics to an already-locked rendering pipeline. You are executing **Phase 3.3 of 6**.

**Where we are:** Phases 1–3.2 complete. Before writing any code, inspect:
- `smig/rendering/pipeline.py` — the `SceneSimulator.simulate_event(...)` signature and its expected `source_params_sequence` element shape
- `smig/rendering/source.py` — what fields the source renderer actually reads

**Critical facts learned from that inspection:**
- `source_params_sequence` is `list[dict]` (Phase 2 internal convention). Do NOT invent a new `SourceParams` type.
- Each dict carries at minimum `flux_e: float` — **total integrated electrons over the epoch exposure**, not e⁻/s.
- Optional dict fields include `centroid_offset_pix` (tuple), `rho_star_arcsec`, `limb_darkening_coeffs`. These are rendering fields; microlensing physics does NOT repurpose them.
- `simulate_event` does NOT accept WCS objects, absolute SCA coordinates, or field centers. The microlensed source is drawn at the stamp center for Phase 3 smoke datasets.

**What this phase delivers:** A thin adapter `bind_event_to_source` that takes `(MicrolensingEvent, StarRecord, epoch_times_mjd, exposure_s)` and returns `list[dict]` matching the Phase 2 `source_params_sequence` contract, with `flux_e = A(t) * F0_total_e` where `F0_total_e` is the baseline total electrons from `mag_ab_to_electrons(source_star.mag_F146_ab, "F146", exposure_s)`. Ships with null + PSPL-peak regression tests.

**What comes next:** Phase 3.4 freezes the dataset contract around the binding's outputs.

### Carry-Forward Context
- **Frozen:** `SceneSimulator`, `MicrolensingEvent`, `SourceProperties`, `StarRecord`.
- **`source_params_sequence` shape:** `list[dict]` with `flux_e` mandatory (total integrated electrons). Optional fields pass through from conservative defaults.
- **Microlensed source is CENTERED** in the Phase 2 cutout. No WCS, no absolute pixel coords, no `centroid_offset_pix` unless documented as a future extension.
- **Photometry:** `mag_ab_to_electrons` returns total electrons over `exposure_s` — the same units Phase 2 expects.
- **σ for null test:** use the DIA noise-floor estimate already produced by `smig/rendering/dia.py`. Do NOT hand-derive a σ.

### Target Files

**IN SCOPE:**
- `smig/microlensing/binding.py`
- `smig/microlensing/validation/test_binding.py`
- Single-line export addition to `smig/microlensing/__init__.py`

**OUT OF SCOPE (DO NOT MODIFY):**
- `smig/rendering/*`, `smig/optics/*`, `smig/detector/*` — frozen
- `smig/microlensing/event.py`, `pspl.py`, `fspl.py`, `binary.py`, `priors.py` — frozen after 3.2
- `smig/catalogs/*` — frozen after 3.1
- `scripts/validate_splits.py` — read-only

### Rules of Engagement
- **Composition only.** No microlensing physics in `binding.py` beyond calling `event.magnification(...)`. No rendering decisions. Zero changes to `SceneSimulator`.
- **Type signatures match Phase 2.** Return `list[dict]` matching what `simulate_event` already accepts. Do NOT introduce a new `SourceParams` dataclass.
- **Centered source assumption.** Document this in `binding.py`'s module docstring. If a future phase needs off-center microlensed sources, it adds the field explicitly to the binding signature with a versioned migration.
- **Exposure time source.** The caller passes `exposure_s` explicitly. Do NOT silently read it from a config inside `binding.py` — that's the orchestrator's job in Phase 3.5.
- **Stop and ask before:** modifying any file outside `smig/microlensing/binding.py`, `smig/microlensing/validation/test_binding.py`, or the single export line in `smig/microlensing/__init__.py`.

### Execution Tasks

1. **Read first.** Inspect `smig/rendering/pipeline.py:218-330` and `smig/rendering/source.py`. Extract the exact dict shape of `source_params_sequence[i]`. Paste the field names and types verbatim as a module-level doc comment in `binding.py`. Also read `smig/rendering/dia.py` to find the noise-floor estimate field name returned by the DIA path.
2. **Implement:**
    ```python
    def bind_event_to_source(
        event: MicrolensingEvent,
        source_star: StarRecord,
        epoch_times_mjd: np.ndarray,
        exposure_s: float,
        band: str = "F146",
    ) -> list[dict]:
        """
        Produces source_params_sequence matching Phase 2 SceneSimulator.simulate_event contract.

        flux_e semantics: TOTAL integrated electrons over the exposure window,
        == A(t_i) * mag_ab_to_electrons(source_star.mag_F146_ab, band, exposure_s).

        The microlensed source is drawn at the stamp center. This phase does not
        support off-center microlensed sources; that is a versioned future extension.
        """
        source_props = SourceProperties(
            teff_K=source_star.teff_K,
            log_g=source_star.log_g,
            metallicity_feh=source_star.metallicity_feh,
            distance_kpc=source_star.distance_kpc,
            mass_msun=source_star.mass_msun,
        )
        A_t = event.magnification(epoch_times_mjd, band, source_props)
        F0_total_e = mag_ab_to_electrons(source_star.mag_F146_ab, band, exposure_s)
        return [{"flux_e": float(A_t[i] * F0_total_e)} for i in range(len(epoch_times_mjd))]
    ```
    If inspection of `source.py` reveals additional MANDATORY fields beyond `flux_e`, populate them from Phase-2-safe defaults documented in the inspection comment. Do not invent defaults.
3. **Export** `bind_event_to_source` from `smig/microlensing/__init__.py`.
4. **Null test (`test_binding.py::test_null_dia_aggregate`):**
    - Construct a PSPL event with `u0 = 100.0` so A ≈ 1 across all epochs.
    - Bind, run through `SceneSimulator`, extract the DIA difference cube and the noise-floor estimate σ from the DIA output.
    - Compute `r = abs(dia_cube) / sigma`.
    - Assert `np.median(r) < 0.3` AND `np.percentile(r, 99.5) < 4.0`.
    - Document both thresholds in a comment citing the DIA residual-structure context.
5. **PSPL peak test (`test_binding.py::test_pspl_peak_ideal_cube`):**
    - Construct a PSPL event with `u0 = 1e-3`, `F146_AB = 18.0` source.
    - Bind across 11 epochs centered on t0.
    - Instead of DIA: extract the **ideal pre-DIA electron cube** (`SceneSimulator` exposes this internally — if it does not, assert against `flux_e` in the source params dict directly, which is the input contract).
    - Assert `flux_e[peak_epoch] / flux_e[baseline_epoch]` is within **2% of the analytic `A_peak / A_baseline`** ratio from the PSPL formula. This tests the binding math in isolation without DIA/PSF convolution tolerance issues.
6. **Contract test (`test_binding.py::test_return_type_is_list_of_dict`):**
    - Assert `isinstance(result, list)` and `all(isinstance(x, dict) and "flux_e" in x for x in result)`.
    - Assert dtype of `flux_e` is `float` (not numpy scalar).

### Acceptance Criteria

- [ ] `pytest smig/microlensing/validation/test_binding.py -v` green
- [ ] `pytest -v` green (zero regressions)
- [ ] `git diff --stat smig/rendering/ smig/optics/ smig/detector/ smig/catalogs/` prints no changes
- [ ] `git diff --stat smig/microlensing/event.py smig/microlensing/pspl.py smig/microlensing/fspl.py smig/microlensing/binary.py smig/microlensing/priors.py` prints no changes
- [ ] Null test: `np.median(r) < 0.3` AND `np.percentile(r, 99.5) < 4.0`
- [ ] PSPL peak test: ideal-cube ratio within 2% of analytic

Run exactly:
```bash
pytest smig/microlensing/validation/test_binding.py -v
pytest -v
git diff --stat smig/rendering/ smig/microlensing/event.py smig/microlensing/pspl.py smig/microlensing/fspl.py smig/microlensing/binary.py smig/microlensing/priors.py smig/catalogs/
```

After all pass: ✅ **Phase 3.3 complete. Binding adapter live. Ready for Phase 3.4.**

---

## Prompt 4 of 6 — Phase 3.4: Dataset Contract (Labels, Splits, Manifest, Shard Schema)

**Model: Claude Code Sonnet 4.6 (standard).** Schema work; Opus is not required provided the agent re-reads `scripts/validate_splits.py` carefully.

### Role & Context
You are a senior ML data engineer defining the frozen contract every downstream component will depend on. You are executing **Phase 3.4 of 6**.

**Where we are:** Phases 1–3.3 complete. The binding adapter produces per-event per-epoch flux sequences that `SceneSimulator` turns into stamp cubes. The repo already has `scripts/validate_splits.py` which expects a JSON manifest — **re-read that script end to end before writing any schema code.** It dictates:
- manifest shape: `{"events": [{"event_id": str, "split": str, "starfield_seed": int, "params": {...}}, ...]}`
- split values: `"train" | "val" | "test"`
- parameter-similarity Union-Find at 5% edge threshold on `params`
- shared `starfield_seed` across splits = leakage, full stop

**What this phase delivers:** A frozen dataset contract — `LabelVector`, split assignment rule, flat HDF5 shard layout, and the canonical JSON manifest emitter — that Phase 3.5's orchestrator writes against without further negotiation.

**What comes next:** Phase 3.5 builds the process-pool orchestrator and atomic writer against this locked contract.

### Carry-Forward Context
- **Validator path:** `scripts/validate_splits.py`. **Re-read it.** Manifest JSON must match exactly what that script expects — no Parquet substitute.
- **Single-band smoke:** `source_mag_F146_ab` (AB system) is the one photometric label.
- **Scope exclusions:** no orbital motion, no xallarap, no 2L2S, no astrometric shifts, no non-zero parallax in smoke configs.
- **`N_EPOCHS` is per-dataset, not per-code.** Store as an HDF5 file attribute; the smoke YAML config defines the concrete integer. No compile-time constant.
- **Hashing:** `hashlib.sha256(repr(key).encode()).hexdigest()` for split assignment. No `xxhash`.

### Target Files

**IN SCOPE:**
- `smig/datasets/__init__.py`
- `smig/datasets/labels.py` — frozen `LabelVector` + `EventClass` re-export
- `smig/datasets/splits.py` — deterministic split assignment
- `smig/datasets/schema.py` — HDF5 layout + schema version
- `smig/datasets/manifest.py` — `DatasetManifest` dataclass + canonical JSON serializer
- `smig/datasets/validation/test_labels.py`, `test_splits.py`, `test_schema.py`, `test_manifest.py`, `test_validator_compat.py`
- `smig/datasets/validation/fixtures/synthetic_manifest.json` — small committed fixture (diverse params to avoid accidental similarity edges)
- `docs/phase3_dataset_contract.md` — 1-page human spec

**OUT OF SCOPE:**
- All frozen upstream modules
- `scripts/validate_splits.py` — read-only, must remain compatible
- No orchestrator, no writer, no process pool — Phase 3.5

### Rules of Engagement
- **Contract freeze at end of phase.** `LabelVector` field list + order + dtypes, manifest JSON schema, HDF5 layout constants become LOCKED. State this in each module docstring.
- **Flat HDF5 layout — one HDF5 file per shard, parallel datasets (NOT compound dtype, NOT per-event groups):**
  - `/science_stamps` shape `(N, n_epochs, 64, 64)` float32
  - `/saturation_stamps` shape `(N, n_epochs, 64, 64)` uint8 (only if Phase 2 produces; else omit per-shard and document)
  - `/cr_stamps` shape `(N, n_epochs, 64, 64)` uint8 (same)
  - One dataset per `LabelVector` field: `/label__event_class` (uint8 enum), `/label__log_tE` (float32), `/label__log_u0` (float32), `/label__log_rho` (float32), `/label__alpha_rad` (float32), `/label__log_q` (float32), `/label__log_s` (float32), `/label__t0_mjd_normalized` (float32), `/label__source_mag_F146_ab` (float32), `/label__lens_mass_msun` (float32), `/label__source_distance_kpc` (float32), `/label__lens_distance_kpc` (float32)
  - `/event_id` variable-length string shape `(N,)`
  - `/starfield_seed` uint64 shape `(N,)` (values < 2⁵³ for JSON-safe serialization)
  - `/shard_row_index` uint32 shape `(N,)` — O(1) intra-shard lookup
  - File attributes: `schema_version: "phase3-contract-v1"`, `shard_id: int`, `n_epochs: int`, `smig_version: str`, `writer_backend: "h5py"`
- **Chunking:** `/science_stamps` chunk shape `(1, n_epochs, 64, 64)` for DataLoader-friendly access. Set via `schema.science_stamp_chunks(n_epochs)`.
- **Compression:** `("gzip", 4)` (h5py built-in). **No BLOSC, no pyarrow, no parquet.**
- **Schema version string:** `"phase3-contract-v1"` — NOT tied to phase number; immutable going forward.
- **Split rule:** `assign_split(event_id, starfield_seed, catalog_tile_id, source_star_id, ratios=(0.8, 0.1, 0.1))`:
  - Primary group key: `starfield_seed` — all events with the same `starfield_seed` MUST land in the same split (required by `validate_splits.py`).
  - Additional leakage protection: the hash seed combines `(starfield_seed, catalog_tile_id, source_star_id)` so reused stars with different starfield seeds still cluster, but the assignment is still fully determined by `starfield_seed` to satisfy the validator.
  - Implementation: compute `bucket = int.from_bytes(hashlib.sha256(f"{starfield_seed}".encode()).digest()[:8], "little") % 10000`; map bucket ranges to train/val/test per ratios. Whole-group-invariant test MUST enforce: same `starfield_seed` → same split regardless of other fields.
- **Manifest output MUST match `scripts/validate_splits.py` exactly.** Parquet sidecar is explicitly FORBIDDEN in this phase; analytics Parquet may be added in Phase 4 but is not a substitute.
- **Stop and ask before:** adding any dependency, modifying `scripts/validate_splits.py`, changing any frozen upstream interface, introducing compound HDF5 dtypes.

### Execution Tasks

1. **Read `scripts/validate_splits.py` end-to-end.** Document the exact manifest shape, required fields, the 5% similarity Union-Find threshold, and the `params` field's expected content in `smig/datasets/manifest.py`'s module docstring.
2. **`labels.py` — frozen `LabelVector`** (fields listed above, in this exact order for HDF5 dataset stability). Methods: `.to_label_dict() -> dict[str, Any]`, `.iter_hdf5_datasets() -> Iterator[tuple[str, Any]]` (yields `(dataset_name, value)` pairs for the writer). Re-export `EventClass` from `smig.microlensing`.
3. **`splits.py`** — `assign_split(event_id, starfield_seed, catalog_tile_id, source_star_id, ratios=(0.8, 0.1, 0.1)) -> Literal["train", "val", "test"]` per Rules of Engagement. Validator-compatible (group by `starfield_seed` primary).
4. **`schema.py`:**
    ```python
    DATASET_SCHEMA_VERSION = "phase3-contract-v1"
    SCIENCE_STAMP_SHAPE = (64, 64)
    HDF5_COMPRESSION = ("gzip", 4)

    def science_stamp_chunks(n_epochs: int) -> tuple[int, int, int, int]:
        return (1, n_epochs, 64, 64)

    LABEL_DATASET_NAMES: tuple[str, ...] = (...)  # frozen order
    ```
5. **`manifest.py`** — `DatasetManifest` frozen-except-for-append with `.add_event(event_id: str, split: str, starfield_seed: int, params: dict[str, Any])`, `.to_json_path(path: Path)` emitting `{"events": [...]}` with (a) sorted keys throughout, (b) `starfield_seed` serialized as plain int, (c) no NaN/Inf in params. Recursive canonicalization for nested dicts.
6. **`docs/phase3_dataset_contract.md`** — 1 page: `LabelVector` field list and order, HDF5 layout table, manifest JSON shape, split rule algorithm, schema version.
7. **Validation tests:**
    - `test_labels.py`: frozenness, field order matches `LABEL_DATASET_NAMES`, `iter_hdf5_datasets` yields all fields exactly once.
    - `test_splits.py`: whole-group invariant — 500 events sharing `starfield_seed=42` but varying `catalog_tile_id` and `source_star_id` all assigned the same split. Ratio convergence within 2% on 10,000 events with distinct seeds.
    - `test_schema.py`: chunk shape, schema version string exact, no compound dtypes imported.
    - `test_manifest.py`: JSON round-trip, canonical ordering, `starfield_seed` serialized as JSON int.
    - `test_validator_compat.py`: build `fixtures/synthetic_manifest.json` with 16 events (diverse params to avoid accidental similarity edges); run `scripts/validate_splits.py` as subprocess via `subprocess.run([sys.executable, "scripts/validate_splits.py", fixture_path], check=True)`; assert exit 0 AND no "leakage" or "warning" substring in stderr.

### Acceptance Criteria

- [ ] `pytest smig/datasets/validation/ -v` green
- [ ] `pytest -v` green (zero regressions)
- [ ] `LabelVector` and `DatasetManifest` enforce frozen / controlled-mutation semantics
- [ ] `python scripts/validate_splits.py smig/datasets/validation/fixtures/synthetic_manifest.json` exits 0
- [ ] `test -f docs/phase3_dataset_contract.md`
- [ ] `grep -rnE "parquet|BLOSC|pyarrow|xxhash|frozendict" smig/datasets/ || true` prints no matches
- [ ] Composite split key algorithm documented in docstring AND enforced by whole-group-invariant test

Run exactly:
```bash
pytest smig/datasets/validation/ -v
pytest -v
python scripts/validate_splits.py smig/datasets/validation/fixtures/synthetic_manifest.json
grep -rnE "parquet|BLOSC|pyarrow|xxhash|frozendict" smig/datasets/ || true
```

After all pass: ✅ **Phase 3.4 complete. Dataset contract frozen. Ready for Phase 3.5.**

---

## Prompt 5 of 6 — Phase 3.5: Orchestrator + Atomic Writer + Checkpointing

**Model: Claude Opus 4.7 in plan mode for `docs/phase3_5_orchestrator_design.md` and the determinism/atomicity design. Sonnet 4.6 for the implementation pass against the approved design.** Multi-process determinism and atomic shard semantics are the traps that burn entire datasets.

### Role & Context
You are a senior distributed-systems engineer specializing in deterministic parallel data pipelines. You are executing **Phase 3.5 of 6**.

**Where we are:** Phases 1–3.4 complete. Dataset contract frozen. Binding adapter produces per-event epoch stamp cubes.

**What this phase delivers:** The process-pool orchestrator, atomic HDF5 shard writer, deterministic event scheduling, crash-safe checkpointing, and emission of a `scripts/validate_splits.py`-compatible manifest. This is the phase where the real catalog path FINALLY reaches `SceneSimulator` — in the worker, not in `pipeline.py`.

**What comes next:** Phase 3.6 locks Phase 3 with risk-register regression gates.

### Carry-Forward Context
- **GalSim is NOT thread-safe.** `concurrent.futures.ProcessPoolExecutor` only.
- **Seed utilities:** `derive_event_seed(master_seed, event_id)`, `derive_stage_seed(event_seed, stage_name)`. Workers are STATELESS executors; all randomness derives from the stable `event_id` via these helpers inside the worker process. No worker-identity seeds.
- **Frozen dataset contract (3.4):** flat HDF5 layout, parallel label datasets (not compound dtype), `(1, n_epochs, 64, 64)` chunks, gzip level 4, manifest JSON schema. Do NOT renegotiate.
- **Validator path:** `scripts/validate_splits.py` is the hard gate.
- **Determinism definition:** same master seed + same config + same codebase ⇒ same **decoded HDF5 array payloads** and **sorted-identical manifest JSON**. NOT byte-identical HDF5 files.
- **Atomic writes:** write to `*.tmp` → fsync → atomic rename. Never append to a partially valid shard on resume; always start a fresh shard and record continuity in the checkpoint.
- **IPC payload discipline:** workers return `(stamps: np.ndarray shape (n_epochs, 64, 64) float32, labels: LabelVector, starfield_seed: int, event_id: str)` — **small**. Workers MUST NOT return the full `ideal_cube_e` or any 256×256 array; those are released inside `SceneSimulator` per the Phase 2 memory lifecycle.

### Target Files

**IN SCOPE:**
- `smig/datasets/config.py` — `PhaseConfig` Pydantic model
- `smig/datasets/generator.py` — `DatasetBuilder`
- `smig/datasets/writer.py` — atomic `ShardWriter`
- `smig/datasets/checkpoint.py` — SQLite WAL manifest tracker
- `smig/datasets/worker.py` — stateless per-event generator
- `smig/datasets/validation/test_generator.py`, `test_writer.py`, `test_checkpoint.py`, `test_resume.py`, `test_determinism.py`, `test_worker_payload.py`
- `configs/phase3_smoke.yaml` — 16-event smoke config
- `scripts/build_dataset.py` — CLI entry
- `docs/phase3_5_orchestrator_design.md`

**OUT OF SCOPE (DO NOT MODIFY):**
- All upstream frozen modules, including `smig/datasets/labels.py`, `splits.py`, `schema.py`, `manifest.py`
- `scripts/validate_splits.py` — read-only

### Rules of Engagement
- **Design doc before code.** `docs/phase3_5_orchestrator_design.md` MUST cover:
  1. Event ID enumeration algorithm: `event_id_i = f"{master_seed:016x}-{i:08d}"` for `i in range(n_events)`, sorted for submission.
  2. Worker lifecycle: receives `(event_id, master_seed, config_dict)`, returns payload, exits cleanly after each task (stateless across tasks).
  3. Deterministic result collection: `ProcessPoolExecutor.map` with `chunksize=1` preserves order; results collected in event_id order before shard write.
  4. Shard boundary semantics: one writer per shard, no concurrent append, discard `.tmp` on crash, fresh shard on resume.
  5. Checkpoint protocol: SQLite WAL mode, insert after fsync+rename only.
  6. Resume algorithm: enumerate all event_ids → subtract completed from checkpoint DB → group remaining into shards → submit.
  7. Failure classification: worker OOM, HDF5 I/O, catalog read, microlensing computation, binding, DIA extraction.
- **Determinism contract:** decoded arrays equal via `np.testing.assert_array_equal`; sorted-canonical manifest JSONs byte-equal.
- **Worker statelessness.** No per-worker cached state survives across tasks. All randomness derives from `event_id` inside the worker via existing seed helpers.
- **Shard discipline:**
  - `shard_size` from config (default 1024); last shard may be smaller.
  - One writer process per shard — the MAIN process, not workers. Workers compute only; do not touch HDF5.
  - On crash mid-shard: the `.tmp` file is deleted by `ShardWriter.__exit__(exc_type=...)`; resume starts a fresh shard.
- **Checkpoint atomicity:** SQLite WAL. Schema `(event_id TEXT PRIMARY KEY, shard_id INT, row_index INT, completed_at TIMESTAMP, split TEXT)`. INSERT only after `ShardWriter.close()` returns successfully AND `os.fsync(fd)` AND atomic rename.
- **Manifest emission:** canonical JSON after every shard close (incremental) AND as a final consolidated file. Final must pass `scripts/validate_splits.py` exit 0.
- **Worker payload size cap:** `stamps` MUST be `float32 shape (n_epochs, 64, 64)` only. Test asserts the returned `stamps.nbytes <= 4 * n_epochs * 64 * 64 + 1024` (small allocator slack).
- **No autoscaling, no cluster scheduler, no dynamic pools.** Single-machine `ProcessPoolExecutor`.
- **CI install assumption:** orchestrator tests require `pip install -e '.[phase2]'` for GalSim and WebbPSF. Document this in the design doc and in the CLI `--help` text.
- **Stop and ask before:** adding dependencies, modifying any frozen upstream interface, deleting any Phase 3.4 file.

### Execution Tasks

1. **`docs/phase3_5_orchestrator_design.md` first.** Commit before writing any code. Opus 4.7 plan mode earns its keep here.
2. **`config.py`** — `PhaseConfig` Pydantic model with fields `n_events`, `shard_size`, `n_workers`, `n_epochs`, `exposure_s`, `master_seed`, `field_center_l_deg`, `field_center_b_deg`, `catalog_provider: Literal["synthetic", "besancon", "roman_bulge"]`, `event_class_distribution: dict[EventClass, float]`, `output_dir: Path`. Loadable from YAML.
3. **`checkpoint.py`** — `Checkpoint(db_path: Path)` with WAL. Methods `.record_complete(event_id, shard_id, row_index, split)`, `.completed_event_ids() -> set[str]`, `.next_shard_id() -> int`, `.close()`. Idempotent inserts (`INSERT OR IGNORE`).
4. **`writer.py`** — `ShardWriter(path: Path, shard_id: int, expected_n: int, n_epochs: int)` context manager. Writes to `{path}.tmp`, pre-allocates parallel datasets per `smig.datasets.schema`, chunk shape from `schema.science_stamp_chunks(n_epochs)`, compression `schema.HDF5_COMPRESSION`. `__exit__` on success: flush → close → `os.fsync` → `os.rename`. `__exit__` on exception: close HDF5 → delete `.tmp`. Writes file attributes (`schema_version`, `shard_id`, `n_epochs`, `smig_version`, `writer_backend`).
5. **`worker.py`** — stateless function `generate_event(event_id: str, master_seed: int, config_dict: dict) -> tuple[np.ndarray, dict, int]` returning `(stamps, label_dict, starfield_seed)`. Inside:
    - `event_seed = derive_event_seed(master_seed, event_id)`
    - Stage RNGs via `derive_stage_seed(event_seed, stage_name)` for: `"catalog_sample"`, `"microlensing_sample"`, `"binding"` (if stochastic, else omit), `"detector"`
    - Sample catalog field → pick source star → sample microlensing event → bind to source params sequence → run `SceneSimulator.simulate_event` → extract the 64×64×n_epochs science DIA stamps
    - Assemble `LabelVector`, return `(stamps_float32, label_vector.to_label_dict(), starfield_seed)`
    - No file I/O in the worker. No HDF5 access.
6. **`generator.py`** — `DatasetBuilder(config: PhaseConfig, resume: bool = False).build() -> None`:
    - Enumerate `event_id` list per the design-doc algorithm
    - Load `Checkpoint`; subtract completed ids (if `resume=True`)
    - Group remaining into shards of `config.shard_size`
    - For each shard: `ProcessPoolExecutor(max_workers=config.n_workers).map(_worker_wrapper, event_ids, chunksize=1)`; collect results into a dict keyed by `event_id`; iterate in sorted `event_id` order; open `ShardWriter`, write rows, close, checkpoint each event, emit incremental manifest
    - On `KeyboardInterrupt` / `SystemExit`: current shard's `.tmp` is discarded by `ShardWriter.__exit__`; checkpoint state survives; re-run with `--resume` starts fresh shard.
    - On worker exception: mark event as failed in a separate `failed_events.jsonl` file; continue; surface a summary at end.
7. **`scripts/build_dataset.py`** — argparse CLI:
    ```
    python scripts/build_dataset.py --config configs/phase3_smoke.yaml [--resume]
    ```
    `--help` lists required CI extras.
8. **`configs/phase3_smoke.yaml`** — `n_events: 16`, `shard_size: 8`, `n_workers: 4`, `n_epochs: 30` (or whatever the repo's existing Phase 2 cadence standard is — read and match), `exposure_s: 139.8`, `master_seed: 20260416`, `field_center_l_deg: 1.0`, `field_center_b_deg: -3.0`, `catalog_provider: synthetic`, `event_class_distribution: {PSPL: 0.5, FSPL_STAR: 0.2, PLANETARY_CAUSTIC: 0.2, STELLAR_BINARY: 0.1}`.
9. **Validation tests:**
    - `test_writer.py`: atomic rename on success; `.tmp` deleted on exception; reading pre-allocated datasets before close raises.
    - `test_checkpoint.py`: WAL concurrency smoke; idempotent insert.
    - `test_resume.py`: **mocked crash** — patch `ShardWriter.__exit__` to raise `SystemExit` partway through shard 1; run builder; assert `.tmp` gone, checkpoint has only shard 0 events; re-run with `resume=True`; final decoded arrays and manifest match an uninterrupted run of the same config.
    - `test_determinism.py`: two independent `.build()` calls with identical config into different output dirs. Assert `np.testing.assert_array_equal` on all science stamps and label datasets; sorted-canonical manifest JSONs byte-equal. `@pytest.mark.slow`.
    - `test_worker_payload.py`: run one `generate_event` directly (not via pool); assert `stamps.shape == (n_epochs, 64, 64)`, `stamps.dtype == np.float32`, `stamps.nbytes <= 4 * n_epochs * 64 * 64 + 1024`.
    - `test_generator.py`: 16-event smoke finishes; `scripts/validate_splits.py` exits 0 on resulting manifest. `@pytest.mark.slow`. Timing is informational-only (log but do not assert).

### Acceptance Criteria

- [ ] `test -f docs/phase3_5_orchestrator_design.md` (committed before code)
- [ ] `pytest smig/datasets/validation/ -v -m "not slow"` green
- [ ] `pytest -v` green (zero regressions)
- [ ] `pytest smig/datasets/validation/test_determinism.py -v` green (slow)
- [ ] `python scripts/build_dataset.py --config configs/phase3_smoke.yaml` completes without error
- [ ] `python scripts/validate_splits.py <output_dir>/manifest.json` exits 0, no "leakage" / "warning" in stderr
- [ ] `test_resume.py` passes — resumed run byte-matches uninterrupted run (decoded arrays + sorted manifest)
- [ ] `test_worker_payload.py` passes — no oversized IPC payloads
- [ ] `git diff --stat smig/datasets/labels.py smig/datasets/splits.py smig/datasets/schema.py smig/datasets/manifest.py` prints no changes

Run exactly:
```bash
test -f docs/phase3_5_orchestrator_design.md
pytest smig/datasets/validation/ -v -m "not slow"
pytest -v
pytest smig/datasets/validation/test_determinism.py smig/datasets/validation/test_generator.py -v
python scripts/build_dataset.py --config configs/phase3_smoke.yaml
python scripts/validate_splits.py outputs/phase3_smoke/manifest.json
git diff --stat smig/datasets/labels.py smig/datasets/splits.py smig/datasets/schema.py smig/datasets/manifest.py
```

After all pass: ✅ **Phase 3.5 complete. Orchestrator live, determinism verified. Ready for Phase 3.6.**

---

## Prompt 6 of 6 — Phase 3.6: Validation, Scientific Regression, Golden Event

**Model: Claude Code Sonnet 4.6 (standard).** Test authoring against fully-specified gates.

### Role & Context
You are a senior scientific software validation engineer. You are executing **Phase 3.6 of 6**, the final phase of SMIG v2 Phase 3.

**Where we are:** All prior phases complete. Orchestrator produces smoke datasets that pass `scripts/validate_splits.py`. Frozen interfaces: `StarRecord`, `MicrolensingEvent`, `SourceProperties`, `LabelVector`, `DatasetManifest`, HDF5 layout.

**What this phase delivers:** A repo-wide regression harness mapping every risk-register item to a named test. Determinism gate, split-validator gate, memory gate, scientific-validity gates (PSPL, FSPL, 2L1S vs Suzuki 2016), binding gates, and a human-readable golden-event visual report.

**What comes next:** Phase 4 (ML training) — out of scope.

### Carry-Forward Context
- **Risk register (Master Plan):**
  1. Binary-lens numerical failure → `test_binary_suzuki2016.py`
  2. Besançon catalog scale → `test_catalog_stats.py` (slow/integration)
  3. Multi-process RNG drift → `test_determinism_repo.py` (already in 3.5; this phase adds a repo-wide wrapper)
  4. HDF5 corruption on crash → `test_shard_atomicity.py`
  5. Split leakage via shared group keys → `test_split_validator_gate.py`
  6. FSPL LD out-of-grid → `test_ld_policy.py`
- **Gate coverage principle:** each risk item → at least one named test file. **No raw test-count target.**
- **Determinism contract:** numpy-equal decoded arrays + sorted-identical manifests. NOT byte-identity.
- **Reference data:** `data/microlensing/reference_events/suzuki2016_sample.json` (from 3.2).
- **Memory tooling:** `tracemalloc` (stdlib). **Do NOT use `memory_profiler`** — unmaintained and flaky on recent Python versions.

### Target Files

**IN SCOPE:**
- `smig/datasets/validation/test_scientific_pspl.py`
- `smig/datasets/validation/test_scientific_fspl.py`
- `smig/datasets/validation/test_binary_suzuki2016.py`
- `smig/datasets/validation/test_determinism_repo.py`
- `smig/datasets/validation/test_split_validator_gate.py`
- `smig/datasets/validation/test_shard_atomicity.py`
- `smig/datasets/validation/test_memory_ramp_peak.py`
- `smig/datasets/validation/test_ld_policy.py`
- `smig/datasets/validation/test_null_and_peak_binding_e2e.py`
- `smig/datasets/validation/test_catalog_stats.py` (slow/integration, skippable)
- `scripts/phase3_golden_event.py` — regenerates a fixed-seed reference event, emits PNG report
- `docs/phase3_acceptance_report.md` — risk-register → test-file mapping table
- `.gitignore` — add `outputs/` and `datasets/` if not already present
- `pyproject.toml` — add `matplotlib` to `[project.optional-dependencies].phase3-dev` (test/plot only)

**OUT OF SCOPE (DO NOT MODIFY):**
- Any `smig/` production module (see bugfix exception below)
- Frozen interfaces
- `scripts/validate_splits.py` — read-only

### Rules of Engagement
- **No feature changes to `smig/` production code.** If a regression test uncovers a bug, the owning phase is re-opened. **One-line bugfixes are permitted** ONLY with an explicit commit message of the form `phase3.6: bugfix for <risk-id>: <one-line rationale>`; anything more substantial escalates.
- **Slow vs fast marker discipline:** orchestrator runs, large Besançon moment tests, multi-second VBBL computations, resume-after-mocked-crash → `@pytest.mark.slow`. Fast CI runs `-m "not slow"`.
- **Tolerance discipline:** aggregate metrics (median, P99.5, integrated aperture, fractional thresholds) with explicit numeric tolerances. No "every pixel < 3σ" assertions anywhere.
- **Golden event script is a regeneration tool, not a test.** Emits PNG + text summary; does NOT assert pass/fail. `scripts/phase3_golden_event.py` is allowed to change under `scripts/`; acceptance checks `git diff --stat smig/` (not `scripts/`).
- **`outputs/` is gitignored.** Do NOT commit `outputs/phase3_golden_event.png`.
- **Headless CI:** `matplotlib.use("Agg")` at top of `phase3_golden_event.py`. Skip PNG-existence assertion if `DISPLAY` env var is unset AND the test environment has no writable `outputs/` dir.
- **Stop and ask before:** modifying any frozen interface, adding any dependency beyond `matplotlib` (already in `[phase3-dev]`), changing any non-test, non-script, non-docs file.

### Execution Tasks

1. **`test_scientific_pspl.py` — Risk 1 supporting:**
   - `test_peak_magnification`: `u0=1e-3` → peak A within 0.1% of `1/u0`
   - `test_baseline_asymptote`: `|t - t0| = 10·tE` → A within `1e-4` of 1.0
   - `test_symmetry`: `A(t0 + δ) == A(t0 - δ)` within `1e-12`
2. **`test_scientific_fspl.py` — Risks 1 + 6:**
   - `test_pspl_limit`: `z = u/ρ ≫ 1` → FSPL → PSPL within 0.1%
   - `test_finite_plateau`: `z ≪ 1` → matches Yoo B₀(0) within 0.1%
3. **`test_ld_policy.py` — Risk 6:**
   - `test_out_of_grid_strict`: `strict_ld_grid=True` + (Teff, log_g, [Fe/H]) outside Claret grid → `ClaretGridError`
   - `test_out_of_grid_fallback_provenance`: `strict_ld_grid=False` + out-of-grid → nearest-neighbor used AND returned `MicrolensingEvent.ld_fallback_used == True`
4. **`test_binary_suzuki2016.py` — Risk 1:**
   - Load 5 events from `suzuki2016_sample.json`
   - Compute magnification at published peak times via pinned VBBL
   - Assert peak magnification matches published values within 1e-3 relative error
   - On 2 non-caustic-crossing events: cross-check MulensModel via `pytest.importorskip("MulensModel")` to <1e-3
   - Full suite `@pytest.mark.slow`; one non-caustic-crossing event runs in fast CI
5. **`test_determinism_repo.py` — Risk 3:**
   - Two 8-event smoke `DatasetBuilder.build()` invocations with identical config into different output dirs
   - `np.testing.assert_array_equal` on all science-stamp datasets and label datasets across the two shard sets
   - Sorted-canonical manifest JSONs byte-equal
   - `@pytest.mark.slow`
6. **`test_split_validator_gate.py` — Risk 5:**
   - Build a 32-event smoke dataset
   - Run `scripts/validate_splits.py` as subprocess
   - Assert exit 0 AND no `"leakage"` or `"warning"` substring in stderr
   - `@pytest.mark.slow`
7. **`test_shard_atomicity.py` — Risk 4:**
   - Mock `ShardWriter.__exit__` to raise `SystemExit` mid-shard
   - Assert `.tmp` file is gone; the final HDF5 path does not exist; checkpoint shows only completed events
   - Resume with fresh `DatasetBuilder`; assert final dataset matches an uninterrupted run (decoded equality + sorted manifest equality)
8. **`test_memory_ramp_peak.py` — codifies Phase 2 memory invariant:**
   - Determine the expected ramp-size budget from Phase 2's `MultiAccumReadout` docstring: `ramp_bytes = 4 (float32) * detector_shape_0 * detector_shape_1 * n_reads`. Read `detector_shape` and `n_reads` from the smoke config.
   - `tracemalloc.start()` around one call to `SceneSimulator.simulate_event()`
   - Assert `peak_traced_allocations <= 2.5 * ramp_bytes` (2.5× allows for PSF stamp overhead; document the headroom in a comment)
   - Mark `@pytest.mark.integration` so small containers can skip cleanly
9. **`test_null_and_peak_binding_e2e.py` — end-to-end wrapper (public API only; imports from 3.3 tests via helper, does not duplicate assertions):**
   - Import `bind_event_to_source` and run the null + PSPL-peak tests through the full orchestrator path (one-event smoke build). Acts as an integration guard; module-level binding tests in 3.3 remain authoritative.
10. **`test_catalog_stats.py` — Risk 2:**
    - Load a large Besançon fixture (committed under `smig/catalogs/validation/fixtures/`, or skip if missing)
    - Compare sampled moments to published distributions within 2σ
    - `@pytest.mark.slow @pytest.mark.integration`; skip cleanly if fixture absent
11. **`scripts/phase3_golden_event.py`:**
    - Header comment documents fixed seed + fixed event parameters
    - `matplotlib.use("Agg")` before `pyplot` import
    - Regenerates magnification curve (500 points, ±3·tE), 5-epoch DIA stamp mosaic, light curve in e⁻/s
    - Writes `outputs/phase3_golden_event.png` (3-panel)
    - Prints text summary: measured vs expected peak A, `event_class`, `backend`, `backend_version`
12. **`docs/phase3_acceptance_report.md`** — table columns: `Risk ID | Risk | Test file(s) | Gate status | Notes`. Every risk register item maps to at least one test file.
13. **`.gitignore`** — add `outputs/` and `datasets/` if absent.
14. **`pyproject.toml`** — add `matplotlib` to `[project.optional-dependencies].phase3-dev`.

### Acceptance Criteria

- [ ] `pytest -v -m "not slow and not integration"` green (fast CI)
- [ ] `pytest -v` green (full repo suite — all prior + new, zero prior failures)
- [ ] `pytest smig/datasets/validation/test_scientific_pspl.py smig/datasets/validation/test_scientific_fspl.py smig/datasets/validation/test_ld_policy.py smig/datasets/validation/test_null_and_peak_binding_e2e.py -v` green
- [ ] `pytest smig/datasets/validation/ -v` green (slow tests included)
- [ ] `python scripts/phase3_golden_event.py` produces `outputs/phase3_golden_event.png` (skippable under headless CI without writable outputs)
- [ ] `test -f docs/phase3_acceptance_report.md` and it maps all 6 risk items to test files
- [ ] `grep -qE "^outputs/|^datasets/" .gitignore`
- [ ] `git diff --stat smig/` shows ZERO production-code changes (scripts/, docs/, .gitignore, pyproject.toml changes are allowed)

Run exactly:
```bash
pytest -v -m "not slow and not integration"
pytest -v
pytest smig/datasets/validation/test_scientific_pspl.py smig/datasets/validation/test_scientific_fspl.py smig/datasets/validation/test_ld_policy.py smig/datasets/validation/test_null_and_peak_binding_e2e.py -v
pytest smig/datasets/validation/ -v
python scripts/phase3_golden_event.py || echo "PNG gen skipped (likely headless CI)"
test -f docs/phase3_acceptance_report.md
grep -qE "^outputs/|^datasets/" .gitignore
git diff --stat smig/
```

After all pass: ✅ **Phase 3.6 complete. Phase 3 locked. Ready for Phase 4 (ML training).**

---

## Execution Order

Run prompts sequentially. **Do not start Phase N+1 until Phase N's acceptance criteria all pass.** The three hard freeze gates — `MicrolensingEvent` API at end of 3.2, dataset contract at end of 3.4, every cascaded interface — are the single most important protection against compounding errors across phases.

If a phase fails a gate, fix it in its owning phase, not downstream. Phase 3.6 permits narrow one-line bugfixes only; anything larger re-opens the owning phase.

### Recommended agent routing

| Phase | Design / architecture | Implementation |
|---|---|---|
| 3.1 | — | Sonnet 4.6 |
| 3.2 | **Opus 4.7 (plan mode)** for `docs/phase3_2_design.md` + `binary.py` | Sonnet 4.6 for `pspl.py`, `fspl.py`, `priors.py`, `limb_darkening.py`, tests |
| 3.3 | — | Sonnet 4.6 |
| 3.4 | — | Sonnet 4.6 |
| 3.5 | **Opus 4.7 (plan mode)** for `docs/phase3_5_orchestrator_design.md` | Sonnet 4.6 for generator/writer/checkpoint/worker/tests |
| 3.6 | — | Sonnet 4.6 |

Cost-constrained alternative: Opus only for `smig/microlensing/binary.py` and `docs/phase3_5_orchestrator_design.md`. Sonnet for everything else.
