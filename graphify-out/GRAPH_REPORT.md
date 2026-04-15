# Graph Report - .  (2026-04-15)

## Corpus Check
- 30 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 360 nodes · 1449 edges · 23 communities detected
- Extraction: 24% EXTRACTED · 76% INFERRED · 0% AMBIGUOUS · INFERRED: 1095 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 121 edges
2. `GeometryConfig` - 79 edges
3. `ProvenanceRecord` - 67 edges
4. `H4RG10Detector` - 66 edges
5. `IPCConfig` - 65 edges
6. `NonLinearityModel` - 64 edges
7. `ChargeDiffusionConfig` - 63 edges
8. `NonlinearityConfig` - 63 edges
9. `FieldDependentIPC` - 62 edges
10. `ClusteredCosmicRayInjector` - 62 edges

## Surprising Connections (you probably didn't know these)
- `smig/config/optics_schemas.py ============================= Immutable, validated` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\optics_schemas.py → smig\config\schemas.py
- `Configuration for the WebbPSF-based point-spread function model.      Controls t` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\optics_schemas.py → smig\config\schemas.py
- `Placeholder configuration for the CrowdedFieldRenderer rendering pipeline.` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\optics_schemas.py → smig\config\schemas.py
- `Configuration for the crowded-field stamp-based image renderer.      Controls th` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\optics_schemas.py → smig\config\schemas.py
- `Configuration for the Difference Image Analysis (DIA) pipeline.      Controls th` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\optics_schemas.py → smig\config\schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.2
Nodes (73): ChargeDiffusionModel, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral c, ClusteredCosmicRayInjector, DetectorOutput, EventOutput, H4RG10Detector, FieldDependentIPC, Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spat (+65 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (53): CrowdedFieldConfig, DIAConfig, PSFConfig, smig/config/optics_schemas.py ============================= Immutable, validated, Placeholder configuration for the CrowdedFieldRenderer rendering pipeline., Configuration for the crowded-field stamp-based image renderer.      Controls th, Configuration for the Difference Image Analysis (DIA) pipeline.      Controls th, Top-level immutable configuration for a Phase 2 SMIG simulation run.      Compos (+45 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (44): _make_readout_sim(), _make_valid_record(), small_cfg(), test_bfe_widens_psf(), test_chain_order_cd_before_ipc_noncommutative(), test_charge_diffusion_conservation(), test_config_sha256_determinism(), test_config_sha256_is_hex_string() (+36 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (27): OneOverFNoise, smig/sensor/noise/correlated.py ================================ Correlated nois, 1/f (pink) correlated noise generator.      Generates spatially and temporally c, Inject 1/f correlated noise into an image.          Parameters         ---------, # TODO: Implement physical model — generate 1/f noise via FFT-based, Random telegraph signal (RTS) noise generator.      Simulates discrete switching, Inject RTS noise into an image.          Parameters         ----------         i, # TODO: Implement physical model — sample a two-state Markov chain (+19 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (28): GeometryConfig, Focal-plane geometry of a single H4RG-10 SCA., smig/sensor/validation/test_config_utils.py ====================================, SHA-256 of the default DetectorConfig must match the pinned canary value.      I, NonlinearityConfig.coefficients accepts list or tuple; both hash identically., IPCConfig must reject sca_id=0 (valid range is 1–18)., IPCConfig must reject sca_id=19 (valid range is 1–18)., IPCConfig must accept all valid sca_id values 1–18. (+20 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (16): BaseModel, smig/sensor/persistence.py =========================== Two-component exponential, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning, ElectricalConfig, EnvironmentConfig (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (8): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py =======================================, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Paramete, # TODO: Memory optimization - slice specific neighborhood instead of, Find the lower grid index and fractional offset for interpolation.      Parame, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially-

### Community 7 - "Community 7"
Cohesion: 0.33
Nodes (5): smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, _sanitize_numpy_types(), sanitize_rng_state(), smig/provenance/tracker.py ========================== Accumulates ProvenanceReco

### Community 8 - "Community 8"
Cohesion: 0.33
Nodes (5): derive_event_seed(), derive_stage_seed(), smig/config/seed.py =================== Deterministic, hierarchical seed derivat, Derive a reproducible seed for a single microlensing event.      Combines the ma, Derive a reproducible seed for a named pipeline stage within an event.      Take

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (3): Apply charge diffusion and BFE to a charge image.          Applies static Gaus, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussi, Apply the brighter-fatter effect via iterative Jacobi redistribution.

### Community 10 - "Community 10"
Cohesion: 0.4
Nodes (2): Validate that a loaded IPC kernel has the expected shape.          Parameters, Build or load a normalised 9x9 IPC kernel.          If ``config.ipc_kernel_pat

### Community 11 - "Community 11"
Cohesion: 0.5
Nodes (3): get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ----

### Community 12 - "Community 12"
Cohesion: 0.67
Nodes (1): smig/sensor/nonlinearity.py ============================ Polynomial detector non

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): Append one epoch's provenance record to the in-memory accumulator.          Para

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Atomically serialise all accumulated records to a JSON sidecar file.          Th

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Return the number of records accumulated so far.

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): smig/sensor/charge_diffusion.py ================================ Charge diffus

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Apply IPC convolution to a charge image.          Uses ``scipy.signal.fftconvo

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Iterative Jansson-Van Cittert IPC deconvolution.          This method is for t

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Apply the polynomial nonlinearity transfer function.          Parameters

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Prevent analytic kernel from producing a negative centre pixel.          For t

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Sanitize numpy types in dict-form state; pass strings through unchanged.

## Knowledge Gaps
- **29 isolated node(s):** `Reject configs where the detector array is smaller than the DIA stamp.`, `smig/config/schemas.py ====================== Immutable, validated detector co`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 13`** (2 nodes): `.append_record()`, `Append one epoch's provenance record to the in-memory accumulator.          Para`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `.write_sidecar()`, `Atomically serialise all accumulated records to a JSON sidecar file.          Th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `.__len__()`, `Return the number of records accumulated so far.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `charge_diffusion.py`, `smig/sensor/charge_diffusion.py ================================ Charge diffus`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `ipc.py`, `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `.apply()`, `Apply IPC convolution to a charge image.          Uses ``scipy.signal.fftconvo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `.deconvolve()`, `Iterative Jansson-Van Cittert IPC deconvolution.          This method is for t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `.apply()`, `Apply the polynomial nonlinearity transfer function.          Parameters`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Prevent analytic kernel from producing a negative centre pixel.          For t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Sanitize numpy types in dict-form state; pass strings through unchanged.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.306) - this node is a cross-community bridge._
- **Why does `GeometryConfig` connect `Community 4` to `Community 0`, `Community 1`, `Community 5`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `ProvenanceRecord` connect `Community 0` to `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 13`, `Community 14`, `Community 15`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 118 inferred relationships involving `DetectorConfig` (e.g. with `PSFConfig` and `RenderingConfig`) actually correct?**
  _`DetectorConfig` has 118 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `GeometryConfig` (e.g. with `smig/config/validation/test_seed.py ===================================== Contra` and `Enumerate a range of inputs and assert no seed is 0.`) actually correct?**
  _`GeometryConfig` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 64 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `H4RG10Detector` (e.g. with `smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.` and `ChargeDiffusionConfig`) actually correct?**
  _`H4RG10Detector` has 61 INFERRED edges - model-reasoned connections that need verification._