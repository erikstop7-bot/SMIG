<!-- converted from smig_v2_phase1_spec.docx -->


SMIG v2 — Phase 1 Implementation Specification
Advanced Sensor & Detector Physics Modules
H4RG-10 HgCdTe Detector Simulation for Roman WFI
v2.0-alpha  —  April 2026  —  Addresses all v1 review findings

# 1. Scope and Relationship to v1 Review Findings
This document specifies the exact Python modules, classes, method signatures, configuration schemas, and unit test contracts required to implement Phase 1 of the SMIG v2 update. Phase 1 replaces the v1 sensor simulation (which relied on basic roman_imsim wrappers and a static 3×3 IPC kernel) with a physically rigorous, H4RG-10-specific detector simulation chain.
Every module in this specification traces to one or more specific findings from the v1 review. The following table maps critical review findings to the Phase 1 modules that resolve them.

# 2. Module Layout and File Structure
The Phase 1 code lives under smig/sensor/ within the SMIG repository. All modules are pure Python with NumPy/SciPy for array operations and optional JAX acceleration for GPU-batched rendering. No module imports GalSim directly; the sensor chain receives and returns plain NumPy arrays, making it testable and swappable.
smig/
├── sensor/                       # PHASE 1 TARGET
│   ├── __init__.py               # Public API: apply_detector_chain()
│   ├── detector.py               # H4RG10Detector orchestrator
│   ├── ipc.py                    # FieldDependentIPC
│   ├── charge_diffusion.py       # ChargeDiffusionModel + BFE
│   ├── persistence.py            # DynamicPersistence
│   ├── nonlinearity.py           # NonLinearityModel (INL + pixel NL)
│   ├── readout.py                # MultiAccumSimulator
│   ├── noise/
│   │   ├── __init__.py           # NoiseInjector aggregate
│   │   ├── correlated.py         # OneOverFNoise, RTSNoise
│   │   ├── cosmic_rays.py        # ClusteredCosmicRayInjector
│   │   └── poisson_read.py       # PoissonPhotonNoise, ReadNoise
│   ├── calibration/
│   │   ├── __init__.py
│   │   ├── ipc_kernels.py        # Load field-dependent kernel data
│   │   └── nl_curves.py          # Load nonlinearity calibration
│   └── validation/
│       ├── __init__.py
│       ├── unit_tests.py         # Per-module acceptance tests
│       ├── integration_tests.py  # Full-chain regression
│       └── memory_profiler.py    # 32 GB RAM constraint check
├── config/
│   ├── schemas.py                # Pydantic v2 config models
│   ├── detector_h4rg10.yaml      # Default H4RG-10 parameters
│   └── roman_wfi.yaml            # Verified Roman WFI parameters
└── provenance/
├── tracker.py                # JSON sidecar provenance logger
└── schema.py                 # Provenance record Pydantic model

# 3. Configuration Schema (smig/config/schemas.py)
All detector parameters are defined as Pydantic v2 BaseModel classes with strict validation, default values sourced from the Roman Technical Handbook, and explicit units in field descriptions. No magic numbers exist anywhere in the codebase; every physical constant traces to this schema.
## 3.1 DetectorConfig
class DetectorConfig(BaseModel):
"""H4RG-10 detector configuration."""
model_config = ConfigDict(frozen=True)

# Geometry
nx: int = 4096
ny: int = 4096
pixel_pitch_um: float = 10.0
pixel_scale_arcsec: float = 0.11

# Electrical
full_well_e: float = 100_000.0
gain_e_per_adu: float = 1.5
read_noise_e_cds: float = 12.0
read_noise_e_effective: float = 5.0  # After multi-read fit
dark_current_e_per_s: float = 0.01

# Readout
n_reads: int = 8  # Up-the-ramp samples
frame_time_s: float = 5.85  # Single read time
exposure_time_s: float = 46.8

# IPC
ipc_kernel_size: int = 9  # 9x9 max extent
ipc_field_dependent: bool = True
ipc_alpha_center: float = 0.02  # Coupling fraction

# Persistence
persistence_tau_short_s: float = 100.0
persistence_tau_long_s: float = 1000.0
persistence_amplitude_short: float = 0.005
persistence_amplitude_long: float = 0.001

# Nonlinearity
nl_poly_coeffs: list[float] = [1.0, -2.7e-6, 7.8e-12]
saturation_flag_threshold: float = 0.85  # Fraction of full_well

# Noise
one_over_f_alpha: float = 1.0  # PSD slope
one_over_f_amplitude: float = 5.0  # e- RMS
rts_pixel_fraction: float = 0.002
rts_amplitude_range_e: tuple[float,float] = (20.0, 200.0)
cr_rate_per_cm2_per_s: float = 5.0
cr_cluster_size_range: tuple[int,int] = (1, 12)

# Spacecraft (CORRECTED from v1)
jitter_rms_mas_per_axis: float = 5.0  # NOT 14 mas
sky_background_mag_per_arcsec2: float = 22.5
## 3.2 Corrected Roman WFI Parameters
The following values were wrong or unverified in v1 and are now corrected with source citations:

# 4. Detector Orchestrator (smig/sensor/detector.py)
The H4RG10Detector class is the single entry point for applying detector physics to an ideal photon-count image. It owns the signal chain ordering and enforces that effects are applied in the physically correct sequence. The chain is not configurable in order; only individual stages can be enabled or disabled for ablation studies.
## 4.1 Class Signature
class H4RG10Detector:
"""
Orchestrates the full H4RG-10 detector simulation.

Signal chain (fixed order):
1. Charge diffusion + brighter-fatter effect
2. Interpixel capacitance (field-dependent 9x9)
3. Persistence injection (history-aware)
4. Nonlinearity + saturation flagging
5. MultiAccum ramp sampling
6. Correlated noise injection (1/f + RTS)
7. Poisson + read noise (per ramp sample)
8. Cosmic ray injection (clustered)
9. Slope fitting (output: rate image in e-/s)
"""

def __init__(self,
config: DetectorConfig,
sca_id: int,
field_position: tuple[float, float],
rng: np.random.Generator,
enable_persistence: bool = True,
enable_ipc: bool = True,
enable_nonlinearity: bool = True,
enable_correlated_noise: bool = True,
enable_cosmic_rays: bool = True):

def process_epoch(self,
ideal_image_e: np.ndarray,
epoch_index: int,
epoch_time_mjd: float
) -> DetectorOutput:
"""
Apply full detector chain to one epoch.

Args:
ideal_image_e: 2D array [ny, nx] of photon
counts (electrons). From GalSim rendering.
epoch_index: Sequential index within event.
epoch_time_mjd: MJD timestamp for persistence
history tracking.

Returns:
DetectorOutput with rate_image, saturation_mask,
cr_mask, and provenance metadata.
"""

def process_event(self,
ideal_cube_e: np.ndarray,
timestamps_mjd: np.ndarray
) -> EventOutput:
"""
Process all epochs of an event sequentially.
Persistence state carries across epochs.
Aggressively garbage-collects intermediate arrays.

Args:
ideal_cube_e: 3D array [n_epochs, ny, nx].
timestamps_mjd: 1D array [n_epochs].

Returns:
EventOutput with rate_cube, masks, provenance.
"""

def reset_persistence(self):
"""Clear persistence history between events."""
## 4.2 Output Data Classes
@dataclass(frozen=True)
class DetectorOutput:
rate_image: np.ndarray       # [ny, nx] float32 e-/s
saturation_mask: np.ndarray  # [ny, nx] bool
cr_mask: np.ndarray          # [ny, nx] bool
ramp_samples: np.ndarray | None  # [n_reads, ny, nx]
provenance: dict             # Full processing log

@dataclass(frozen=True)
class EventOutput:
rate_cube: np.ndarray         # [n_epochs, ny, nx]
saturation_cube: np.ndarray   # [n_epochs, ny, nx]
cr_cube: np.ndarray           # [n_epochs, ny, nx]
persistence_peak_map: np.ndarray  # [ny, nx] max persist
provenance: list[dict]
peak_memory_mb: float
## 4.3 Memory Management Contract
The orchestrator must operate within a 32 GB RAM budget for local prototyping. For a 64×64 stamp with 8 ramp reads, the per-epoch memory footprint is:
Ramp cube: 8 × 64 × 64 × 4 bytes = 131 KB. Intermediate arrays (IPC convolution buffer, noise arrays): approximately 3× stamp size = 393 KB. Total per epoch: approximately 0.5 MB. For a full event of 200 epochs processed sequentially with immediate deallocation of ramp intermediates, peak memory is approximately 200 × (64 × 64 × 4) + 0.5 MB working set = 3.3 MB per event. At 32 GB, this allows approximately 9,000 events to be held in memory simultaneously, which is more than sufficient for batch processing.
The process_event method explicitly calls del ramp_samples and gc.collect() after each epoch's slope fit to prevent ramp arrays from accumulating. A peak_memory_mb field in the output verifies compliance.

# 5. Interpixel Capacitance (smig/sensor/ipc.py)
## 5.1 Physics Background
Interpixel capacitance (IPC) arises from parasitic electrical coupling between adjacent pixels in the H4RG-10 multiplexer. A charge deposited in pixel (i,j) induces a measurable signal in its neighbors. This effect is not a redistribution of charge (which is handled by charge diffusion) but a purely electrical coupling that operates on the voltage signal after charge-to-voltage conversion.
The v1 implementation used a static, symmetric 3×3 kernel with a single coupling coefficient α. Recent H4RG-10 characterization (Freudenburg et al. 2020, Mosby et al. 2020) demonstrates that the IPC kernel is asymmetric (horizontal and vertical coupling coefficients differ by 10–20%), extends to second and third nearest neighbors (requiring a 5×5 or larger kernel), and varies across the detector focal plane (field-dependent). The v2 implementation replaces the static kernel with an asymmetric, field-dependent kernel that extends up to 9×9 pixels.
## 5.2 Class Specification
class FieldDependentIPC:
"""
Asymmetric, field-position-dependent IPC convolution.

Kernel structure (9x9 max, but power falls off rapidly):
- Nearest neighbors (1-pixel): alpha_h, alpha_v (asymmetric)
- Diagonal neighbors: alpha_d (typically 0.3x nearest)
- Second-nearest (2-pixel): alpha_2 (typically 0.1x nearest)
- Third-nearest and beyond: negligible but included

Field dependence: Kernels are pre-computed on a grid of
SCA positions and bilinearly interpolated to the stamp's
detector coordinates.
"""

def __init__(self,
config: DetectorConfig,
sca_id: int,
field_position: tuple[float, float]):
"""
Args:
config: Detector configuration.
sca_id: Sensor chip assembly ID (1-18).
field_position: (x, y) position on detector
in pixel coordinates, used to interpolate
the field-dependent kernel.
"""

def build_kernel(self) -> np.ndarray:
"""
Construct the 9x9 IPC kernel for this field position.

Returns:
2D array [9, 9] normalized so sum = 1.0.
Center pixel = 1 - sum(couplings).
"""

def apply(self,
image_e: np.ndarray
) -> np.ndarray:
"""
Apply IPC convolution to a detector-frame image.
Uses scipy.signal.fftconvolve for efficiency.

Args:
image_e: 2D array [ny, nx] in electrons.

Returns:
IPC-convolved image, same shape. Boundary:
'same' mode with zero-padded edges (stamps
are already padded by GalSim rendering).
"""

def deconvolve(self,
image_e: np.ndarray,
n_iterations: int = 4
) -> np.ndarray:
"""
Iterative IPC deconvolution (for validation only).
Uses the Jansson-Van Cittert method.
"""
## 5.3 Calibration Data (smig/sensor/calibration/ipc_kernels.py)
IPC kernel coefficients are stored in an HDF5 calibration file with one dataset per SCA. Each dataset is a 3D array of shape (n_grid_y, n_grid_x, 81) where 81 = 9×9 flattened kernel coefficients, and n_grid is the spatial sampling grid (typically 16×16 across the 4096×4096 detector). The loader performs bilinear interpolation to the requested field position.
## 5.4 Unit Test Contract

# 6. Dynamic Persistence (smig/sensor/persistence.py)
## 6.1 Physics Background
Persistence in HgCdTe detectors arises from charge trapping in the depletion region. When a pixel is exposed to high illumination, a fraction of the generated charge is captured by crystal defects. This trapped charge is subsequently released on timescales ranging from seconds to thousands of seconds, producing a ghost signal in later exposures. For Roman's 15-minute cadence, persistence from a bright star or cosmic ray hit in exposure N will contaminate exposures N+1 through approximately N+5.
The v1 implementation had no persistence model. The v2 model implements a two-component exponential decay with independent fast (τ_short ≈ 100s) and slow (τ_long ≈ 1000s) time constants, each with an amplitude proportional to the illumination history above a trapping threshold.
## 6.2 Class Specification
class DynamicPersistence:
"""
History-aware persistence model with dual-exponential
temporal decay. Maintains per-pixel illumination history
across epochs within an event.

Model:
P(x, y, t) = sum_k [ A_short * f(I_k) * exp(-(t-t_k)/tau_s)
+ A_long  * f(I_k) * exp(-(t-t_k)/tau_l) ]
where k indexes all previous exposures, I_k is the peak
illumination in that exposure, and f(I) is the trapping
efficiency function (zero below threshold, power-law above).
"""

def __init__(self, config: DetectorConfig):

def update_history(self,
image_e: np.ndarray,
timestamp_mjd: float) -> None:
"""
Record the illumination state of this exposure.
Only pixels exceeding the trapping threshold
(default: 50% of full well) contribute.

Internally prunes history entries older than
5 * tau_long to bound memory usage.
"""

def compute_persistence_signal(self,
current_time_mjd: float
) -> np.ndarray:
"""
Compute the persistence ghost signal at the current
epoch by summing decayed contributions from all
prior exposures in history.

Returns:
2D array [ny, nx] in electrons to add to the
current frame before readout.
"""

def reset(self) -> None:
"""Clear all history. Call between events."""
## 6.3 Unit Test Contract

# 7. Nonlinearity and Saturation (smig/sensor/nonlinearity.py)
## 7.1 Two-Level Nonlinearity Model
The v2 model separates nonlinearity into two physically distinct components:
Integral Non-Linearity (INL) at the ADC level: A systematic deviation between the true input voltage and the digitized output, modeled as a polynomial correction applied after voltage-to-ADU conversion. This affects all pixels identically and is calibrated from flat-field exposures.
Pixel-level nonlinearity near full well: As a pixel approaches full well capacity, the depletion region narrows, reducing quantum efficiency and altering the charge-to-voltage conversion gain. This effect is flux-dependent and is modeled as a polynomial applied to the accumulated charge in each pixel at each ramp sample.
## 7.2 Saturation Handling (Reviewer-Requested)
Multiple reviewers flagged the complete absence of saturation handling in v1 as a critical gap. High-magnification caustic peaks on bright sources (W146 < 16 mag at peak A > 100) will saturate Roman's detector. The v2 module implements:
Hard saturation clipping: Pixel values exceeding full_well_e are clipped. The corresponding ramp samples are flagged.
Saturation mask output: A boolean mask identifying all pixels that reached saturation in any ramp sample. This mask is a first-class output of the detector chain and propagates to the training data as a quality channel.
Partial saturation recovery: For pixels that saturate partway through the ramp (common for bright sources), the slope fit uses only the unsaturated reads. The number of usable reads is recorded in the provenance log.
Training label policy: Events where the magnification peak causes saturation are retained as hard negatives in the training set, not filtered. The classifier must learn to recognize saturated caustic peaks as genuine high-magnification events rather than detector artifacts. This directly addresses the reviewer finding that saturation at the caustic peak is physically expected and operationally critical.
## 7.3 Class Specification
class NonLinearityModel:
"""
Two-component nonlinearity: ADC-level INL + pixel NL.
Also handles saturation flagging and partial ramp recovery.
"""

def __init__(self, config: DetectorConfig):

def apply_pixel_nl(self,
charge_e: np.ndarray
) -> np.ndarray:
"""
Apply pixel-level NL to accumulated charge.
Polynomial: V_out = c0*Q + c1*Q^2 + c2*Q^3
where Q = charge_e / full_well (normalized).
Returns corrected charge in electrons.
"""

def apply_adc_inl(self,
voltage_adu: np.ndarray
) -> np.ndarray:
"""
Apply ADC integral nonlinearity.
"""

def flag_saturation(self,
charge_e: np.ndarray
) -> np.ndarray:
"""
Returns boolean mask where charge exceeds
saturation_flag_threshold * full_well_e.
"""

def clip_and_report(self,
ramp_cube: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
"""
Clip saturated ramp samples, flag them, and
report the last usable read index per pixel.

Returns:
clipped_ramp: Ramp with saturated reads clipped.
sat_mask: [ny, nx] bool — True if any read saturated.
last_good_read: [ny, nx] int — index of last unsaturated read.
"""

# 8. MultiAccum Readout (smig/sensor/readout.py)
## 8.1 Why MultiAccum Matters
Roman's WFI uses a non-destructive up-the-ramp (MultiAccum) readout rather than the correlated double sampling (CDS) assumed in v1. In MultiAccum mode, the detector is read N times during the exposure without resetting. The flux rate is estimated by fitting a slope to the accumulated signal versus time. This provides three critical advantages: it reduces effective read noise by a factor of approximately √(6(N-1)/N(2N-1)), it enables identification and rejection of cosmic ray hits that corrupt individual reads, and it provides partial saturation recovery by fitting the slope using only unsaturated reads.
## 8.2 Class Specification
class MultiAccumSimulator:
"""
Simulates up-the-ramp non-destructive readout.

The input is an ideal per-exposure image (total electrons
accumulated over the full exposure). This is distributed
linearly across N reads (assuming constant flux rate),
with per-read noise injected at each sample.
"""

def __init__(self, config: DetectorConfig):

def simulate_ramp(self,
total_signal_e: np.ndarray,
rng: np.random.Generator
) -> np.ndarray:
"""
Generate the full ramp cube [n_reads, ny, nx].

Each read k accumulates signal:
S_k = (total_signal_e / n_reads) * (k + 1)
+ dark_current * frame_time * (k + 1)
+ read_noise_realization_k

Poisson noise is applied to the incremental signal
between reads (not to accumulated signal).
"""

def fit_slope(self,
ramp_cube: np.ndarray,
last_good_read: np.ndarray | None = None
) -> np.ndarray:
"""
Fit slope to ramp using least-squares.

If last_good_read is provided (from saturation
flagging), uses only reads up to that index per pixel.
Cosmic-ray-affected reads are identified by >5-sigma
jumps in adjacent read differences and excluded.

Returns:
rate_image [ny, nx] in electrons per second.
"""

# 9. Correlated Noise Models (smig/sensor/noise/)
## 9.1 1/f Noise (correlated.py)
H4RG detectors exhibit correlated 1/f noise that manifests as horizontal banding across the image. This noise arises in the readout amplifier chain and has a power spectral density that scales as 1/fᵅ with α ≈ 1.0. It is not white noise; adjacent rows are correlated, and the banding pattern evolves between reads.
class OneOverFNoise:
"""
1/f correlated read noise with horizontal banding.

Implementation: Generate a 1D power spectrum with
P(f) ~ f^(-alpha), then inverse FFT to produce a
correlated noise vector per row. Each row within a
single read receives the same noise offset (banding),
but the pattern changes between reads.
"""

def __init__(self, config: DetectorConfig):

def generate(self,
shape: tuple[int, int],
rng: np.random.Generator
) -> np.ndarray:
"""
Generate one realization of 1/f banding.
Returns 2D array [ny, nx] in electrons.
"""
## 9.2 Random Telegraph Signal (correlated.py)
A small fraction of pixels (≈0.2%) exhibit Random Telegraph Signal (RTS) noise: the dark current stochastically switches between two or more discrete levels, producing anomalously high variance in the ramp for those pixels. RTS pixels can be misidentified as variable sources by the classifier if not modeled in training.
class RTSNoise:
"""
Random telegraph signal noise on a fixed set of pixels.

At initialization, randomly selects rts_pixel_fraction
of all pixels. Each selected pixel receives a two-state
telegraph switching model with random amplitude and
switching rate.
"""

def __init__(self,
config: DetectorConfig,
stamp_shape: tuple[int, int],
rng: np.random.Generator):

def apply_to_ramp(self,
ramp_cube: np.ndarray,
rng: np.random.Generator
) -> np.ndarray:
"""
Inject RTS noise into the ramp cube in-place.
Each affected pixel switches state independently
between reads with a Poisson-distributed rate.
"""
## 9.3 Clustered Cosmic Rays (cosmic_rays.py)
The v1 model injected cosmic rays as single-pixel hits. At L2, the primary cosmic ray population is Galactic cosmic rays (GCRs), which deposit charge along tracks spanning multiple pixels with characteristic morphology (straight tracks for minimum-ionizing particles, clusters for nuclear interactions). The v2 model generates physically motivated track shapes.
class ClusteredCosmicRayInjector:
"""
Physically motivated cosmic ray hit injection.

Hit types:
- Single pixel (30% of hits): isolated delta
- Linear tracks (50%): straight line, 2-8 pixels,
random orientation, energy proportional to path length
- Clusters (15%): nuclear interaction spallation,
3-12 pixels in compact group
- Snowballs (5%): Roman-specific low-energy deposition
events producing circular charge deposits
"""

def __init__(self, config: DetectorConfig):

def inject_into_ramp(self,
ramp_cube: np.ndarray,
exposure_time_s: float,
stamp_area_cm2: float,
rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
"""
Inject CRs into random reads of the ramp.
CRs affect only the read in which they occur
and all subsequent reads (charge is permanent).

Returns:
modified_ramp: Ramp with CR charge added.
cr_mask: [ny, nx] bool — True if any CR hit.
"""

# 10. Charge Diffusion and Brighter-Fatter (smig/sensor/charge_diffusion.py)
Charge diffusion and the brighter-fatter effect (BFE) are physically distinct from IPC but produce qualitatively similar spreading. Charge diffusion is the lateral migration of photo-generated electrons during collection, broadening the effective PSF. The BFE is a dynamic effect: as a pixel accumulates charge, the resulting electric field deflects newly arriving photons toward neighboring pixels, making bright stars appear spatially broader than faint ones. The BFE must be applied before IPC since it operates on charge, whereas IPC operates on voltage.
class ChargeDiffusionModel:
"""
Static diffusion kernel + dynamic brighter-fatter.

Static diffusion: Gaussian kernel with sigma proportional
to detector thickness / depletion depth. Applied once.

Brighter-fatter: Iterative charge redistribution.
For each pixel, the fraction of charge deflected to
neighbors is proportional to the accumulated charge
in that pixel (and inversely proportional to full well).
"""

def __init__(self, config: DetectorConfig):

def apply_static_diffusion(self,
image_e: np.ndarray
) -> np.ndarray:

def apply_bfe(self,
image_e: np.ndarray,
n_iterations: int = 3
) -> np.ndarray:
"""
Iterative BFE. Each iteration redistributes charge
from bright to neighboring pixels proportional to
local charge fraction of full well.
"""

def apply(self, image_e: np.ndarray) -> np.ndarray:
"""Combined diffusion + BFE."""

# 11. Provenance Tracking (smig/provenance/)
Every event processed through the detector chain produces a JSON sidecar file that records all parameters, random seeds, software versions, and processing decisions. This addresses the reviewer finding that v1 lacked complete reproducibility metadata.
class ProvenanceRecord(BaseModel):
"""Immutable provenance for one processed epoch."""
event_id: str
epoch_index: int
timestamp_mjd: float
pipeline_version: str  # Git commit hash
container_digest: str  # Docker/Singularity image SHA
config_hash: str       # SHA256 of frozen DetectorConfig
rng_state: str         # np.random.Generator bit state

# Per-module flags
ipc_applied: bool
ipc_kernel_hash: str
persistence_applied: bool
persistence_history_depth: int
nl_applied: bool
n_saturated_pixels: int
n_partial_saturation_pixels: int
n_cosmic_ray_hits: int
cr_types: dict[str, int]  # {'single': N, 'track': M, ...}
n_rts_active_pixels: int
slope_fit_method: str  # 'least_squares' | 'optimal_weighting'
n_reads_used_median: float
peak_memory_mb: float

class ProvenanceTracker:
"""Accumulates records and writes JSON sidecars."""

def log_epoch(self, record: ProvenanceRecord) -> None:
def write_sidecar(self, output_path: Path) -> None:
def verify_reproducibility(self,
sidecar_path: Path,
recomputed: ProvenanceRecord
) -> bool:

# 12. Integration Tests and Acceptance Criteria
The following integration tests verify the full detector chain end-to-end. All must pass within the 32 GB memory constraint on a single machine before the pipeline is approved for cluster deployment.

# 13. Implementation Priority and Dependencies
Modules must be implemented in the following order due to signal-chain dependencies and testing prerequisites:
Total estimated effort for Phase 1: approximately 31 engineering days (6–7 weeks at standard pace). Modules 3–6 can be developed in parallel by separate engineers once the config schema is finalized.
| Review Finding | Severity | Resolving Module |
| --- | --- | --- |
| Static 3×3 IPC kernel outdated | Critical | smig.sensor.ipc.FieldDependentIPC |
| No persistence model or static only | Critical | smig.sensor.persistence.DynamicPersistence |
| Saturation handling completely absent | Critical | smig.sensor.nonlinearity.NonLinearityModel |
| MultiAccum readout not modeled | High | smig.sensor.readout.MultiAccumSimulator |
| No correlated noise (1/f, RTS) | High | smig.sensor.noise.correlated |
| CR morphology underspecified | Medium | smig.sensor.noise.cosmic_rays |
| PSF jitter value unverified (14 vs 5 mas) | High | Config schema (verified value: 5 mas/axis) |
| SAA reference wrong for L2 | Medium | Cadence gap model updated (safe-mode/downlink) |
| DeltaFunction vs finite source gap | Critical | smig.rendering.source (Phase 2, flagged here) |
| Compute budget arithmetic error | Critical | Corrected in config + budget appendix |
| Parameter | v1 Value | v2 Value | Source |
| --- | --- | --- | --- |
| Jitter RMS per axis | 14 mas | 5 mas | Roman Pointing Requirements Doc (GSFC-ROMAN-SYS-REQ-0004) |
| Read noise (effective) | 12 e⁻ (CDS) | 5 e⁻ (multi-read) | H4RG-10 multi-read slope fitting specification |
| Cadence gap cause | SAA passages | Safe-mode / downlink | Roman at L2, not LEO; SAA is irrelevant |
| Crowding density unit | per pixel area | per arcmin² > W146 limit | Penny et al. (2019) GBTDS simulation |
| Test | Condition | Pass Threshold |
| --- | --- | --- |
| Kernel normalization | Sum of all kernel elements | == 1.0 to machine precision |
| Kernel asymmetry | α_h ≠ α_v | |(α_h - α_v) / α_h| ∈ [0.05, 0.30] |
| Flux conservation | Sum of convolved image == sum of input | Relative error < 10⁻¹² |
| Deconvolution round-trip | Apply then deconvolve | RMS residual < 0.1% of peak |
| Field dependence | Kernels at (100,100) vs (3900,3900) | Not identical (coefficient diff > 1%) |
| Test | Condition | Pass Threshold |
| --- | --- | --- |
| Decay monotonicity | Persistence signal decreases with time gap | Strictly decreasing for fixed illumination |
| Below-threshold immunity | Illumination < 50% full well | Persistence signal == 0 |
| History pruning | 100 exposures recorded, memory measured | Memory < 2× single-frame size |
| Dual-component shape | Fit decay curve to two exponentials | Recovered τ within 5% of config values |
| Test Name | Description | Pass Criterion |
| --- | --- | --- |
| Full-chain smoke | Process 10 events (200 epochs each, 64×64 stamp) through all modules | Completes without error; peak memory < 8 GB |
| Noise statistics | Process 1000 dark frames (zero input signal). Measure pixel noise distribution. | Mean ≈ dark_current × t_exp; std matches effective read noise ±10% |
| Saturation recovery | Inject a source at 120% full well. Verify partial ramp fitting. | Recovered rate within 5% of input for unsaturated reads |
| Persistence decay | Flash full well in epoch 0. Measure ghost in epochs 1–5. | Decay follows dual-exponential within fitted τ ±10% |
| CR rejection | Inject known CR in read 4 of 8. Run slope fit with CR rejection. | Recovered rate within 2% of CR-free rate |
| 1/f banding structure | Compute row-by-row correlation in 100 dark frames. | Autocorrelation length > 1 row (not white noise) |
| IPC + NL + BFE ordering | Swap BFE and IPC order. Compare output to correct order. | Results must differ (proves order matters and is enforced) |
| Provenance round-trip | Process event, reload sidecar, reprocess with same seeds. | Bit-identical output |
| Memory ceiling | Process 50 events sequentially, monitoring RSS. | Peak RSS never exceeds 32 GB |
| Order | Module | Dependency | Estimated Effort |
| --- | --- | --- | --- |
| 1 | config/schemas.py | None (foundation) | 2 days: Pydantic models + YAML defaults |
| 2 | provenance/ | Config schemas | 1 day: dataclass + JSON serializer |
| 3 | charge_diffusion.py | Config schemas | 3 days: BFE iterative solver + tests |
| 4 | ipc.py + calibration/ | Config schemas | 3 days: kernel interpolation + HDF5 loader |
| 5 | persistence.py | Config schemas | 3 days: history tracking + dual-exp model |
| 6 | nonlinearity.py | Config schemas | 2 days: polynomial NL + saturation handler |
| 7 | readout.py | nonlinearity (for saturation) | 4 days: ramp generation + slope fitting + CR flagging |
| 8 | noise/correlated.py | readout (injected per-read) | 3 days: 1/f PSD generation + RTS model |
| 9 | noise/cosmic_rays.py | readout (injected into ramp) | 3 days: track morphology + snowball model |
| 10 | detector.py (orchestrator) | All above modules | 3 days: chain wiring + memory management + GC |
| 11 | validation/ (integration) | Orchestrator | 4 days: all tests in Section 12 |