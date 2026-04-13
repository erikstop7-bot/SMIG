# Graph Report - .  (2026-04-12)

## Corpus Check
- 24 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 286 nodes · 1220 edges · 13 communities detected
- Extraction: 23% EXTRACTED · 77% INFERRED · 0% AMBIGUOUS · INFERRED: 940 edges (avg confidence: 0.5)
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
- `Two-component exponential persistence (residual image) model.      Tracks trappe` --uses--> `PersistenceConfig`  [INFERRED]
  smig\sensor\persistence.py → smig\config\schemas.py
- `smig/sensor/nonlinearity.py ============================ Polynomial detector non` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `Polynomial detector nonlinearity model.      Converts accumulated charge Q (elec` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `Apply the polynomial nonlinearity transfer function.          Parameters` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `smig/config/utils.py ==================== Config loading and canonical hashing u` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (34): OneOverFNoise, smig/sensor/noise/correlated.py ================================ Correlated nois, 1/f (pink) correlated noise generator.      Generates spatially and temporally c, Inject 1/f correlated noise into an image.          Parameters         ---------, # TODO: Implement physical model — generate 1/f noise via FFT-based, Random telegraph signal (RTS) noise generator.      Simulates discrete switching, Inject RTS noise into an image.          Parameters         ----------         i, # TODO: Implement physical model — sample a two-state Markov chain (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (29): ProvenanceRecord, smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, Immutable audit record for one simulated epoch of one microlensing event.      A, _sanitize_numpy_types(), sanitize_rng_state(), smig/sensor/validation/test_integration.py =====================================, load_detector_config correctly parses smig/config/roman_wfi.yaml. (+21 more)

### Community 2 - "Community 2"
Cohesion: 0.1
Nodes (29): NonLinearityModel, smig/sensor/nonlinearity.py ============================ Polynomial detector non, Polynomial detector nonlinearity model.      Converts accumulated charge Q (elec, Apply the polynomial nonlinearity transfer function.          Parameters, MultiAccumSimulator, smig/sensor/readout.py ======================= MULTIACCUM (up-the-ramp) readout, Estimate the count rate for each pixel via OLS along the ramp.          Uses ord, MULTIACCUM (up-the-ramp) readout simulator.      Builds a non-destructive read r (+21 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (28): ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffusio, Apply charge diffusion and BFE to a charge image.          Applies static Gaussi, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral cha, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussian, Apply the brighter-fatter effect via iterative Jacobi redistribution.          F, EventOutput, Multi-epoch event simulation result.      Note: ``frozen=True`` freezes attribut (+20 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (29): GeometryConfig, NonlinearityConfig, Focal-plane geometry of a single H4RG-10 SCA., Polynomial detector nonlinearity correction model.      Maps normalized charge $, smig/sensor/validation/test_config_utils.py ====================================, SHA-256 of the default DetectorConfig must match the pinned canary value.      I, NonlinearityConfig.coefficients accepts list or tuple; both hash identically., IPCConfig must reject sca_id=0 (valid range is 1–18). (+21 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (21): BaseModel, smig/sensor/persistence.py =========================== Two-component exponential, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning, ElectricalConfig, EnvironmentConfig (+13 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (18): FieldDependentIPC, smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I, Validate that a loaded IPC kernel has the expected shape.          Parameters, Apply IPC convolution to a charge image.          Uses ``scipy.signal.fftconvolv, Iterative Jansson-Van Cittert IPC deconvolution.          This method is for tes, Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spatia, Build or load a normalised 9x9 IPC kernel.          If ``config.ipc_kernel_path`, IPCConfig (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (8): All records are ProvenanceRecords with correct event_id and epoch_index., ClusteredCosmicRayInjector.apply() must reject 3D arrays with ValueError., Identical configs produce the same 64-char hash; different configs differ., A single 5-pixel cluster contributes 1 to cosmic_ray_hit_count., test_config_sha256_determinism(), test_cr_hit_count_is_events_not_pixels(), test_cr_injector_signature_2d_only(), test_process_event_provenance_records_are_valid()

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (7): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py ======================================= S, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Parameters, Find the lower grid index and fractional offset for interpolation.      Paramete, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially-va

### Community 9 - "Community 9"
Cohesion: 0.25
Nodes (8): _make_readout_sim(), Helper: build a MultiAccumSimulator with explicit parameters., simulate_ramp returns (ramp, sat_reads) with ramp shape (n_reads, ny, nx)., Zero-photon ramp: per-read dark increment mean ≈ dark_e_per_s * frame_time., Zero-signal, zero-dark ramp: spatial variance per read ≈ (cds/√2)²., test_dark_current_accumulation(), test_ramp_dimensions_and_timing(), test_read_noise_addition()

### Community 10 - "Community 10"
Cohesion: 0.5
Nodes (3): get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ----

### Community 11 - "Community 11"
Cohesion: 0.5
Nodes (4): _make_valid_record(), Helper: build a minimal valid ProvenanceRecord for drift tests., ProvenanceTracker raises ValueError when record git_commit is None     but the t, test_tracker_rejects_silent_metadata_drift()

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (1): Delegate to the module-level sanitize_rng_state function.

## Knowledge Gaps
- **22 isolated node(s):** `smig/config/schemas.py ====================== Immutable, validated detector conf`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.      Th`, `Configuration for the charge diffusion and brighter-fatter effect model.      Ex` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 12`** (1 nodes): `Delegate to the module-level sanitize_rng_state function.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.194) - this node is a cross-community bridge._
- **Why does `ProvenanceRecord` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `IPCConfig` connect `Community 6` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 86 inferred relationships involving `DetectorConfig` (e.g. with `smig/config/utils.py ==================== Config loading and canonical hashing u` and `Load and validate a DetectorConfig from a YAML file.      Parameters     -------`) actually correct?**
  _`DetectorConfig` has 86 INFERRED edges - model-reasoned connections that need verification._
- **Are the 63 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 63 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `H4RG10Detector` (e.g. with `smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.` and `ChargeDiffusionConfig`) actually correct?**
  _`H4RG10Detector` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `IPCConfig` (e.g. with `FieldDependentIPC` and `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I`) actually correct?**
  _`IPCConfig` has 61 INFERRED edges - model-reasoned connections that need verification._