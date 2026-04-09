# SMIG v2 — Claude Persistent Context

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current

---

## WHAT — Codebase Map

| Path | Purpose |
|---|---|
| `smig/config/schemas.py` | Pydantic v2 `DetectorConfig` + sub-configs (single source of truth for all H4RG-10 constants) |
| `smig/config/roman_wfi.yaml` | Default Roman WFI parameters (load via `DetectorConfig.model_validate(yaml.safe_load(...))`) |
| `smig/provenance/schema.py` | `ProvenanceRecord` — immutable per-epoch audit record; includes NumPy RNG state sanitization |
| `smig/provenance/tracker.py` | `ProvenanceTracker` — accumulates records, writes atomic JSON sidecar via `os.replace()` |
| `smig/sensor/detector.py` | `H4RG10Detector` — **star-topology orchestrator** (not yet implemented in Phase 1) |
| `smig/sensor/ipc.py` | `FieldDependentIPC` — loads 9×9 field-varying kernel from HDF5 |
| `smig/sensor/charge_diffusion.py` | `ChargeDiffusionModel` + Brighter-Fatter Effect |
| `smig/sensor/persistence.py` | `DynamicPersistence` — two-component exponential trap model |
| `smig/sensor/nonlinearity.py` | `NonLinearityModel` — polynomial INL + per-pixel NL |
| `smig/sensor/readout.py` | `MultiAccumSimulator` — up-the-ramp MULTIACCUM ramp builder |
| `smig/sensor/noise/` | `OneOverFNoise`, `RTSNoise`, `ClusteredCosmicRayInjector`, `PoissonPhotonNoise`, `ReadNoise` |
| `smig/sensor/calibration/` | HDF5 IPC kernel loader, nonlinearity calibration curve loader |
| `smig/sensor/validation/` | Unit tests, integration tests, 32 GB memory profiler |

**Graph god nodes** (from `graphify-out/GRAPH_REPORT.md`):
- `H4RG10Detector` (12 edges) — central orchestrator bridging all communities
- `SpatiotemporalTrigger` (5 edges) — Stage A classifier (Phase 2+)
- `ProvenanceTracker` (4 edges) — reproducibility contract anchor
- `MicroluxEngine` (4 edges) — microlensing physics (Phase 2+)

---

## WHY — Mission Context

SMIG v2 simulates the **Roman Space Telescope WFI H4RG-10 HgCdTe detector** to generate physically realistic synthetic exposures for microlensing event classification.

- Phase 1 replaces v1's `roman_imsim` wrappers and static 3×3 IPC kernel with a rigorous, modular detector chain
- The fixed signal chain order is: charge diffusion → IPC → persistence → nonlinearity → MULTIACCUM readout → noise injection
- Downstream pipeline (Phases 2–6) trains a `SpatiotemporalTrigger` (NeuralCDE + EfficientNet-B0) on simulated ramps

---

## HOW — Verification Commands

```bash
# Run unit tests for each sensor module
python -m pytest smig/sensor/validation/unit_tests.py -v

# Run full-chain integration regression
python -m pytest smig/sensor/validation/integration_tests.py -v

# Check memory does not exceed 32 GB during a MULTIACCUM loop
python smig/sensor/validation/memory_profiler.py

# Validate config round-trips cleanly (no silent mutation)
python -c "
import yaml; from pathlib import Path
from smig.config.schemas import DetectorConfig
cfg = DetectorConfig.model_validate(yaml.safe_load(Path('smig/config/roman_wfi.yaml').read_text()))
print(cfg.model_dump_json(indent=2))
"

# Verify provenance sidecar is JSON-clean (no numpy types)
python -c "
import json, numpy as np
from datetime import datetime, timezone
from smig.provenance.schema import ProvenanceRecord
rng = np.random.default_rng(0)
r = ProvenanceRecord(
    event_id='test', epoch_index=0,
    timestamp_utc=datetime.now(timezone.utc),
    git_commit=None, container_digest=None,
    python_version='3.11', numpy_version=np.__version__,
    config_sha256='a'*64, random_state=rng.bit_generator.state,
    ipc_applied=True, persistence_applied=True, nonlinearity_applied=True,
    saturated_pixel_count=0, cosmic_ray_hit_count=0,
)
json.dumps(r.model_dump(mode='json'))   # must not raise
print('OK')
"
```

---

## Architectural Constraints — ENFORCE THESE

### Star Topology (non-negotiable)
- `H4RG10Detector` in `smig/sensor/detector.py` is the **sole orchestrator**
- Noise and physics leaf modules (`ipc.py`, `persistence.py`, `noise/*.py`, etc.) **must not import each other**
- Sensor modules **must never `import galsim`** — they receive and return plain `np.ndarray`s; GalSim rendering happens upstream in `CrowdedFieldRenderer` before the detector chain

### Memory — 32 GB Hard Limit
- Intermediate 3D ramp cubes (`shape: [n_reads, ny, nx]` → ~1.3 GB at float32 for 4096×4096×9) accumulate fast
- After each frame is folded into the ramp **explicitly call `del frame_cube; gc.collect()`**
- Never hold more than two ramp-sized arrays simultaneously in a MultiAccum loop

### Config Rigor
- Every Pydantic model **must** use `model_config = ConfigDict(frozen=True, extra="forbid")`
- **Zero magic numbers** in `smig/sensor/` — all physical constants come from a `DetectorConfig` instance passed as an argument
- Load configs via `DetectorConfig.model_validate(yaml.safe_load(...))`, never construct with raw kwargs outside tests

### NumPy/JSON Trap
- `numpy.random.Generator.bit_generator.state` returns dicts containing `np.ndarray` and `np.uint64` — these are **not JSON-serializable**
- Always pass raw RNG state through `ProvenanceRecord`'s `_sanitize_numpy_types` validator (it calls `.tolist()` / `.item()` recursively)
- Never call `json.dumps()` directly on an unsanitized RNG state dict

### Timestamps — UTC Only
- All timestamps must be `pydantic.AwareDatetime` fields
- Always construct with `datetime.now(timezone.utc)` — naive `datetime.utcnow()` is rejected at validation time
- The provenance sidecar serializes to ISO-8601 strings via `model_dump(mode="json")`
