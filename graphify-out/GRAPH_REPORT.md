# Graph Report - .  (2026-04-10)

## Corpus Check
- 21 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 235 nodes · 785 edges · 23 communities detected
- Extraction: 29% EXTRACTED · 71% INFERRED · 0% AMBIGUOUS · INFERRED: 556 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 75 edges
2. `ProvenanceRecord` - 52 edges
3. `H4RG10Detector` - 51 edges
4. `IPCConfig` - 49 edges
5. `GeometryConfig` - 47 edges
6. `ChargeDiffusionConfig` - 47 edges
7. `ClusteredCosmicRayInjector` - 47 edges
8. `DetectorOutput` - 45 edges
9. `EventOutput` - 45 edges
10. `FieldDependentIPC` - 45 edges

## Surprising Connections (you probably didn't know these)
- `Two-component exponential persistence (residual image) model.      Tracks trappe` --uses--> `PersistenceConfig`  [INFERRED]
  smig\sensor\persistence.py → smig\config\schemas.py
- `Polynomial detector nonlinearity model.      Converts accumulated charge (in ele` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `Apply the nonlinearity polynomial to a charge image.          Parameters` --uses--> `NonlinearityConfig`  [INFERRED]
  smig\sensor\nonlinearity.py → smig\config\schemas.py
- `smig/config/utils.py ==================== Config loading and canonical hashing u` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py
- `Load and validate a DetectorConfig from a YAML file.      Parameters     -------` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (33): OneOverFNoise, smig/sensor/noise/correlated.py ================================ Correlated nois, 1/f (pink) correlated noise generator.      Generates spatially and temporally c, Inject 1/f correlated noise into an image.          Parameters         ---------, # TODO: Implement physical model — generate 1/f noise via FFT-based, Random telegraph signal (RTS) noise generator.      Simulates discrete switching, Inject RTS noise into an image.          Parameters         ----------         i, # TODO: Implement physical model — sample a two-state Markov chain (+25 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (24): FieldDependentIPC, smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I, Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spatia, Validate that a loaded IPC kernel has an expected shape.          Raises ``NotIm, Apply IPC convolution to a charge image.          Parameters         ----------, # TODO: Implement physical model — load 9×9 field-varying kernel from, IPCConfig, Inter-pixel capacitance (IPC) kernel parameters.      Only scalar defaults are s (+16 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (19): ProvenanceRecord, smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, Immutable audit record for one simulated epoch of one microlensing event.      A, _sanitize_numpy_types(), sanitize_rng_state(), smig/sensor/validation/test_integration.py =====================================, load_detector_config correctly parses smig/config/roman_wfi.yaml. (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (25): smig/sensor/nonlinearity.py ============================ Polynomial detector non, # TODO: Implement physical model — evaluate polynomial, GeometryConfig, NonlinearityConfig, Focal-plane geometry of a single H4RG-10 SCA., Polynomial detector nonlinearity model.      The normalized measured response S_, smig/sensor/validation/test_config_utils.py ====================================, SHA-256 of the default DetectorConfig must match the pinned canary value.      I (+17 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (17): BaseModel, smig/sensor/persistence.py =========================== Two-component exponential, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ElectricalConfig, EnvironmentConfig, PersistenceConfig (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (14): ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffusio, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral cha, Apply charge diffusion and BFE to a charge image.          Parameters         --, # TODO: Implement physical model — Gaussian diffusion kernel +, ChargeDiffusionConfig, Minimal configuration for the charge diffusion and brighter-fatter effect model., smig/sensor/validation/test_unit.py ===================================== Unit t (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.2
Nodes (12): EventOutput, Multi-epoch event simulation result.      Note: ``frozen=True`` freezes attribut, NonLinearityModel, Polynomial detector nonlinearity model.      Converts accumulated charge (in ele, Apply the nonlinearity polynomial to a charge image.          Parameters, MultiAccumSimulator, smig/sensor/readout.py ======================= MULTIACCUM (up-the-ramp) readout, MULTIACCUM (up-the-ramp) readout simulator.      Builds a non-destructive read r (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (0): 

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (5): H4RG10Detector, All records are ProvenanceRecords with correct event_id and epoch_index., Charge diffusion must conserve total electron count within 0.01%., test_charge_diffusion_conservation(), test_process_event_provenance_records_are_valid()

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (2): ValueError when ideal_cube_e is 2-D instead of 3-D., test_process_event_rejects_2d_cube()

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (2): Every *_applied key in provenance_data must be a native Python bool., test_process_epoch_applied_flags_are_booleans()

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (2): ClusteredCosmicRayInjector.apply() must reject 3D arrays with ValueError., test_cr_injector_signature_2d_only()

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (2): process_event must raise ValueError for decreasing timestamps., test_process_event_rejects_non_monotone_timestamps()

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (2): ValueError on NaN anywhere in ideal_image_e., test_process_epoch_rejects_nan_input()

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (2): cr_mask must have the same shape as rate_image., test_process_epoch_cr_mask_shape_matches_rate_image()

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (2): diffuse(ipc(x)) != ipc(diffuse(x)) for non-trivial kernels., test_chain_order_cd_before_ipc_noncommutative()

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (2): IPC convolution must conserve total flux to within 0.01%., test_ipc_flux_conservation()

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (2): Hash is a valid lowercase hex string of length 64., test_config_sha256_is_hex_string()

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (2): Pixels strictly below the saturation threshold must not be flagged., test_saturation_mask_below_threshold_not_masked()

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (2): Provenance random_state is a static snapshot, not a live generator reference., test_rng_state_serialization_is_snapshot()

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (2): IPC applied to a point source must produce asymmetric neighbour values     that, test_ipc_asymmetric_kernel_injection()

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (2): Output rate_image must not be the same object as the input array., test_process_epoch_output_does_not_alias_input()

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): Delegate to the module-level sanitize_rng_state function.

## Knowledge Gaps
- **14 isolated node(s):** `smig/config/schemas.py ====================== Immutable, validated detector conf`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.      Th`, `Minimal configuration for the charge diffusion and brighter-fatter effect model.` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (2 nodes): `ValueError when ideal_cube_e is 2-D instead of 3-D.`, `test_process_event_rejects_2d_cube()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (2 nodes): `Every *_applied key in provenance_data must be a native Python bool.`, `test_process_epoch_applied_flags_are_booleans()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (2 nodes): `ClusteredCosmicRayInjector.apply() must reject 3D arrays with ValueError.`, `test_cr_injector_signature_2d_only()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (2 nodes): `process_event must raise ValueError for decreasing timestamps.`, `test_process_event_rejects_non_monotone_timestamps()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `ValueError on NaN anywhere in ideal_image_e.`, `test_process_epoch_rejects_nan_input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `cr_mask must have the same shape as rate_image.`, `test_process_epoch_cr_mask_shape_matches_rate_image()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `diffuse(ipc(x)) != ipc(diffuse(x)) for non-trivial kernels.`, `test_chain_order_cd_before_ipc_noncommutative()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `IPC convolution must conserve total flux to within 0.01%.`, `test_ipc_flux_conservation()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `Hash is a valid lowercase hex string of length 64.`, `test_config_sha256_is_hex_string()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `Pixels strictly below the saturation threshold must not be flagged.`, `test_saturation_mask_below_threshold_not_masked()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `Provenance random_state is a static snapshot, not a live generator reference.`, `test_rng_state_serialization_is_snapshot()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `IPC applied to a point source must produce asymmetric neighbour values     that`, `test_ipc_asymmetric_kernel_injection()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `Output rate_image must not be the same object as the input array.`, `test_process_epoch_output_does_not_alias_input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Delegate to the module-level sanitize_rng_state function.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 21`?**
  _High betweenness centrality (0.259) - this node is a cross-community bridge._
- **Why does `ProvenanceRecord` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 5`, `Community 6`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 21`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `IPCConfig` connect `Community 1` to `Community 0`, `Community 3`, `Community 4`, `Community 5`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 21`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Are the 72 inferred relationships involving `DetectorConfig` (e.g. with `smig/config/utils.py ==================== Config loading and canonical hashing u` and `Load and validate a DetectorConfig from a YAML file.      Parameters     -------`) actually correct?**
  _`DetectorConfig` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 49 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `H4RG10Detector` (e.g. with `smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.` and `ChargeDiffusionConfig`) actually correct?**
  _`H4RG10Detector` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `IPCConfig` (e.g. with `FieldDependentIPC` and `smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I`) actually correct?**
  _`IPCConfig` has 46 INFERRED edges - model-reasoned connections that need verification._