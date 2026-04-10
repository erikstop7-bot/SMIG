# Graph Report - .  (2026-04-10)

## Corpus Check
- 23 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 252 nodes · 893 edges · 10 communities detected
- Extraction: 28% EXTRACTED · 72% INFERRED · 0% AMBIGUOUS · INFERRED: 647 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 80 edges
2. `ProvenanceRecord` - 57 edges
3. `H4RG10Detector` - 56 edges
4. `IPCConfig` - 54 edges
5. `GeometryConfig` - 52 edges
6. `ChargeDiffusionConfig` - 52 edges
7. `ClusteredCosmicRayInjector` - 52 edges
8. `DetectorOutput` - 50 edges
9. `EventOutput` - 50 edges
10. `FieldDependentIPC` - 50 edges

## Surprising Connections (you probably didn't know these)
- `Two-component exponential persistence (residual image) model.      Tracks trappe` --uses--> `PersistenceConfig`  [INFERRED]
  smig\sensor\persistence.py → smig\config\schemas.py
- `Polynomial detector nonlinearity model.      Converts accumulated charge (in ele` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `Apply the nonlinearity polynomial to a charge image.          Parameters` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `1/f (pink) correlated noise generator.      Generates spatially and temporally c` --uses--> `DetectorConfig`  [INFERRED]
  smig\sensor\noise\correlated.py → smig\config\schemas.py
- `Inject 1/f correlated noise into an image.          Parameters         ---------` --uses--> `DetectorConfig`  [INFERRED]
  smig\sensor\noise\correlated.py → smig\config\schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (32): ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffusio, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral cha, Apply charge diffusion and BFE to a charge image.          Parameters         --, # TODO: Implement physical model — Gaussian diffusion kernel +, ChargeDiffusionConfig, Minimal configuration for the charge diffusion and brighter-fatter effect model., smig/sensor/validation/test_unit.py ===================================== Unit t (+24 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (28): OneOverFNoise, 1/f (pink) correlated noise generator.      Generates spatially and temporally c, Inject 1/f correlated noise into an image.          Parameters         ---------, Random telegraph signal (RTS) noise generator.      Simulates discrete switching, Inject RTS noise into an image.          Parameters         ----------         i, RTSNoise, DetectorOutput, EventOutput (+20 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (33): ProvenanceRecord, smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, Immutable audit record for one simulated epoch of one microlensing event.      A, _sanitize_numpy_types(), sanitize_rng_state(), smig/sensor/validation/test_integration.py =====================================, load_detector_config correctly parses smig/config/roman_wfi.yaml. (+25 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (27): smig/sensor/noise/correlated.py ================================ Correlated nois, # TODO: Implement physical model — generate 1/f noise via FFT-based, # TODO: Implement physical model — sample a two-state Markov chain, ClusteredCosmicRayInjector, smig/sensor/noise/cosmic_rays.py ================================= Clustered cos, Deposit a single cosmic-ray event at a specified location.          Deterministi, Clustered cosmic-ray hit injector.      Simulates cosmic-ray strikes as spatiall, Inject cosmic-ray hits into a 2D image.          Parameters         ---------- (+19 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (24): FieldDependentIPC, smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I, Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spatia, Validate that a loaded IPC kernel has an expected shape.          Raises ``NotIm, Apply IPC convolution to a charge image.          Parameters         ----------, # TODO: Implement physical model — load 9×9 field-varying kernel from, IPCConfig, Inter-pixel capacitance (IPC) kernel parameters.      Only scalar defaults are s (+16 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (25): smig/sensor/nonlinearity.py ============================ Polynomial detector non, # TODO: Implement physical model — evaluate polynomial, GeometryConfig, NonlinearityConfig, Focal-plane geometry of a single H4RG-10 SCA., Polynomial detector nonlinearity correction model.      Maps normalized charge $, smig/sensor/validation/test_config_utils.py ====================================, SHA-256 of the default DetectorConfig must match the pinned canary value.      I (+17 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (14): BaseModel, smig/sensor/persistence.py =========================== Two-component exponential, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ElectricalConfig, EnvironmentConfig, NoiseConfig (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.5
Nodes (3): get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ----

### Community 8 - "Community 8"
Cohesion: 0.5
Nodes (4): _make_valid_record(), Helper: build a minimal valid ProvenanceRecord for drift tests., ProvenanceTracker raises ValueError when record git_commit is None     but the t, test_tracker_rejects_silent_metadata_drift()

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (1): Delegate to the module-level sanitize_rng_state function.

## Knowledge Gaps
- **17 isolated node(s):** `smig/config/schemas.py ====================== Immutable, validated detector conf`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.      Th`, `Minimal configuration for the charge diffusion and brighter-fatter effect model.` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (1 nodes): `Delegate to the module-level sanitize_rng_state function.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 8`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `ProvenanceRecord` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`, `Community 4`, `Community 6`, `Community 8`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `IPCConfig` connect `Community 4` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 8`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `DetectorConfig` (e.g. with `smig/config/utils.py ==================== Config loading and canonical hashing u` and `Load and validate a DetectorConfig from a YAML file.      Parameters     -------`) actually correct?**
  _`DetectorConfig` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 54 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 54 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `H4RG10Detector` (e.g. with `smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.` and `ChargeDiffusionConfig`) actually correct?**
  _`H4RG10Detector` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `IPCConfig` (e.g. with `FieldDependentIPC` and `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I`) actually correct?**
  _`IPCConfig` has 51 INFERRED edges - model-reasoned connections that need verification._