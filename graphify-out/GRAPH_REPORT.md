# Graph Report - .  (2026-04-08)

## Corpus Check
- 20 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 161 nodes · 371 edges · 11 communities detected
- Extraction: 42% EXTRACTED · 58% INFERRED · 0% AMBIGUOUS · INFERRED: 216 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 47 edges
2. `ProvenanceRecord` - 31 edges
3. `H4RG10Detector` - 28 edges
4. `DetectorOutput` - 23 edges
5. `EventOutput` - 23 edges
6. `GeometryConfig` - 16 edges
7. `ChargeDiffusionModel` - 14 edges
8. `FieldDependentIPC` - 14 edges
9. `OneOverFNoise` - 14 edges
10. `RTSNoise` - 14 edges

## Surprising Connections (you probably didn't know these)
- `smig/config/utils.py ==================== Config loading and canonical hashing u` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py
- `Load and validate a DetectorConfig from a YAML file.      Parameters     -------` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py
- `Compute the SHA-256 fingerprint of a DetectorConfig.      Uses ``model_dump_json` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\utils.py → smig\config\schemas.py
- `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco` --uses--> `ProvenanceRecord`  [INFERRED]
  smig\provenance\tracker.py → smig\provenance\schema.py
- `Accumulates and persists provenance records for one microlensing event.      Par` --uses--> `ProvenanceRecord`  [INFERRED]
  smig\provenance\tracker.py → smig\provenance\schema.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.1
Nodes (26): ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffusio, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral cha, Apply charge diffusion and BFE to a charge image.          Parameters         --, # TODO: Implement physical model — Gaussian diffusion kernel +, OneOverFNoise, smig/sensor/noise/correlated.py ================================ Correlated nois, 1/f (pink) correlated noise generator.      Generates spatially and temporally c (+18 more)

### Community 1 - "Community 1"
Cohesion: 0.24
Nodes (22): DetectorOutput, EventOutput, H4RG10Detector, ProvenanceRecord, Immutable audit record for one simulated epoch of one microlensing event.      A, GeometryConfig, Focal-plane geometry of a single H4RG-10 SCA., smig/sensor/validation/test_integration.py ===================================== (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (9): small_cfg(), test_config_sha256_determinism(), test_config_sha256_is_hex_string(), test_detector_construction(), test_process_epoch_provenance_data_stub_flags(), test_process_epoch_stub_returns_copy_not_alias(), test_process_event_provenance_config_sha256_consistent(), test_process_event_provenance_records_are_valid() (+1 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (11): BaseModel, ElectricalConfig, EnvironmentConfig, smig/config/schemas.py ====================== Immutable, validated detector conf, Telescope and sky environment parameters., Electrical characteristics governing signal range and read noise., get_config_sha256(), load_detector_config() (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (7): smig/provenance/schema.py ========================= Pydantic v2 model representi, ProvenanceTracker, smig/provenance/tracker.py ========================== Accumulates ProvenanceReco, Atomically serialise all accumulated records to a JSON sidecar file.          Th, Return the number of records accumulated so far., Accumulates and persists provenance records for one microlensing event.      Par, Append one epoch's provenance record to the in-memory accumulator.          Para

### Community 5 - "Community 5"
Cohesion: 0.25
Nodes (8): Multi-epoch event simulation result.      Note: ``frozen=True`` freezes attribut, FieldDependentIPC, smig/sensor/ipc.py ================== Field-dependent inter-pixel capacitance (I, Field-dependent inter-pixel capacitance (IPC) convolution.      Applies a spatia, Apply IPC convolution to a charge image.          Parameters         ----------, # TODO: Implement physical model — load 9×9 field-varying kernel from, IPCConfig, Inter-pixel capacitance (IPC) kernel parameters.      Only scalar defaults are s

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (7): NonLinearityModel, smig/sensor/nonlinearity.py ============================ Polynomial detector non, Polynomial detector nonlinearity model.      Converts accumulated charge (in ele, Apply the nonlinearity polynomial to a charge image.          Parameters, # TODO: Implement physical model — evaluate polynomial, NonlinearityConfig, Polynomial detector nonlinearity model.      The normalized measured response S_

### Community 7 - "Community 7"
Cohesion: 0.29
Nodes (7): DynamicPersistence, smig/sensor/persistence.py =========================== Two-component exponential, Two-component exponential persistence (residual image) model.      Tracks trappe, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, PersistenceConfig, Two-component exponential persistence (residual-image) model.      The persisten

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (7): MultiAccumSimulator, smig/sensor/readout.py ======================= MULTIACCUM (up-the-ramp) readout, MULTIACCUM (up-the-ramp) readout simulator.      Builds a non-destructive read r, Simulate MULTIACCUM ramp readout of a charge image.          Parameters, # TODO: Implement physical model — build up-the-ramp sample cube with, Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.      Th, ReadoutConfig

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (0): 

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (1): Recursively convert numpy types to native Python for JSON safety.          Conve

## Knowledge Gaps
- **12 isolated node(s):** `smig/config/schemas.py ====================== Immutable, validated detector conf`, `Focal-plane geometry of a single H4RG-10 SCA.`, `Electrical characteristics governing signal range and read noise.`, `Non-destructive readout timing for Multi-Accumulation (MULTIACCUM) mode.      Th`, `Inter-pixel capacitance (IPC) kernel parameters.      Only scalar defaults are s` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `Recursively convert numpy types to native Python for JSON safety.          Conve`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 0` to `Community 1`, `Community 3`, `Community 5`?**
  _High betweenness centrality (0.322) - this node is a cross-community bridge._
- **Why does `ProvenanceRecord` connect `Community 1` to `Community 0`, `Community 3`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `smig/sensor/validation/test_unit.py ===================================== Unit t` connect `Community 1` to `Community 0`, `Community 2`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `DetectorConfig` (e.g. with `smig/config/utils.py ==================== Config loading and canonical hashing u` and `Load and validate a DetectorConfig from a YAML file.      Parameters     -------`) actually correct?**
  _`DetectorConfig` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `ProvenanceRecord` (e.g. with `ProvenanceTracker` and `smig/provenance/tracker.py ========================== Accumulates ProvenanceReco`) actually correct?**
  _`ProvenanceRecord` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `H4RG10Detector` (e.g. with `DetectorConfig` and `ProvenanceRecord`) actually correct?**
  _`H4RG10Detector` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `DetectorOutput` (e.g. with `.process_epoch()` and `DetectorConfig`) actually correct?**
  _`DetectorOutput` has 21 INFERRED edges - model-reasoned connections that need verification._