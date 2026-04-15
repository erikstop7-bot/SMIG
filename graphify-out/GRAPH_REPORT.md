# Graph Report - .  (2026-04-15)

## Corpus Check
- 42 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 744 nodes · 2494 edges · 26 communities detected
- Extraction: 29% EXTRACTED · 71% INFERRED · 0% AMBIGUOUS · INFERRED: 1770 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 182 edges
2. `PSFConfig` - 112 edges
3. `GeometryConfig` - 105 edges
4. `ProvenanceRecord` - 103 edges
5. `H4RG10Detector` - 76 edges
6. `DIAConfig` - 72 edges
7. `STPSFProvider` - 71 edges
8. `IPCConfig` - 65 edges
9. `NonLinearityModel` - 64 edges
10. `ChargeDiffusionConfig` - 63 edges

## Surprising Connections (you probably didn't know these)
- `smig/optics/psf.py ================== Field-varying polychromatic PSF provider f` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Normalize an SCA identifier to canonical ``'SCA{n:02d}'`` format.      Accepts:` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Clamp each coordinate to ``[0, 1]`` and round to 4 decimal places.      Prevents` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Thread-safe bounded cache using an insertion-ordered LRU eviction policy.      E` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py
- `Field-varying polychromatic PSF provider for the Roman WFI.      Computes wavele` --uses--> `PSFConfig`  [INFERRED]
  smig\optics\psf.py → smig\config\optics_schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (96): BaseModel, Build a 2D Gaussian kernel, normalized so its sum equals 1.0.          The kerne, CrowdedFieldConfig, DIAConfig, PSFConfig, smig/config/optics_schemas.py ============================= Immutable, validated, Placeholder configuration for the CrowdedFieldRenderer rendering pipeline., Configuration for the crowded-field stamp-based image renderer.      Controls th (+88 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (105): _BoundedCache, _normalize_sca_id(), _quantize_field_position(), smig/optics/psf.py ================== Field-varying polychromatic PSF provider f, Clamp each coordinate to ``[0, 1]`` and round to 4 decimal places.      Prevents, Thread-safe bounded cache using an insertion-ordered LRU eviction policy.      E, Field-varying polychromatic PSF provider for the Roman WFI.      Computes wavele, Compute a normalized monochromatic PSF at a single wavelength.          The resu (+97 more)

### Community 2 - "Community 2"
Cohesion: 0.1
Nodes (99): ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffus, Apply charge diffusion and BFE to a charge image.          Applies static Gaus, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral c, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussi, Apply the brighter-fatter effect via iterative Jacobi redistribution., OneOverFNoise, 1/f (pink) correlated noise generator.      Generates spatially and temporally c (+91 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (56): CrowdedFieldRenderer, smig/rendering/crowding.py =========================== Phase 2 crowded-field sce, Render all catalog neighbors into a stamp centred on         *stamp_center_detec, Render a static crowded-field background from a neighbor star catalog.      The, _validate_catalog(), _make_catalog(), _make_psf(), psf() (+48 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (44): _make_readout_sim(), _make_valid_record(), small_cfg(), test_bfe_widens_psf(), test_chain_order_cd_before_ipc_noncommutative(), test_charge_diffusion_conservation(), test_config_sha256_determinism(), test_config_sha256_is_hex_string() (+36 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (29): DIAPipeline, _make_gaussian_kernel(), smig/rendering/dia.py ===================== Difference Image Analysis (DIA) pipe, Alard-Lupton fixed-kernel convolution matching (MVP).          Uses 3 spatially-, Dynamic central crop to science_stamp_size.          Crop boundaries are compute, MVP Difference Image Analysis pipeline.      Parameters     ----------     confi, Inverse-variance weighted coadd of baseline epochs in rate space.          Each, detector() (+21 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (44): _col_centroid(), _flux_total(), _make_psf(), _make_stamp(), psf(), smig/rendering/validation/test_source.py =======================================, Point source (unresolved): total rendered flux == flux_e within 0.1%., Point source at zero offset: centroid near stamp centre. (+36 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (16): test_derive_event_seed_deterministic_across_custom_namespace(), test_derive_event_seed_never_zero(), test_derive_stage_seed_never_zero(), test_detector_config_imports_unaffected(), test_domain_separation_event_vs_stage_default_namespaces(), test_psf_config_rejects_equal_wavelength_bounds(), test_psf_config_rejects_inverted_wavelength_range(), test_simulation_config_accepts_geometry_equal_to_context_stamp() (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (16): smig/sensor/persistence.py =========================== Two-component exponential, Two-component exponential persistence (residual image) model.      Tracks trappe, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning, ElectricalConfig, EnvironmentConfig (+8 more)

### Community 9 - "Community 9"
Cohesion: 0.1
Nodes (19): smig/sensor/validation/test_config_utils.py ====================================, SHA-256 of the default DetectorConfig must match the pinned canary value.      I, NonlinearityConfig.coefficients accepts list or tuple; both hash identically., IPCConfig must reject sca_id=0 (valid range is 1–18)., IPCConfig must reject sca_id=19 (valid range is 1–18)., IPCConfig must accept all valid sca_id values 1–18., load_detector_config must raise FileNotFoundError for a nonexistent path., load_detector_config must raise ValueError for an empty YAML file. (+11 more)

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (8): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py =======================================, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Paramete, # TODO: Memory optimization - slice specific neighborhood instead of, Find the lower grid index and fractional offset for interpolation.      Parame, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially-

### Community 11 - "Community 11"
Cohesion: 0.25
Nodes (7): smig/sensor/validation/test_integration.py =====================================, load_detector_config correctly parses smig/config/roman_wfi.yaml., process_event → ProvenanceTracker → sidecar round-trips as valid JSON., Full physics integration smoke test at 128×128 with all models active.      When, test_full_chain_integration(), test_load_detector_config_from_yaml(), test_physics_integration_128x128()

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (5): smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, _sanitize_numpy_types(), sanitize_rng_state(), smig/provenance/tracker.py ========================== Accumulates ProvenanceReco

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): derive_event_seed(), derive_stage_seed(), smig/config/seed.py =================== Deterministic, hierarchical seed derivat, Derive a reproducible seed for a single microlensing event.      Combines the ma, Derive a reproducible seed for a named pipeline stage within an event.      Take

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (3): get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ----

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (3): smig/sensor/noise/correlated.py ================================ Correlated nois, # TODO: Implement physical model — generate 1/f noise via FFT-based, # TODO: Implement physical model — sample a two-state Markov chain

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (2): smig/sensor/noise/cosmic_rays.py ================================= Clustered cos, # TODO: Implement physical model — sample hit positions, energies, and

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (1): smig/sensor/nonlinearity.py ============================ Polynomial detector non

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Inject 1/f correlated noise into an image.          Parameters         ---------

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Inject RTS noise into an image.          Parameters         ----------         i

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Inject cosmic-ray hits into a 2D image.          Parameters         ----------

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Inject cosmic-ray hits into a single read of a 3D MULTIACCUM ramp.          Inte

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Deposit a single cosmic-ray event at a specified location.          Deterministi

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Prevent analytic kernel from producing a negative centre pixel.          For t

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Sanitize numpy types in dict-form state; pass strings through unchanged.

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Validate *df* and return a clean copy.          Enforces         --------

## Knowledge Gaps
- **38 isolated node(s):** `Reject configs where the detector array is smaller than the DIA stamp.`, `smig/config/schemas.py ====================== Immutable, validated detector co`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (2 nodes): `.apply()`, `Inject 1/f correlated noise into an image.          Parameters         ---------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `Inject RTS noise into an image.          Parameters         ----------         i`, `.apply()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `.apply()`, `Inject cosmic-ray hits into a 2D image.          Parameters         ----------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `.inject_into_ramp()`, `Inject cosmic-ray hits into a single read of a 3D MULTIACCUM ramp.          Inte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `._inject_single_event()`, `Deposit a single cosmic-ray event at a specified location.          Deterministi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Prevent analytic kernel from producing a negative centre pixel.          For t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Sanitize numpy types in dict-form state; pass strings through unchanged.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Validate *df* and return a clean copy.          Enforces         --------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 2`, `Community 5`, `Community 8`, `Community 9`, `Community 11`, `Community 15`, `Community 16`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 22`?**
  _High betweenness centrality (0.363) - this node is a cross-community bridge._
- **Why does `PSFConfig` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **Why does `CrowdedFieldRenderer` connect `Community 3` to `Community 0`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Are the 179 inferred relationships involving `DetectorConfig` (e.g. with `PSFConfig` and `RenderingConfig`) actually correct?**
  _`DetectorConfig` has 179 INFERRED edges - model-reasoned connections that need verification._
- **Are the 109 inferred relationships involving `PSFConfig` (e.g. with `DetectorConfig` and `smig/config/validation/test_seed.py ===================================== Contra`) actually correct?**
  _`PSFConfig` has 109 INFERRED edges - model-reasoned connections that need verification._
- **Are the 102 inferred relationships involving `GeometryConfig` (e.g. with `smig/config/validation/test_seed.py ===================================== Contra` and `Enumerate a range of inputs and assert no seed is 0.`) actually correct?**
  _`GeometryConfig` has 102 INFERRED edges - model-reasoned connections that need verification._
- **Are the 100 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 100 INFERRED edges - model-reasoned connections that need verification._