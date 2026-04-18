# Graph Report - .  (2026-04-18)

## Corpus Check
- 63 files · ~57,091 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1272 nodes · 4845 edges · 42 communities detected
- Extraction: 25% EXTRACTED · 75% INFERRED · 0% AMBIGUOUS · INFERRED: 3644 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 312 edges
2. `PSFConfig` - 263 edges
3. `DIAConfig` - 192 edges
4. `STPSFProvider` - 183 edges
5. `H4RG10Detector` - 168 edges
6. `SimulationConfig` - 163 edges
7. `FiniteSourceRenderer` - 154 edges
8. `DIAPipeline` - 146 edges
9. `RenderingConfig` - 139 edges
10. `CrowdedFieldConfig` - 139 edges

## Surprising Connections (you probably didn't know these)
- `FiniteSourceRenderer` --uses--> `smig/rendering/validation/test_source.py =======================================`  [INFERRED]
  smig/rendering/source.py → smig\rendering\validation\test_source.py
- `IPCConfig` --uses--> `Build or load a normalised 9x9 IPC kernel.          If ``config.ipc_kernel_pat`  [INFERRED]
  smig/config/schemas.py → smig\sensor\ipc.py
- `IPCConfig` --uses--> `Validate that a loaded IPC kernel has the expected shape.          Parameters`  [INFERRED]
  smig/config/schemas.py → smig\sensor\ipc.py
- `DetectorConfig` --uses--> `smig/config/optics_schemas.py ============================= Immutable, validated`  [INFERRED]
  smig/config/schemas.py → smig\config\optics_schemas.py
- `DetectorConfig` --uses--> `smig/sensor/noise/correlated.py ================================ Correlated nois`  [INFERRED]
  smig/config/schemas.py → smig\sensor\noise\correlated.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (237): H4RG10Detector, DIAPipeline, Alard-Lupton fixed-kernel convolution matching (MVP).          Uses 3 spatially-, Dynamic central crop to science_stamp_size.          Crop boundaries are compute, Dynamic central crop to science_stamp_size.          Crop boundaries are compute, Build a 2D Gaussian kernel, normalized so its sum equals 1.0.          The kerne, Build a 2D Gaussian kernel, normalized so its sum equals 1.0.          The kerne, MVP Difference Image Analysis pipeline.      Parameters     ----------     confi (+229 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (182): BaseModel, ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffus, Apply charge diffusion and BFE to a charge image.          Applies static Gaus, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral c, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussi, Apply the brighter-fatter effect via iterative Jacobi redistribution., OneOverFNoise (+174 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (145): PSFConfig, Configuration for the WebbPSF-based point-spread function model.      Controls t, _BoundedCache, _normalize_sca_id(), _quantize_field_position(), smig/optics/psf.py ================== Field-varying polychromatic PSF provider f, Clamp each coordinate to ``[0, 1]`` and round to 4 decimal places.      Prevents, Clamp each coordinate to ``[0, 1]`` and round to 4 decimal places.      Prevents (+137 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (60): project_to_sca_dataframe(), smig/catalogs/adapter.py ========================= ProjectedStarTable adapter —, Project a list of StarRecords to a CrowdedFieldRenderer-compatible DataFrame., CatalogProvider, list_bands(), MissingColumnError, smig/catalogs/base.py ===================== Abstract base types for Phase 3 cata, Raised when a catalog file is missing required columns.      Parameters     ---- (+52 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (45): smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, _sanitize_numpy_types(), sanitize_rng_state(), test_sanitize_rng_state_rejects_non_dict(), _assert_fails(), _assert_passes(), _make_event() (+37 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (79): CrowdedFieldRenderer, smig/rendering/crowding.py =========================== Phase 2 crowded-field sce, Render all catalog neighbors into a stamp centred on         *stamp_center_detec, Return the number of catalog stars that pass the brightness-cap filter., Render a static crowded-field background from a neighbor star catalog.      The, _validate_catalog(), _make_catalog(), _make_psf() (+71 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (58): Render a single source into *stamp* in-place.          Parameters         ------, _col_centroid(), _flux_total(), _make_psf(), _make_stamp(), psf(), smig/rendering/validation/test_source.py =======================================, Point source (unresolved): total rendered flux == flux_e within 0.1%. (+50 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (17): _make_gaussian_kernel(), smig/rendering/dia.py ===================== Difference Image Analysis (DIA) pipe, Alard-Lupton fixed-kernel convolution matching (MVP).          Uses 3 spatially-, Inverse-variance weighted coadd of baseline epochs in rate space.          Each, detector(), dia_config(), _make_backgrounds(), _make_flat_epochs() (+9 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (32): smig/config/optics_schemas.py ============================= Immutable, validated, derive_event_seed(), derive_stage_seed(), smig/config/seed.py =================== Deterministic, hierarchical seed derivat, Derive a reproducible seed for a named pipeline stage within an event.      Take, Derive a reproducible seed for a single microlensing event.      Combines the ma, test_derive_event_seed_deterministic(), test_derive_event_seed_deterministic_across_custom_namespace() (+24 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (16): smig/sensor/persistence.py =========================== Two-component exponential, Two-component exponential persistence (residual image) model.      Tracks trappe, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning, ElectricalConfig, EnvironmentConfig (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (13): Tests for smig.catalogs.wcs — Galactic → SCA pixel projection., Field centre (l, b) must map to exactly (128.0, 128.0)., Field centre must map to (128, 128) for any (l, b) value., Total pixel displacement scales linearly with angular offset.      The Galactic, True angular separation using astropy., 0.11 arcsec offset in Galactic b → total pixel distance ≈ 1 px., 0.11 arcsec offset in Galactic l → total pixel distance ≈ 1 px., Total pixel distance = angular_sep / plate_scale for offsets up to 1 deg. (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (11): get_f146_zero_point(), mag_ab_to_electrons(), smig/catalogs/photometry.py ============================ AB-magnitude photometry, Return the F146 AB zero-point loaded from the YAML file.      Exposed for tests, Convert an AB magnitude to total integrated electrons over an exposure.      Thi, Tests for smig.catalogs.photometry — AB mag → electrons conversion., By definition of AB zero-point: ZP mag → 1 e⁻/s → exposure_s total., 1 mag fainter → flux ratio of 10^(1/2.5) ≈ 2.512 fewer electrons. (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (11): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py =======================================, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Paramete, # TODO: Memory optimization - slice specific neighborhood instead of, Find the lower grid index and fractional offset for interpolation.      Parame, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially- (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.2
Nodes (1): TestSmokeFullPipeline

### Community 14 - "Community 14"
Cohesion: 0.25
Nodes (1): TestProvenancePhase2Fields

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (3): get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ----

### Community 16 - "Community 16"
Cohesion: 0.5
Nodes (3): smig/sensor/noise/correlated.py ================================ Correlated nois, # TODO: Implement physical model — generate 1/f noise via FFT-based, # TODO: Implement physical model — sample a two-state Markov chain

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (2): smig/sensor/noise/cosmic_rays.py ================================= Clustered cos, # TODO: Implement physical model — sample hit positions, energies, and

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): smig/rendering/source.py ======================== Phase 2 source-profile renderi

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Validate *df* and return a clean copy.          Enforces         --------

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Prevent analytic kernel from producing a negative centre pixel.          For t

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Return all stars within a square FOV centred on ``(l_deg, b_deg)``.          Par

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Return the photometric band names available in this catalog.          Returns

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Sanitize numpy types in dict-form state; pass strings through unchanged.

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Return ``True`` if every parameter in both dicts is within 5%% of the other.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Validate *manifest* for data leakage.  Return list of violation strings.      An

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Parse arguments, validate manifest, print results, return exit code.

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Render a single source profile into a GalSim Image stamp.      Supports two rend

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Render a single source into *stamp* in-place.          Parameters         ------

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Validate *df* and return a clean copy.          Enforces         --------

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Render all catalog neighbors into a stamp centred on         *stamp_center_detec

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Derive a reproducible seed for a single microlensing event.      Combines the ma

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Derive a reproducible seed for a named pipeline stage within an event.      Take

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Immutable audit record for one simulated epoch of one microlensing event.      A

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Sanitize numpy types in dict-form state; pass strings through unchanged.

## Knowledge Gaps
- **160 isolated node(s):** `TestInvalidSplitLabels`, `scripts/test_validate_splits.py ================================ Regression test`, `Must not raise — failure is communicated via the return value.`, `A~B and B~C but A and C in different splits → leakage.`, `A (train) ~ B (val) ~ C (test): A, B, C form one component → violation.` (+155 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (2 nodes): `source.py`, `smig/rendering/source.py ======================== Phase 2 source-profile renderi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Validate *df* and return a clean copy.          Enforces         --------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Prevent analytic kernel from producing a negative centre pixel.          For t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Return all stars within a square FOV centred on ``(l_deg, b_deg)``.          Par`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Return the photometric band names available in this catalog.          Returns`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Sanitize numpy types in dict-form state; pass strings through unchanged.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Return ``True`` if every parameter in both dicts is within 5%% of the other.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Validate *manifest* for data leakage.  Return list of violation strings.      An`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Parse arguments, validate manifest, print results, return exit code.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Render a single source profile into a GalSim Image stamp.      Supports two rend`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Render a single source into *stamp* in-place.          Parameters         ------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Validate *df* and return a clean copy.          Enforces         --------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Render all catalog neighbors into a stamp centred on         *stamp_center_detec`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Derive a reproducible seed for a single microlensing event.      Combines the ma`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Derive a reproducible seed for a named pipeline stage within an event.      Take`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Immutable audit record for one simulated epoch of one microlensing event.      A`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `Sanitize numpy types in dict-form state; pass strings through unchanged.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 1`, `Community 2`, `Community 7`, `Community 8`, `Community 9`, `Community 13`, `Community 14`, `Community 16`, `Community 17`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Why does `smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `PSFConfig` connect `Community 2` to `Community 0`, `Community 1`, `Community 8`, `Community 13`, `Community 14`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Are the 309 inferred relationships involving `DetectorConfig` (e.g. with `EventSceneOutput` and `SceneSimulator`) actually correct?**
  _`DetectorConfig` has 309 INFERRED edges - model-reasoned connections that need verification._
- **Are the 260 inferred relationships involving `PSFConfig` (e.g. with `TestSmokeFullPipeline` and `TestDeterminism`) actually correct?**
  _`PSFConfig` has 260 INFERRED edges - model-reasoned connections that need verification._
- **Are the 189 inferred relationships involving `DIAConfig` (e.g. with `DIAPipeline` and `smig/rendering/dia.py ===================== Difference Image Analysis (DIA) pipe`) actually correct?**
  _`DIAConfig` has 189 INFERRED edges - model-reasoned connections that need verification._
- **Are the 166 inferred relationships involving `STPSFProvider` (e.g. with `EventSceneOutput` and `SceneSimulator`) actually correct?**
  _`STPSFProvider` has 166 INFERRED edges - model-reasoned connections that need verification._