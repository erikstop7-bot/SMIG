# Graph Report - .  (2026-04-12)

## Corpus Check
- Corpus is ~28,097 words - fits in a single context window. You may not need a graph.

## Summary
- 380 nodes · 1319 edges · 39 communities detected
- Extraction: 27% EXTRACTED · 73% INFERRED · 0% AMBIGUOUS · INFERRED: 969 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 89 edges
2. `ProvenanceRecord` - 66 edges
3. `H4RG10Detector` - 65 edges
4. `IPCConfig` - 64 edges
5. `NonLinearityModel` - 63 edges
6. `ChargeDiffusionConfig` - 62 edges
7. `GeometryConfig` - 61 edges
8. `NonlinearityConfig` - 61 edges
9. `FieldDependentIPC` - 61 edges
10. `ClusteredCosmicRayInjector` - 61 edges

## Surprising Connections (you probably didn't know these)
- `smig/sensor/charge_diffusion.py ================================ Charge diffusio` --uses--> `ChargeDiffusionConfig`  [INFERRED]
  smig\sensor\charge_diffusion.py → smig\config\schemas.py
- `Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussian` --uses--> `ChargeDiffusionConfig`  [INFERRED]
  smig\sensor\charge_diffusion.py → smig\config\schemas.py
- `Apply the brighter-fatter effect via iterative Jacobi redistribution.          F` --uses--> `ChargeDiffusionConfig`  [INFERRED]
  smig\sensor\charge_diffusion.py → smig\config\schemas.py
- `Apply charge diffusion and BFE to a charge image.          Applies static Gaussi` --uses--> `ChargeDiffusionConfig`  [INFERRED]
  smig\sensor\charge_diffusion.py → smig\config\schemas.py
- `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I` --uses--> `IPCConfig`  [INFERRED]
  smig\sensor\ipc.py → smig\config\schemas.py

## Hyperedges (group relationships)
- **H4RG10 Fixed Signal Chain** — smig_v2_phase1_H4RG10Detector, smig_v2_phase1_ChargeDiffusionModel, smig_v2_phase1_FieldDependentIPC, smig_v2_phase1_DynamicPersistence, smig_v2_phase1_NonLinearityModel, smig_v2_phase1_MultiAccumSimulator, smig_v2_phase1_ClusteredCosmicRayInjector [EXTRACTED 1.00]
- **Stage A Classifier Architecture** — smig_v2_phases2to6_SpatiotemporalTrigger, smig_v2_phases2to6_NeuralCDE, smig_v2_phases2to6_EfficientNetEncoder, smig_v2_phases2to6_TriggerCalibrator [EXTRACTED 1.00]
- **Reproducibility Triad** — smig_v2_phases2to6_ReproducibilityContract, smig_v2_phase1_ProvenanceTracker, smig_v2_phase1_DetectorConfig, smig_v2_phases2to6_SnakemakeDVC [EXTRACTED 0.95]
- **Fixed Signal Chain: Charge Diffusion -> IPC -> Persistence -> Readout -> Noise** — detector_H4RG10Detector, charge_diffusion_ChargeDiffusionModel, ipc_FieldDependentIPC, persistence_DynamicPersistence, nonlinearity_NonLinearityModel [EXTRACTED 0.97]
- **DetectorConfig Composed from Sub-Config Models** — schemas_DetectorConfig, schemas_GeometryConfig, schemas_ElectricalConfig, schemas_ReadoutConfig, schemas_IPCConfig, schemas_PersistenceConfig, schemas_NonlinearityConfig, schemas_NoiseConfig [EXTRACTED 1.00]
- **Provenance Integrity: ProvenanceRecord + sanitize_rng_state + ProvenanceTracker** — provenance_schema_ProvenanceRecord, provenance_schema_sanitize_rng_state, provenance_tracker_ProvenanceTracker [EXTRACTED 0.95]
- **Noise leaf modules share star-topology leaf constraint** — correlated_OneOverFNoise, correlated_RTSNoise, cosmic_rays_ClusteredCosmicRayInjector, claude_md_star_topology_constraint [EXTRACTED 0.95]
- **MultiAccum ramp pipeline: simulate_ramp -> fit_slope -> saturation test** — readout_simulate_ramp, readout_fit_slope, test_unit_saturation_mask, readout_MultiAccumSimulator [INFERRED 0.85]
- **IPC calibration pipeline: generate -> load -> interpolate** — calibration_generate_synthetic_ipc_hdf5, calibration_load_interpolated_kernel, calibration_find_bracket [EXTRACTED 0.95]

## Communities

### Community 0 - "Physics Engine Core"
Cohesion: 0.24
Nodes (70): ChargeDiffusionModel, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral cha, ClusteredCosmicRayInjector, DetectorOutput, EventOutput, H4RG10Detector, FieldDependentIPC, Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spatia (+62 more)

### Community 1 - "Noise Module Source Files"
Cohesion: 0.05
Nodes (45): OneOverFNoise, smig/sensor/noise/correlated.py ================================ Correlated nois, 1/f (pink) correlated noise generator.      Generates spatially and temporally c, Inject 1/f correlated noise into an image.          Parameters         ---------, # TODO: Implement physical model — generate 1/f noise via FFT-based, Random telegraph signal (RTS) noise generator.      Simulates discrete switching, Inject RTS noise into an image.          Parameters         ----------         i, # TODO: Implement physical model — sample a two-state Markov chain (+37 more)

### Community 2 - "Unit Test Suite"
Cohesion: 0.04
Nodes (43): _make_readout_sim(), _make_valid_record(), small_cfg(), test_bfe_widens_psf(), test_chain_order_cd_before_ipc_noncommutative(), test_charge_diffusion_conservation(), test_config_sha256_determinism(), test_config_sha256_is_hex_string() (+35 more)

### Community 3 - "Architecture Overview Docs"
Cohesion: 0.06
Nodes (35): ChargeDiffusionModel + BFE, ClusteredCosmicRayInjector, DetectorConfig (Pydantic v2), DynamicPersistence Module, FieldDependentIPC Module, H4RG10Detector Orchestrator, HDF5 Field-Dependent IPC Kernel Loader, MultiAccumSimulator (+27 more)

### Community 4 - "Detector Orchestrator"
Cohesion: 0.09
Nodes (29): ChargeDiffusionModel, DetectorOutput, EventOutput, H4RG10Detector, FieldDependentIPC, get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ---- (+21 more)

### Community 5 - "Persistence Module"
Cohesion: 0.11
Nodes (16): BaseModel, smig/sensor/persistence.py =========================== Two-component exponential, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning, ElectricalConfig, EnvironmentConfig (+8 more)

### Community 6 - "Config and Integration Tests"
Cohesion: 0.22
Nodes (9): NumPy/JSON serialization trap guidance, YAML loader robustness tests, test_full_chain_integration, test_load_detector_config_from_yaml, Phase C input guard tests, process_epoch provenance tests, process_epoch shape and dtype tests, process_event shape and provenance tests (+1 more)

### Community 7 - "IPC Calibration Pipeline"
Cohesion: 0.29
Nodes (7): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py ======================================= S, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Parameters, Find the lower grid index and fractional offset for interpolation.      Paramete, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially-va

### Community 8 - "Integration Test Suite"
Cohesion: 0.25
Nodes (7): smig/sensor/validation/test_integration.py =====================================, load_detector_config correctly parses smig/config/roman_wfi.yaml., process_event → ProvenanceTracker → sidecar round-trips as valid JSON., Full physics integration smoke test at 128×128 with all models active.      When, test_full_chain_integration(), test_load_detector_config_from_yaml(), test_physics_integration_128x128()

### Community 9 - "Provenance Schema"
Cohesion: 0.33
Nodes (5): smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, _sanitize_numpy_types(), sanitize_rng_state(), smig/provenance/tracker.py ========================== Accumulates ProvenanceReco

### Community 10 - "Architectural Constraints & Readout"
Cohesion: 0.33
Nodes (7): 32 GB memory hard limit constraint, Star topology architectural constraint, MultiAccumSimulator, Architectural Note: one-way NL dependency in readout, fit_slope(), simulate_ramp(), Saturation mask threshold tests

### Community 11 - "Charge Diffusion Methods"
Cohesion: 0.33
Nodes (3): Apply charge diffusion and BFE to a charge image.          Applies static Gaussi, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussian, Apply the brighter-fatter effect via iterative Jacobi redistribution.          F

### Community 12 - "IPC Kernel Validation"
Cohesion: 0.4
Nodes (2): Validate that a loaded IPC kernel has the expected shape.          Parameters, Build or load a normalised 9x9 IPC kernel.          If ``config.ipc_kernel_path`

### Community 13 - "Noise Leaf Modules"
Cohesion: 0.5
Nodes (5): OneOverFNoise, RTSNoise, ClusteredCosmicRayInjector, inject_into_ramp() (NotImplemented), _inject_single_event() (NotImplemented)

### Community 14 - "IPC HDF5 Functions"
Cohesion: 0.67
Nodes (1): load_interpolated_kernel()

### Community 15 - "Provenance Sidecar Write"
Cohesion: 1.0
Nodes (1): Atomically serialise all accumulated records to a JSON sidecar file.          Th

### Community 16 - "Provenance Record Append"
Cohesion: 1.0
Nodes (1): Append one epoch's provenance record to the in-memory accumulator.          Para

### Community 17 - "Provenance Record Count"
Cohesion: 1.0
Nodes (1): Return the number of records accumulated so far.

### Community 18 - "Charge Diffusion Source"
Cohesion: 1.0
Nodes (1): smig/sensor/charge_diffusion.py ================================ Charge diffusio

### Community 19 - "IPC Source File"
Cohesion: 1.0
Nodes (1): smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I

### Community 20 - "IPC Apply Method"
Cohesion: 1.0
Nodes (1): Apply IPC convolution to a charge image.          Uses ``scipy.signal.fftconvolv

### Community 21 - "IPC Deconvolution"
Cohesion: 1.0
Nodes (1): Iterative Jansson-Van Cittert IPC deconvolution.          This method is for tes

### Community 22 - "Nonlinearity Source"
Cohesion: 1.0
Nodes (1): smig/sensor/nonlinearity.py ============================ Polynomial detector non

### Community 23 - "Nonlinearity Apply"
Cohesion: 1.0
Nodes (1): Apply the polynomial nonlinearity transfer function.          Parameters

### Community 24 - "Readout Source"
Cohesion: 1.0
Nodes (1): smig/sensor/readout.py ======================= MULTIACCUM (up-the-ramp) readout

### Community 25 - "Ramp Slope Fitting"
Cohesion: 1.0
Nodes (1): Estimate the count rate for each pixel via OLS along the ramp.          Uses ord

### Community 26 - "Ramp Simulation"
Cohesion: 1.0
Nodes (1): Build a 3D up-the-ramp sample cube.          The photon signal (``ideal_image_e`

### Community 27 - "Config Hash and Type Tests"
Cohesion: 1.0
Nodes (2): Config SHA-256 canary hash test, NonlinearityConfig list vs tuple normalization test

### Community 28 - "Signal Chain Order Verification"
Cohesion: 1.0
Nodes (2): Fixed signal chain order: CD->IPC->Persistence->MULTIACCUM->Noise, test_chain_order_cd_before_ipc_noncommutative

### Community 29 - "Previous Graph Metadata"
Cohesion: 1.0
Nodes (2): 13-community graph structure, Graph god nodes: DetectorConfig, ProvenanceRecord, H4RG10Detector

### Community 30 - "RNG Sanitization Helper"
Cohesion: 1.0
Nodes (1): Delegate to the module-level sanitize_rng_state function.

### Community 31 - "Package Init"
Cohesion: 1.0
Nodes (1): smig Package Init

### Community 32 - "DetectorOutput Export"
Cohesion: 1.0
Nodes (1): DetectorOutput (re-exported)

### Community 33 - "EventOutput Export"
Cohesion: 1.0
Nodes (1): EventOutput (re-exported)

### Community 34 - "IPC SCA Boundary Tests"
Cohesion: 1.0
Nodes (1): IPCConfig SCA ID boundary tests

### Community 35 - "Physics Integration Placeholder"
Cohesion: 1.0
Nodes (1): test_physics_integration_128x128 (skipped)

### Community 36 - "Detector Construction Test"
Cohesion: 1.0
Nodes (1): test_detector_construction

### Community 37 - "IPC Flux Conservation Test"
Cohesion: 1.0
Nodes (1): test_ipc_flux_conservation

### Community 38 - "BFE PSF Widening Test"
Cohesion: 1.0
Nodes (1): test_bfe_widens_psf

## Knowledge Gaps
- **64 isolated node(s):** `smig/config/schemas.py ====================== Immutable, validated detector conf`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.      Th`, `Configuration for the charge diffusion and brighter-fatter effect model.      Ex` (+59 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Provenance Sidecar Write`** (2 nodes): `.write_sidecar()`, `Atomically serialise all accumulated records to a JSON sidecar file.          Th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Provenance Record Append`** (2 nodes): `.append_record()`, `Append one epoch's provenance record to the in-memory accumulator.          Para`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Provenance Record Count`** (2 nodes): `.__len__()`, `Return the number of records accumulated so far.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Charge Diffusion Source`** (2 nodes): `charge_diffusion.py`, `smig/sensor/charge_diffusion.py ================================ Charge diffusio`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `IPC Source File`** (2 nodes): `ipc.py`, `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `IPC Apply Method`** (2 nodes): `.apply()`, `Apply IPC convolution to a charge image.          Uses ``scipy.signal.fftconvolv`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `IPC Deconvolution`** (2 nodes): `.deconvolve()`, `Iterative Jansson-Van Cittert IPC deconvolution.          This method is for tes`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Nonlinearity Source`** (2 nodes): `nonlinearity.py`, `smig/sensor/nonlinearity.py ============================ Polynomial detector non`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Nonlinearity Apply`** (2 nodes): `.apply()`, `Apply the polynomial nonlinearity transfer function.          Parameters`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Readout Source`** (2 nodes): `readout.py`, `smig/sensor/readout.py ======================= MULTIACCUM (up-the-ramp) readout`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ramp Slope Fitting`** (2 nodes): `.fit_slope()`, `Estimate the count rate for each pixel via OLS along the ramp.          Uses ord`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ramp Simulation`** (2 nodes): `.simulate_ramp()`, `Build a 3D up-the-ramp sample cube.          The photon signal (``ideal_image_e``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config Hash and Type Tests`** (2 nodes): `Config SHA-256 canary hash test`, `NonlinearityConfig list vs tuple normalization test`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Signal Chain Order Verification`** (2 nodes): `Fixed signal chain order: CD->IPC->Persistence->MULTIACCUM->Noise`, `test_chain_order_cd_before_ipc_noncommutative`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Previous Graph Metadata`** (2 nodes): `13-community graph structure`, `Graph god nodes: DetectorConfig, ProvenanceRecord, H4RG10Detector`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `RNG Sanitization Helper`** (1 nodes): `Delegate to the module-level sanitize_rng_state function.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Package Init`** (1 nodes): `smig Package Init`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `DetectorOutput Export`** (1 nodes): `DetectorOutput (re-exported)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `EventOutput Export`** (1 nodes): `EventOutput (re-exported)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `IPC SCA Boundary Tests`** (1 nodes): `IPCConfig SCA ID boundary tests`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Physics Integration Placeholder`** (1 nodes): `test_physics_integration_128x128 (skipped)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Detector Construction Test`** (1 nodes): `test_detector_construction`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `IPC Flux Conservation Test`** (1 nodes): `test_ipc_flux_conservation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `BFE PSF Widening Test`** (1 nodes): `test_bfe_widens_psf`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Noise Module Source Files` to `Physics Engine Core`, `Integration Test Suite`, `Detector Orchestrator`, `Persistence Module`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Why does `Compute the SHA-256 fingerprint of a DetectorConfig.      Uses ``model_dump_json` connect `Detector Orchestrator` to `Noise Module Source Files`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 86 inferred relationships involving `DetectorConfig` (e.g. with `smig/config/utils.py ==================== Config loading and canonical hashing u` and `Load and validate a DetectorConfig from a YAML file.      Parameters     -------`) actually correct?**
  _`DetectorConfig` has 86 INFERRED edges - model-reasoned connections that need verification._
- **Are the 63 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 63 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `H4RG10Detector` (e.g. with `ChargeDiffusionConfig` and `DetectorConfig`) actually correct?**
  _`H4RG10Detector` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `IPCConfig` (e.g. with `FieldDependentIPC` and `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I`) actually correct?**
  _`IPCConfig` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `NonLinearityModel` (e.g. with `DetectorOutput` and `EventOutput`) actually correct?**
  _`NonLinearityModel` has 59 INFERRED edges - model-reasoned connections that need verification._