# Graph Report - .  (2026-04-09)

## Corpus Check
- 20 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 186 nodes · 469 edges · 22 communities detected
- Extraction: 38% EXTRACTED · 62% INFERRED · 0% AMBIGUOUS · INFERRED: 289 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 58 edges
2. `ProvenanceRecord` - 42 edges
3. `H4RG10Detector` - 39 edges
4. `DetectorOutput` - 34 edges
5. `EventOutput` - 34 edges
6. `GeometryConfig` - 27 edges
7. `NonLinearityModel` - 19 edges
8. `MultiAccumSimulator` - 15 edges
9. `ChargeDiffusionModel` - 14 edges
10. `FieldDependentIPC` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spatia` --uses--> `IPCConfig`  [INFERRED]
  smig\sensor\ipc.py → smig\config\schemas.py
- `Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral cha` --uses--> `DetectorConfig`  [INFERRED]
  smig\sensor\charge_diffusion.py → smig\config\schemas.py
- `1/f (pink) correlated noise generator.      Generates spatially and temporally c` --uses--> `DetectorConfig`  [INFERRED]
  smig\sensor\noise\correlated.py → smig\config\schemas.py
- `Random telegraph signal (RTS) noise generator.      Simulates discrete switching` --uses--> `DetectorConfig`  [INFERRED]
  smig\sensor\noise\correlated.py → smig\config\schemas.py
- `Clustered cosmic-ray hit injector.      Simulates cosmic-ray strikes as spatiall` --uses--> `DetectorConfig`  [INFERRED]
  smig\sensor\noise\cosmic_rays.py → smig\config\schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.1
Nodes (18): smig/sensor/charge_diffusion.py ================================ Charge diffusio, Apply charge diffusion and BFE to a charge image.          Parameters         --, # TODO: Implement physical model — Gaussian diffusion kernel +, smig/sensor/noise/correlated.py ================================ Correlated nois, Inject 1/f correlated noise into an image.          Parameters         ---------, # TODO: Implement physical model — generate 1/f noise via FFT-based, Inject RTS noise into an image.          Parameters         ----------         i, # TODO: Implement physical model — sample a two-state Markov chain (+10 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (18): ChargeDiffusionModel, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral cha, OneOverFNoise, 1/f (pink) correlated noise generator.      Generates spatially and temporally c, Random telegraph signal (RTS) noise generator.      Simulates discrete switching, RTSNoise, ClusteredCosmicRayInjector, Clustered cosmic-ray hit injector.      Simulates cosmic-ray strikes as spatiall (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.16
Nodes (14): NonLinearityModel, smig/sensor/nonlinearity.py ============================ Polynomial detector non, Polynomial detector nonlinearity model.      Converts accumulated charge (in ele, Apply the nonlinearity polynomial to a charge image.          Parameters, # TODO: Implement physical model — evaluate polynomial, MultiAccumSimulator, smig/sensor/readout.py ======================= MULTIACCUM (up-the-ramp) readout, MULTIACCUM (up-the-ramp) readout simulator.      Builds a non-destructive read r (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.17
Nodes (12): ProvenanceRecord, Immutable audit record for one simulated epoch of one microlensing event.      A, smig/sensor/validation/test_integration.py =====================================, load_detector_config correctly parses smig/config/roman_wfi.yaml., process_event → ProvenanceTracker → sidecar round-trips as valid JSON., test_full_chain_integration(), test_load_detector_config_from_yaml(), ProvenanceTracker (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (4): All provenance timestamps are timezone-aware (UTC)., Pixels at exactly the saturation threshold must be flagged.      Uses _saturatio, test_process_event_provenance_timestamps_are_aware(), test_saturation_mask_correct_threshold()

### Community 5 - "Community 5"
Cohesion: 0.14
Nodes (11): BaseModel, smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I, Apply IPC convolution to a charge image.          Parameters         ----------, # TODO: Implement physical model — load 9×9 field-varying kernel from, ElectricalConfig, EnvironmentConfig, IPCConfig, smig/config/schemas.py ====================== Immutable, validated detector conf (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (11): GeometryConfig, Focal-plane geometry of a single H4RG-10 SCA., smig/sensor/validation/test_unit.py ===================================== Unit t, ValueError when ideal_image_e is 1-D (ndim != 2)., 16×16 DetectorConfig for fast unit tests., Provenance random_state is a static snapshot, not a live generator reference., H4RG10Detector constructs without error and stores the config., small_cfg() (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (8): DynamicPersistence, smig/sensor/persistence.py =========================== Two-component exponential, Two-component exponential persistence (residual image) model.      Tracks trappe, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, PersistenceConfig, Two-component exponential persistence (residual-image) model.      The persisten

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (9): H4RG10Detector, Checks provenance applied-effect flags and counts.      charge_diffusion_applied, cr_mask must have the same shape as rate_image., ValueError when ideal_cube_e is 2-D instead of 3-D., Pixels strictly below the saturation threshold must not be flagged., test_process_epoch_cr_mask_shape_matches_rate_image(), test_process_epoch_provenance_data_stub_flags(), test_process_event_rejects_2d_cube() (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (5): smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, _sanitize_numpy_types(), sanitize_rng_state(), smig/provenance/tracker.py ========================== Accumulates ProvenanceReco

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (2): ValueError when ideal_image_e contains negative electron counts., test_process_epoch_rejects_negative_input()

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (2): Mutating ideal_cube_e after process_event does not corrupt the output.      proc, test_process_event_independence_from_input_mutation()

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (2): Hash is a valid lowercase hex string of length 64., test_config_sha256_is_hex_string()

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (2): ValueError on NaN anywhere in ideal_image_e., test_process_epoch_rejects_nan_input()

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (2): All records are ProvenanceRecords with correct event_id and epoch_index., test_process_event_provenance_records_are_valid()

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (2): Output rate_image is always float64 even when input dtype is integer., test_process_epoch_rate_image_is_float64()

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (2): All records share the same config_sha256., test_process_event_provenance_config_sha256_consistent()

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (2): random_state in provenance_data must be natively JSON-serializable., test_process_epoch_provenance_random_state_json_serializable()

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (2): Identical configs produce the same 64-char hash; different configs differ., test_config_sha256_determinism()

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (2): Stub returns a copy of the input, not the same object., test_process_epoch_stub_returns_copy_not_alias()

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Delegate to the module-level sanitize_rng_state function.

## Knowledge Gaps
- **13 isolated node(s):** `smig/config/schemas.py ====================== Immutable, validated detector conf`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.      Th`, `Inter-pixel capacitance (IPC) kernel parameters.      Only scalar defaults are s` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (2 nodes): `ValueError when ideal_image_e contains negative electron counts.`, `test_process_epoch_rejects_negative_input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (2 nodes): `Mutating ideal_cube_e after process_event does not corrupt the output.      proc`, `test_process_event_independence_from_input_mutation()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (2 nodes): `Hash is a valid lowercase hex string of length 64.`, `test_config_sha256_is_hex_string()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `ValueError on NaN anywhere in ideal_image_e.`, `test_process_epoch_rejects_nan_input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `All records are ProvenanceRecords with correct event_id and epoch_index.`, `test_process_event_provenance_records_are_valid()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `Output rate_image is always float64 even when input dtype is integer.`, `test_process_epoch_rate_image_is_float64()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `All records share the same config_sha256.`, `test_process_event_provenance_config_sha256_consistent()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `random_state in provenance_data must be natively JSON-serializable.`, `test_process_epoch_provenance_random_state_json_serializable()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `Identical configs produce the same 64-char hash; different configs differ.`, `test_config_sha256_determinism()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `Stub returns a copy of the input, not the same object.`, `test_process_epoch_stub_returns_copy_not_alias()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Delegate to the module-level sanitize_rng_state function.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 8`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`?**
  _High betweenness centrality (0.298) - this node is a cross-community bridge._
- **Why does `ProvenanceRecord` connect `Community 3` to `Community 1`, `Community 4`, `Community 5`, `Community 6`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Why does `H4RG10Detector` connect `Community 8` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 55 inferred relationships involving `DetectorConfig` (e.g. with `smig/config/utils.py ==================== Config loading and canonical hashing u` and `Load and validate a DetectorConfig from a YAML file.      Parameters     -------`) actually correct?**
  _`DetectorConfig` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `H4RG10Detector` (e.g. with `DetectorConfig` and `ProvenanceRecord`) actually correct?**
  _`H4RG10Detector` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `DetectorOutput` (e.g. with `.process_epoch()` and `DetectorConfig`) actually correct?**
  _`DetectorOutput` has 32 INFERRED edges - model-reasoned connections that need verification._