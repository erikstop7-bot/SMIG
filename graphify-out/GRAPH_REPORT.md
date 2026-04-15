# Graph Report - .  (2026-04-15)

## Corpus Check
- 26 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 292 nodes · 1241 edges · 15 communities detected
- Extraction: 23% EXTRACTED · 77% INFERRED · 0% AMBIGUOUS · INFERRED: 957 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 90 edges
2. `ProvenanceRecord` - 67 edges
3. `H4RG10Detector` - 66 edges
4. `IPCConfig` - 65 edges
5. `NonLinearityModel` - 64 edges
6. `ChargeDiffusionConfig` - 63 edges
7. `NonlinearityConfig` - 63 edges
8. `GeometryConfig` - 62 edges
9. `FieldDependentIPC` - 62 edges
10. `ClusteredCosmicRayInjector` - 62 edges

## Surprising Connections (you probably didn't know these)
- `Two-component exponential persistence (residual image) model.      Tracks trappe` --uses--> `PersistenceConfig`  [INFERRED]
  smig\sensor\persistence.py → smig\config\schemas.py
- `Polynomial detector nonlinearity model.      Converts accumulated charge Q (elec` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `Apply the polynomial nonlinearity transfer function.          Parameters` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `smig/config/utils.py ==================== Config loading and canonical hashing u` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py
- `Load and validate a DetectorConfig from a YAML file.      Parameters     -------` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (43): smig/sensor/noise/correlated.py ================================ Correlated nois, # TODO: Implement physical model — generate 1/f noise via FFT-based, # TODO: Implement physical model — sample a two-state Markov chain, smig/sensor/noise/cosmic_rays.py ================================= Clustered cos, # TODO: Implement physical model — sample hit positions, energies, and, smig/sensor/nonlinearity.py ============================ Polynomial detector non, Saturation flagging threshold in electrons.          This is ``saturation_flag_t, DetectorConfig (+35 more)

### Community 1 - "Community 1"
Cohesion: 0.1
Nodes (30): NonLinearityModel, Polynomial detector nonlinearity model.      Converts accumulated charge Q (elec, Apply the polynomial nonlinearity transfer function.          Parameters, MultiAccumSimulator, smig/sensor/readout.py ======================= MULTIACCUM (up-the-ramp) readout, Estimate the count rate for each pixel via OLS along the ramp.          Uses ord, MULTIACCUM (up-the-ramp) readout simulator.      Builds a non-destructive read r, Build a 3D up-the-ramp sample cube.          The photon signal (``ideal_image_e` (+22 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (24): OneOverFNoise, 1/f (pink) correlated noise generator.      Generates spatially and temporally c, Inject 1/f correlated noise into an image.          Parameters         ---------, Random telegraph signal (RTS) noise generator.      Simulates discrete switching, Inject RTS noise into an image.          Parameters         ----------         i, RTSNoise, DetectorOutput, EventOutput (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (21): BaseModel, smig/sensor/persistence.py =========================== Two-component exponential, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning, ElectricalConfig, EnvironmentConfig (+13 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (22): ProvenanceRecord, smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, Immutable audit record for one simulated epoch of one microlensing event.      A, _sanitize_numpy_types(), sanitize_rng_state(), ValueError on NaN anywhere in ideal_image_e., 16×16 DetectorConfig for fast unit tests. (+14 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (20): FieldDependentIPC, smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance, Validate that a loaded IPC kernel has the expected shape.          Parameters, Apply IPC convolution to a charge image.          Uses ``scipy.signal.fftconvo, Iterative Jansson-Van Cittert IPC deconvolution.          This method is for t, Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spat, Build or load a normalised 9x9 IPC kernel.          If ``config.ipc_kernel_pat, IPCConfig (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (20): ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffus, Apply charge diffusion and BFE to a charge image.          Applies static Gaus, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral c, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussi, Apply the brighter-fatter effect via iterative Jacobi redistribution., ChargeDiffusionConfig, Configuration for the charge diffusion and brighter-fatter effect model. (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (8): ValueError when ideal_image_e contains negative electron counts., Injecting a bright point source and applying charge diffusion must     decrease, All Phase B fields must be declared in ProvenanceRecord.model_fields., H4RG10Detector constructs without error and stores the config., test_bfe_widens_psf(), test_detector_construction(), test_process_epoch_rejects_negative_input(), test_provenance_record_has_phase_b_fields()

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (11): ClusteredCosmicRayInjector, Deposit a single cosmic-ray event at a specified location.          Deterministi, Clustered cosmic-ray hit injector.      Simulates cosmic-ray strikes as spatiall, Inject cosmic-ray hits into a 2D image.          Parameters         ----------, Inject cosmic-ray hits into a single read of a 3D MULTIACCUM ramp.          Inte, Checks provenance applied-effect flags and counts.      All four physics stage, diffuse(ipc(x)) != ipc(diffuse(x)) for non-trivial kernels.      With the phys, sanitize_rng_state raises TypeError for non-dict inputs. (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.25
Nodes (8): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py =======================================, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Paramete, # TODO: Memory optimization - slice specific neighborhood instead of, Find the lower grid index and fractional offset for interpolation.      Parame, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially-

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (8): _make_readout_sim(), Helper: build a MultiAccumSimulator with explicit parameters., simulate_ramp returns (ramp, sat_reads) with ramp shape (n_reads, ny, nx)., Zero-photon ramp: per-read dark increment mean ≈ dark_e_per_s * frame_time., Zero-signal, zero-dark ramp: spatial variance per read ≈ (cds/√2)²., test_dark_current_accumulation(), test_ramp_dimensions_and_timing(), test_read_noise_addition()

### Community 11 - "Community 11"
Cohesion: 0.5
Nodes (3): get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ----

### Community 12 - "Community 12"
Cohesion: 0.5
Nodes (4): _make_valid_record(), Helper: build a minimal valid ProvenanceRecord for drift tests., ProvenanceTracker raises ValueError when record git_commit is None     but the, test_tracker_rejects_silent_metadata_drift()

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): Prevent analytic kernel from producing a negative centre pixel.          For t

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Sanitize numpy types in dict-form state; pass strings through unchanged.

## Knowledge Gaps
- **25 isolated node(s):** `smig/config/schemas.py ====================== Immutable, validated detector co`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.`, `Configuration for the charge diffusion and brighter-fatter effect model.` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 13`** (1 nodes): `Prevent analytic kernel from producing a negative centre pixel.          For t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `Sanitize numpy types in dict-form state; pass strings through unchanged.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 10`, `Community 12`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **Why does `ProvenanceRecord` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 10`, `Community 12`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `IPCConfig` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 10`, `Community 12`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `DetectorConfig` (e.g. with `smig/config/utils.py ==================== Config loading and canonical hashing u` and `Load and validate a DetectorConfig from a YAML file.      Parameters     -------`) actually correct?**
  _`DetectorConfig` has 87 INFERRED edges - model-reasoned connections that need verification._
- **Are the 64 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `H4RG10Detector` (e.g. with `smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.` and `ChargeDiffusionConfig`) actually correct?**
  _`H4RG10Detector` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `IPCConfig` (e.g. with `FieldDependentIPC` and `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance`) actually correct?**
  _`IPCConfig` has 62 INFERRED edges - model-reasoned connections that need verification._