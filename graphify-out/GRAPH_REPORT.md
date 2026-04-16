# Graph Report - .  (2026-04-15)

## Corpus Check
- 44 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 817 nodes · 3216 edges · 31 communities detected
- Extraction: 24% EXTRACTED · 76% INFERRED · 0% AMBIGUOUS · INFERRED: 2429 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 226 edges
2. `PSFConfig` - 167 edges
3. `DIAConfig` - 127 edges
4. `STPSFProvider` - 126 edges
5. `H4RG10Detector` - 126 edges
6. `SimulationConfig` - 117 edges
7. `RenderingConfig` - 102 edges
8. `CrowdedFieldConfig` - 102 edges
9. `GeometryConfig` - 101 edges
10. `ProvenanceRecord` - 93 edges

## Surprising Connections (you probably didn't know these)
- `smig/optics/psf.py ================== Field-varying polychromatic PSF provider f` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Normalize an SCA identifier to canonical ``'SCA{n:02d}'`` format.      Accepts:` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Clamp each coordinate to ``[0, 1]`` and round to 4 decimal places.      Prevents` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Thread-safe bounded cache using an insertion-ordered LRU eviction policy.      E` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Compute a normalized monochromatic PSF at a single wavelength.          The resu` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (149): DIAPipeline, Dynamic central crop to science_stamp_size.          Crop boundaries are compute, Build a 2D Gaussian kernel, normalized so its sum equals 1.0.          The kerne, MVP Difference Image Analysis pipeline.      Parameters     ----------     confi, Inverse-variance weighted coadd of baseline epochs in rate space.          Each, CrowdedFieldConfig, DIAConfig, PSFConfig (+141 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (118): ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffus, Apply charge diffusion and BFE to a charge image.          Applies static Gaus, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral c, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussi, Apply the brighter-fatter effect via iterative Jacobi redistribution., OneOverFNoise, 1/f (pink) correlated noise generator.      Generates spatially and temporally c (+110 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (83): cached_config(), default_config(), _estimate_sigma_arcsec(), _get_rss_mb(), smig/optics/validation/test_psf.py ==================================== Unit tes, PSFConfig with disk caching enabled in a temporary directory., STPSFProvider constructs without error from default PSFConfig., STPSFProvider constructs from a minimal PSFConfig. (+75 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (56): CrowdedFieldRenderer, smig/rendering/crowding.py =========================== Phase 2 crowded-field sce, Render all catalog neighbors into a stamp centred on         *stamp_center_detec, Render a static crowded-field background from a neighbor star catalog.      The, _validate_catalog(), _make_catalog(), _make_psf(), psf() (+48 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (44): _make_readout_sim(), _make_valid_record(), small_cfg(), test_bfe_widens_psf(), test_chain_order_cd_before_ipc_noncommutative(), test_charge_diffusion_conservation(), test_config_sha256_determinism(), test_config_sha256_is_hex_string() (+36 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (44): _col_centroid(), _flux_total(), _make_psf(), _make_stamp(), psf(), smig/rendering/validation/test_source.py =======================================, Point source (unresolved): total rendered flux == flux_e within 0.1%., Point source at zero offset: centroid near stamp centre. (+36 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (20): _BoundedCache, _normalize_sca_id(), _quantize_field_position(), smig/optics/psf.py ================== Field-varying polychromatic PSF provider f, Clamp each coordinate to ``[0, 1]`` and round to 4 decimal places.      Prevents, Thread-safe bounded cache using an insertion-ordered LRU eviction policy.      E, Compute a normalized monochromatic PSF at a single wavelength.          The resu, Compute a polychromatic, jitter-convolved PSF.          Assembles the polychroma (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (27): BaseModel, smig/config/optics_schemas.py ============================= Immutable, validated, smig/sensor/persistence.py =========================== Two-component exponential, Two-component exponential persistence (residual image) model.      Tracks trappe, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning (+19 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (14): detector(), dia_config(), _make_backgrounds(), _make_flat_epochs(), TestBuildReferenceShape, TestBuildReferenceValidation, TestDeterminism, TestExtractStampDynamicScaling (+6 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (10): _make_sim_config(), _make_source_params(), _make_timestamps(), sim_config(), simulator(), smoke_output(), TestDeterminism, TestInputValidation (+2 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (16): test_derive_event_seed_deterministic_across_custom_namespace(), test_derive_event_seed_never_zero(), test_derive_stage_seed_never_zero(), test_detector_config_imports_unaffected(), test_domain_separation_event_vs_stage_default_namespaces(), test_psf_config_rejects_equal_wavelength_bounds(), test_psf_config_rejects_inverted_wavelength_range(), test_simulation_config_accepts_geometry_equal_to_context_stamp() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.25
Nodes (8): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py =======================================, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Paramete, # TODO: Memory optimization - slice specific neighborhood instead of, Find the lower grid index and fractional offset for interpolation.      Parame, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially-

### Community 12 - "Community 12"
Cohesion: 0.38
Nodes (6): main(), _params_within_5pct(), Validate *manifest* for data leakage.  Return list of violation strings.      An, Parse arguments, validate manifest, print results, return exit code., Return ``True`` if every parameter in both dicts is within 5%% of the other., validate_manifest()

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): derive_event_seed(), derive_stage_seed(), smig/config/seed.py =================== Deterministic, hierarchical seed derivat, Derive a reproducible seed for a single microlensing event.      Combines the ma, Derive a reproducible seed for a named pipeline stage within an event.      Take

### Community 14 - "Community 14"
Cohesion: 0.53
Nodes (4): _count_filtered_neighbors(), _derive_event_seed(), _derive_stage_seed(), _generate_catalog()

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (4): smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, _sanitize_numpy_types(), sanitize_rng_state()

### Community 16 - "Community 16"
Cohesion: 0.4
Nodes (3): _make_gaussian_kernel(), smig/rendering/dia.py ===================== Difference Image Analysis (DIA) pipe, Alard-Lupton fixed-kernel convolution matching (MVP).          Uses 3 spatially-

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (3): smig/sensor/noise/correlated.py ================================ Correlated nois, # TODO: Implement physical model — generate 1/f noise via FFT-based, # TODO: Implement physical model — sample a two-state Markov chain

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): smig/rendering/source.py ======================== Phase 2 source-profile renderi

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Render a single source into *stamp* in-place.          Parameters         ------

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Inject RTS noise into an image.          Parameters         ----------         i

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Inject 1/f correlated noise into an image.          Parameters         ---------

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (2): test_full_chain_integration, test_load_detector_config_from_yaml

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): smig Package Init

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Prevent analytic kernel from producing a negative centre pixel.          For t

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Sanitize numpy types in dict-form state; pass strings through unchanged.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Validate *df* and return a clean copy.          Enforces         --------

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): DetectorOutput (re-exported)

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): EventOutput (re-exported)

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): get_peak_memory_mb

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): test_physics_integration_128x128 (skipped)

## Knowledge Gaps
- **48 isolated node(s):** `Return ``True`` if every parameter in both dicts is within 5%% of the other.`, `Validate *manifest* for data leakage.  Return list of violation strings.      An`, `Parse arguments, validate manifest, print results, return exit code.`, `smig Package Init`, `Reject configs where the detector array is smaller than the DIA stamp.` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (2 nodes): `source.py`, `smig/rendering/source.py ======================== Phase 2 source-profile renderi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `.render_source()`, `Render a single source into *stamp* in-place.          Parameters         ------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `Inject RTS noise into an image.          Parameters         ----------         i`, `.apply()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `.apply()`, `Inject 1/f correlated noise into an image.          Parameters         ---------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `test_full_chain_integration`, `test_load_detector_config_from_yaml`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `smig Package Init`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Prevent analytic kernel from producing a negative centre pixel.          For t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Sanitize numpy types in dict-form state; pass strings through unchanged.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Validate *df* and return a clean copy.          Enforces         --------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `DetectorOutput (re-exported)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `EventOutput (re-exported)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `get_peak_memory_mb`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `test_physics_integration_128x128 (skipped)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 1`, `Community 7`, `Community 8`, `Community 9`, `Community 16`, `Community 17`, `Community 20`, `Community 21`?**
  _High betweenness centrality (0.304) - this node is a cross-community bridge._
- **Why does `PSFConfig` connect `Community 0` to `Community 9`, `Community 2`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.203) - this node is a cross-community bridge._
- **Why does `CrowdedFieldRenderer` connect `Community 3` to `Community 0`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Are the 223 inferred relationships involving `DetectorConfig` (e.g. with `PSFConfig` and `RenderingConfig`) actually correct?**
  _`DetectorConfig` has 223 INFERRED edges - model-reasoned connections that need verification._
- **Are the 164 inferred relationships involving `PSFConfig` (e.g. with `DetectorConfig` and `smig/config/validation/test_seed.py ===================================== Contra`) actually correct?**
  _`PSFConfig` has 164 INFERRED edges - model-reasoned connections that need verification._
- **Are the 124 inferred relationships involving `DIAConfig` (e.g. with `DetectorConfig` and `smig/config/validation/test_seed.py ===================================== Contra`) actually correct?**
  _`DIAConfig` has 124 INFERRED edges - model-reasoned connections that need verification._
- **Are the 110 inferred relationships involving `STPSFProvider` (e.g. with `smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.` and `PSFConfig`) actually correct?**
  _`STPSFProvider` has 110 INFERRED edges - model-reasoned connections that need verification._