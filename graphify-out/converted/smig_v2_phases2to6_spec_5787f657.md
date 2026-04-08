<!-- converted from smig_v2_phases2to6_spec.docx -->


SMIG v2 — Phases 2–6 Implementation Specification
Optics, Physics Engine, Classifier, Validation & Operations
Incorporating All v1 Review Findings and Architectural Suggestions
v2.0-alpha  —  April 2026

# A. Cross-Cutting: Requirement Traceability Matrix
Multiple reviewers identified that v1 lacked a formal mapping from science requirements to pipeline stages, acceptance tests, and pass/fail thresholds. This section establishes that traceability as a first-class architectural artifact. Every module in Phases 2–6 traces back to this matrix.

# B. Cross-Cutting: Prior Separation Policy
Reviewers consistently flagged that v1 conflated the astrophysical generation prior, the training class balance, and inference-time probability interpretation. This section formalizes the three-tier prior architecture.
## B.1 Generation Prior (Astrophysical)
Events are drawn from physically realistic distributions: the Kroupa IMF, Cassan et al. (2012) planet occurrence rates, empirical Bulge stellar densities, and scenario-based FFP rates. This prior reflects the true occurrence rates of microlensing event classes in the Roman GBTDS field. The generation prior produces a highly imbalanced dataset where 2L1S events constitute roughly 1–5% of all events, 1L2S approximately 3–8%, and the vast majority are 1L1S or non-microlensing variables.
## B.2 Training Prior (Reweighted)
The training set is class-balanced by oversampling rare classes (2L1S) and undersampling common classes (contaminants). The target training composition is 500K events per major class (2L1S, 1L1S, 1L2S, contaminants). This reweighting is documented in the dataset manifest and is purely a training optimization; it does not imply that these classes occur at equal rates in nature.
## B.3 Inference-Time Calibration (Prior Correction)
The classifier's raw softmax outputs are trained on balanced data and therefore do not represent calibrated astrophysical posteriors. Before deployment, the model undergoes two calibration steps:
Temperature scaling: A single scalar T is learned on a prevalence-weighted validation set to minimize negative log-likelihood. The calibrated probability is softmax(logits / T). This corrects overconfidence without changing class rankings.
Threshold governance: The trigger threshold is not a fixed P > 0.5 but is derived from a cost matrix that balances science yield (false negatives = missed planets) against Stage B compute cost (false positives = wasted GPU-hours). The threshold is field-dependent and magnitude-dependent: bright sources in high-density fields receive a lower threshold (more aggressive triggering) because their centroid signals are more reliable.

# C. Cross-Cutting: Data Leakage Prevention Policy
With 2M synthetic events and heavy augmentation, data leakage across train/validation/test splits is the single most likely cause of inflated performance metrics. This section defines the leakage prevention contract.
Split unit: The atomic unit for splitting is the base event, defined by its unique event_id and the Stage 1 physical parameter vector. All augmented variants of a single base event (cadence dropout, photometric rescaling, PSF variation, geometric transforms) must reside in the same split. Splitting occurs before any augmentation.
Starfield isolation: Background starfield scenes are generated from independent random seeds per sky tile. No two events in different splits may share the same background starfield seed. The sky tile seed is recorded in the provenance sidecar and checked during split validation.
Parameter proximity guard: Events whose physical parameters (t_E, u_0, s, q) differ by less than 5% in all dimensions simultaneously are assigned to the same split to prevent near-duplicate leakage across nuisance parameters.
Validation script: A mandatory pre-training script (validate_splits.py) checks all three conditions and fails with a non-zero exit code if any violation is detected. Training cannot proceed without a passing split validation.

# D. Cross-Cutting: Ablation Plan
Multiple reviewers questioned whether pixel-level image cubes are justified over lighter baselines. The ablation plan provides the experimental design to answer this definitively.
Ablation A3 (DIA-only) is the primary deployment target. If A3 performance equals or exceeds A5 (dual-stream), the simpler architecture is preferred. Ablation A1 is the mandatory control that justifies the entire project.

# E. Cross-Cutting: Reproducibility Contract
Every artifact produced by SMIG v2 must be bit-for-bit reproducible given the same configuration. This section specifies the reproducibility infrastructure.
Immutable configuration: All pipeline parameters are defined in Pydantic v2 frozen models. A SHA-256 hash of the serialized config is embedded in every output file. Changing any parameter changes the hash and produces a new lineage.
Deterministic RNG: Each event receives a deterministic seed derived from a master seed and the event_id: seed_event = hash(master_seed || event_id). Each pipeline stage derives its own sub-seed: seed_stage = hash(seed_event || stage_name). This ensures that adding a new event does not change the seeds of existing events, and that reprocessing a single event reproduces it exactly regardless of batch ordering.
Container pinning: The normative execution environment is a Docker image with a pinned digest (not a mutable tag). The Dockerfile, conda lockfile, and pip freeze output are stored alongside the code in version control. The container digest is recorded in every provenance sidecar.
Workflow orchestration: The pipeline is managed by Snakemake with file-level dependency tracking. Each stage produces a manifest file listing all outputs with their SHA-256 checksums. Re-running a stage with identical inputs produces identical outputs (verified by manifest comparison). DVC tracks large intermediate artifacts (HDF5, FITS) with content-addressable storage.
Dataset manifest: The final training dataset includes a machine-readable manifest (JSON) listing every event, its split assignment, its provenance sidecar path, the master seed, pipeline version, and container digest. This manifest is the single source of truth for the dataset and is versioned alongside model checkpoints.

# 1. Phase 2: Optical Modeling and Scene Rendering
## 1.1 Scope and Reviewer Findings Addressed
Phase 2 replaces the v1 optical simulation (which used WebbPSF with unverified jitter and DeltaFunction source rendering) with a physically accurate, field-varying PSF model using STPSF, resolves the critical finite-source rendering gap, and implements sensor-level blending. It also corrects the DIA reference template construction.
## 1.2 Module: smig/optics/psf.py — STPSFProvider
STPSF (Space Telescope PSF, formerly WebbPSF) is the authoritative source for Roman WFI PSFs. The provider computes wavelength-dependent, field-position-varying PSFs using Zernike polynomial wavefront error maps. The W146 filter spans 0.93–2.00 μm, which means the PSF changes shape significantly across the bandpass; a monochromatic PSF at 1.5 μm is insufficient.
class STPSFProvider:
"""
Field-varying, polychromatic PSF generator using STPSF.

Precomputes PSFs on a grid of (SCA, field_position,
wavelength) and caches them. At render time, the
polychromatic PSF is assembled by weighting monochromatic
PSFs by the source SED * filter throughput * QE.
"""

def __init__(self,
filter_name: str = 'W146',
oversample: int = 4,
n_wavelengths: int = 10,
jitter_rms_mas: float = 5.0,
cache_dir: Path | None = None):

def get_psf(self,
sca_id: int,
field_position: tuple[float, float],
source_sed: str = 'flat'
) -> galsim.InterpolatedImage:
"""
Returns GalSim-compatible PSF for this position.
Includes jitter convolution (Gaussian, 5 mas/axis).
The PSF is 4x oversampled and normalized to unit flux.
"""

def get_psf_at_wavelength(self,
sca_id: int,
field_position: tuple[float, float],
wavelength_um: float
) -> np.ndarray:
"""Monochromatic PSF at specific wavelength."""
## 1.3 Module: smig/rendering/source.py — FiniteSourceRenderer
This module resolves the most critical physics-simulation gap identified by all reviewers: the v1 pipeline rendered the microlensed source as a DeltaFunction (point source) convolved with the PSF, while Stage 2 computed magnification accounting for the finite angular size of the source. For source radii ρ* > 0.01 θ_E interacting with a caustic, the resolved source disk produces an image morphology that differs from a point source with the same total flux.
The solution depends on the regime:
Unresolved regime (ρ* < 3 pixels ≈ 0.33 arcsec, the vast majority of events): The source is physically unresolved on Roman's pixel grid. The Stage 2 magnification and centroid already encode the finite-source physics. Rendering as DeltaFunction(flux=f_s * A(t)) at the centroid offset is physically correct. No change from v1.
Marginally resolved regime (ρ* > 3 pixels, rare giant sources at extreme magnification): The source disk subtends multiple pixels and must be rendered as a limb-darkened disk profile. The renderer creates a GalSim SBProfile using the limb-darkening coefficients from Stage 1, assigns it the Stage 2 magnification, and convolves with the PSF. This is computationally expensive and applies to fewer than 0.1% of events.
class FiniteSourceRenderer:
"""
Renders the microlensed source with correct finite-source
treatment depending on angular size regime.
"""

UNRESOLVED_THRESHOLD_ARCSEC = 0.33  # ~3 Roman pixels

def __init__(self, psf_provider: STPSFProvider):

def render_source(self,
flux_e: float,
centroid_offset_pix: tuple[float, float],
rho_star_arcsec: float,
limb_darkening_coeffs: tuple[float, float],
psf: galsim.InterpolatedImage,
stamp: galsim.Image
) -> None:
"""
Render source onto stamp in-place.
Dispatches to point-source or disk based on rho_star.
"""
## 1.4 Module: smig/rendering/crowding.py — CrowdedFieldRenderer
Reviewer finding: blending must operate at the raw sensor level (overlapping PSFs + charge diffusion from Phase 1), not just aggregated fluxes. The v2 crowding model renders every neighbor star individually through the full PSF + Phase 1 detector chain, producing physically correct blend morphology including IPC-induced flux coupling between neighbors.
class CrowdedFieldRenderer:
"""
Renders all sources in a stamp through the same PSF
and detector chain. Neighbor fluxes contribute to
IPC, persistence, and saturation of the target pixel.

Neighbor catalog is drawn from Galaxia/SPISEA for the
specific sightline, filtered to W146 < 26 mag within
the stamp FOV. Stellar multiples (binaries, triples)
are natively included in the population synthesis.

Corrected density: ~1.5e4 stars/arcmin² above W146=26
in the densest Bulge fields, yielding 30-200 detectable
sources per 64x64 stamp (7x7 arcsec FOV).
"""

def __init__(self,
neighbor_catalog: pd.DataFrame,
psf_provider: STPSFProvider,
stamp_size: int = 64,
pixel_scale: float = 0.11,
brightness_cap_mag: float | None = None):
"""
brightness_cap_mag: If set, neighbors brighter than
this limit generate saturated-neighbor artifacts
(persistence, charge bleed). If None, no cap is
applied and saturated neighbors are included.
"""

def render_static_field(self,
psf: galsim.InterpolatedImage
) -> np.ndarray:
"""
Render all static neighbors onto a blank stamp.
This is the constant component across all epochs.
Computed once and cached per event.
"""
## 1.5 Module: smig/rendering/dia.py — Corrected DIA Pipeline
Reviewer consensus: the v1 reference template (50 coadded noise realizations of the same baseline with identical PSF) was unrealistic. Real Roman references will be deep stacks of many epochs with variable PSF, background, and registration. The v2 DIA module addresses this.
Reference construction: The reference image is built from 20–50 baseline epochs, each rendered with an independently drawn PSF realization (varying focus position and jitter) and sky background level. The coadd uses inverse-variance weighting, producing a reference whose noise covariance structure matches what a real pipeline would produce.
Subtraction method for training: A fixed-kernel convolution matching (Alard & Lupton 1998 style) is used for training data generation because it is computationally cheap and sufficient for a well-characterized space-based PSF. SFFT (spatially varying) is reserved for validation runs on a subset of events to quantify the impact of kernel choice on classifier performance.
Context stamp: To address reviewer concerns about SFFT instability on small stamps, the DIA subtraction operates on a 256×256 pixel context stamp. The central 64×64 crop is extracted after subtraction for the training cube. This provides adequate support for the convolution kernel.

# 2. Phase 3: Physics Engine Unification and Orbital Dynamics
## 2.1 microlux Unification
The v1 architecture bifurcated the physics engine between VBMicrolensing (CPU, high-precision) and caustics (JAX, GPU-batched). Multiple reviewers flagged the need for cross-backend agreement testing, and the compute budget showed the CPU path as a bottleneck. The suggestion to unify on microlux (Ren & Zhu, 2025) is adopted.
microlux implements Bozza's adaptive contour integration algorithm natively in JAX, providing the numerical stability of VBMicrolensing with the GPU batching and automatic differentiation of JAX. This eliminates the bifurcated backend, the cross-backend agreement testing burden, and the CPU bottleneck.
class MicroluxEngine:
"""
Unified GPU-accelerated microlensing physics engine.
Replaces the bifurcated VBMicrolensing / caustics split.

Capabilities:
- Binary lens magnification via adaptive contour integration
- Finite source size with limb darkening (linear, quadratic)
- Flux-weighted astrometric centroid computation
- Exact gradient computation via JAX autodiff
- Batch processing: ~10,000 epoch evaluations/second on A100
- Automatic precision escalation for resonant topologies

VBMicrolensing is retained as a validation reference only,
not as a production backend. A subset of 1000 events is
cross-validated against VBMicrolensing with acceptance
threshold |Delta_A| / A < 10^-4.
"""

def __init__(self,
precision: str = 'adaptive',
device: str = 'gpu',
store_gradients: bool = False):

def compute_magnification_batch(self,
s: jnp.ndarray, q: jnp.ndarray,
y1: jnp.ndarray, y2: jnp.ndarray,
rho: jnp.ndarray,
limb_u: jnp.ndarray | None = None
) -> jnp.ndarray:
"""Batch magnification for N events x M epochs."""

def compute_centroid_batch(self, ...) -> tuple[jnp.ndarray, jnp.ndarray]:
"""Batch centroid shifts."""

def classify_topology(self, s: float, q: float) -> str:
"""Returns 'close', 'resonant', or 'wide'."""
## 2.2 BAGLE Orbital Dynamics
For events with t_E > 20 days, orbital motion changes the instantaneous binary separation s(t) and orientation α(t). The v1 spec called for full Keplerian integration for all such events. The suggestion to use BAGLE's linear and accelerated orbital approximations is adopted.
Routing policy: Events where P_orb / t_E > 10 (orbital period much longer than event timescale) use BAGLE's linear approximation: ds/dt and dα/dt are constant, requiring only 2 extra parameters. Events with 3 < P_orb / t_E < 10 use the accelerated approximation (4 extra parameters). Only events with P_orb / t_E < 3 (rare short-period binaries) use full Keplerian integration (5 extra parameters: P, e, i, Ω, ω). This reduces the median orbital computation cost by approximately 80%.
## 2.3 Corrected Terminology and Labeling
All reviewers flagged the v1 terminology (BLPL, BSPL) as non-standard and internally contradictory. The v2 pipeline adopts the community-standard notation:
## 2.4 Close/Wide Degeneracy in Training Labels
A reviewer correctly identified that events with separation s and 1/s produce nearly identical light curves, creating contradictory training labels. The v2 labeling policy resolves this:
The Stage 1 catalog stores both the physical s and its degenerate partner s' = 1/s. The classifier is trained with a degenerate-aware label: the training target for the separation parameter is a two-component Gaussian mixture (one mode at log(s), one at log(1/s)) rather than a single point label. This directly teaches the classifier that both solutions are valid and prevents it from learning to reject the equally probable degenerate solution.
## 2.5 Xallarap for 1L2S Events
Reviewer finding: xallarap (binary source orbital motion) was entirely absent from v1 despite 1L2S being a listed event class. The v2 pipeline injects xallarap into 50% of 1L2S training events using BAGLE's binary-source orbital model. The xallarap signal is a periodic modulation of the centroid and magnification that can mimic parallax, making it essential training data for the classifier to learn the distinction.
## 2.6 Multi-Window Events
Reviewer finding: Roman's GBTDS has 7 observing windows separated by months-long gaps. Events with t_E > 72 days span multiple windows. The v1 pipeline assumed a single contiguous window.
The v2 pipeline generates 5% of training events as multi-window events. These events have the full physics (parallax + orbital motion) computed across the gap, but the image cubes contain only the epochs within observing windows. The gap regions are represented as missing data in the sequence, which the Neural CDE architecture handles natively without imputation.

# 3. Phase 4: Domain Adaptation and Augmentation
## 3.1 Physics-Aware Augmentation (Corrected)
Several v1 augmentations were flagged by reviewers as potentially breaking physical consistency. The v2 augmentation policy separates augmentations into two tiers:
Pre-render augmentations (safe, applied in Stage 1): Source magnitude variation (equivalent to drawing different source stars), blend fraction variation, trajectory angle rotation. These modify the physics inputs and produce self-consistent outputs.
Post-render augmentations (constrained, applied after Stage 3): Cadence dropout (remove 5–30% of epochs; attributed to safe-mode and downlink gaps, not SAA), geometric flips restricted to 180° rotation only (preserving parallax direction), and sub-pixel jitter perturbations (σ = 0.01 pixels). Photometric rescaling is moved to the pre-render tier because post-render rescaling breaks Poisson statistics and saturation behavior, as a reviewer correctly identified.
Flip augmentation constraint: A reviewer noted that arbitrary flips change the handedness of caustic crossing sequences and corrupt centroid training signals. The v2 policy restricts geometric augmentations to 180° rotations (which preserve the source-caustic geometry) and reflections about the binary axis (which are a true physical symmetry). Random flips about arbitrary axes are prohibited.
## 3.2 Contaminant Budget (Corrected)
Reviewers flagged that the v1 contaminant fractions were internally inconsistent (10–15% per class summing past 100%). The v2 budget is:
## 3.3 Domain Adaptation: Noise-Domain Transfer Only
The suggestion to use CycleGAN for sim-to-real hardening is adopted with a critical restriction: generative models are used only for noise texture transfer, never for generating microlensing event morphology. The physics of the event (magnification, centroid, caustic structure) always comes from the microlux engine. The generative model maps the noise realization from the simulated detector chain onto an empirical noise distribution learned from real detector data.
Training data: Before Roman launches, the CycleGAN is trained on JWST NIRCam short-wavelength imaging (similar H2RG detector family) as a proxy for Roman noise characteristics. After Roman commissioning data becomes available, the generative model is retrained on actual Roman flat fields and dark frames. This is the primary sim-to-real mitigation pathway.
Validation: The generative model is validated by comparing pixel-level noise statistics (power spectral density, pixel-pixel covariance, 1/f banding structure) between transferred synthetic images and real detector data. If the PSD diverges by more than 20% at any spatial frequency, the generative model is rejected and the pipeline falls back to physics-only noise injection.

# 4. Phase 5: Classifier Architecture (Stage A + Stage B)
## 4.1 Stage A: Trigger Classifier
The v2 classifier architecture addresses the following reviewer findings: ImageNet pretraining is questionable for single-channel NIR data; bidirectional LSTMs are non-causal for streaming inference; the Stage A output does not provide the topology information Stage B needs; variable sequence lengths are not handled; and probability calibration is absent.
Primary architecture: Neural Controlled Differential Equation (Neural CDE) with a spatial CNN encoder. This replaces the ConvLSTM and directly addresses the irregular sampling problem flagged by multiple reviewers. The Neural CDE uses natural cubic spline interpolation of the image feature sequence, allowing the hidden state to evolve continuously over time. Data gaps (cadence dropout, multi-window events) are handled natively without imputation.
class SpatiotemporalTrigger(nn.Module):
"""
Stage A trigger classifier.

Architecture:
1. Spatial encoder: EfficientNet-B0 (pretrained on
astronomical images, not ImageNet) processes each
64x64 stamp independently -> 256-dim feature vector.
2. Temporal encoder: Neural CDE with 128-dim hidden state
operating on the continuous interpolation of the
spatial feature sequence.
3. Classification head: Two output heads:
a) Class head: 4-class softmax (1L1S, 2L1S, 1L2S, contaminant)
b) Topology head: 3-class softmax (close, resonant, wide)
activated only when class head predicts 2L1S.
4. Auxiliary regression head: predicts log(t_E) and
anomaly amplitude to improve feature learning for
low-SNR smooth perturbations.

The model is causal: it processes epochs in arrival order
and can emit predictions after any number of epochs,
enabling early-warning mode.
"""

def __init__(self,
spatial_backbone: str = 'efficientnet_b0',
cde_hidden_dim: int = 128,
n_classes: int = 4,
n_topologies: int = 3,
pretrained_weights: Path | None = None):

def forward(self,
image_sequence: torch.Tensor,
timestamps: torch.Tensor,
sequence_mask: torch.Tensor
) -> TriggerOutput:
"""
Args:
image_sequence: [B, T_max, 1, 64, 64]
timestamps: [B, T_max] (MJD; irregular spacing OK)
sequence_mask: [B, T_max] bool (False = missing epoch)

Returns:
TriggerOutput with class_logits, topology_logits,
t_E_estimate, anomaly_amplitude, and calibrated_probs.
"""
## 4.2 Sequence Length and Input Unit (Corrected)
A reviewer identified that v1 was internally inconsistent: Roman produces ~6,912 epochs per 72-day window at 15-minute cadence, but the architecture assumed 200 epochs/event. The v2 specification resolves this by defining the inference input unit explicitly:
The input unit is an event-centered excerpt. An upstream photometric anomaly detector (simple threshold on DIA flux) identifies candidate variable sources. Once a source exceeds a significance threshold, the classifier begins receiving stamps. The input is a rolling window of the most recent 256 epochs (approximately 2.7 days of continuous observation). As new epochs arrive, the oldest are dropped. The Neural CDE's continuous hidden state is updated incrementally, making this efficient.
For offline reprocessing (post-season analysis), the full window sequence is available. The classifier processes it in chunks of 256 epochs with 128-epoch overlap, maintaining the CDE hidden state across chunks. The final classification uses the hidden state at the last epoch.
## 4.3 Topology Head (Stage A → Stage B Interface Fix)
A reviewer correctly identified that the v1 Stage A (4-class classifier) did not produce the topology information that Stage B (HMC seeding) needed. The v2 classifier adds a dedicated topology head that outputs a 3-class distribution over (close, resonant, wide) conditional on the class head predicting 2L1S. This topology distribution is passed to Stage B as a prior for initializing the sampler.
If the topology head's entropy is high (all three modes approximately equally likely), Stage B uses multi-start sampling across all three topologies rather than seeding from a single mode. This prevents Stage B from inheriting a wrong topology estimate from Stage A.
## 4.4 Probability Calibration and Threshold Governance
The v1 fixed threshold of P > 0.5 is replaced with a cost-based threshold policy.
class TriggerCalibrator:
"""
Post-training probability calibration and threshold selection.

1. Temperature scaling: Learn T on prevalence-weighted
validation set to minimize NLL.
2. Cost matrix: Define C_FN (science cost of missing a
binary) and C_FP (compute cost of a false Stage B run).
3. Threshold: Select P_threshold that minimizes expected
total cost: E[cost] = C_FN * FNR(t) + C_FP * FPR(t) * N_alerts.
4. Field/magnitude dependence: Compute threshold per
magnitude bin (bright sources get lower threshold).
"""

def __init__(self,
cost_fn: float = 100.0,
cost_fp: float = 1.0):

def calibrate(self,
logits: torch.Tensor,
labels: torch.Tensor,
prevalence_weights: torch.Tensor
) -> float:
"""Learn temperature T. Returns optimal T."""

def find_threshold(self,
calibrated_probs: torch.Tensor,
labels: torch.Tensor,
n_expected_alerts_per_day: float
) -> dict[str, float]:
"""Returns magnitude-dependent thresholds."""

def compute_ece(self, probs, labels, n_bins=15) -> float:
"""Expected calibration error."""

def compute_brier(self, probs, labels) -> float:
"""Brier score for probabilistic reliability."""
## 4.5 Stage B: Amortized Neural Posterior Estimation (ANPE)
The suggestion to replace HMC with Simulation-Based Inference (SBI) as the primary Stage B backend is adopted. Following Smyth et al. (2025), a Transformer encoder paired with a Normalizing Flow posterior estimator provides amortized inference that is approximately 1,000× faster than HMC while producing well-calibrated posteriors.
class AmortizedPosteriorEstimator:
"""
Stage B inference engine using ANPE.

Architecture: Transformer encoder processes the image
cube feature sequence -> context embedding -> Normalizing
Flow (Neural Spline Flow with 8 coupling layers) outputs
posterior samples over (s, q, rho, alpha, t_E, u_0, t_0).

The posterior is explicitly multimodal: the flow is
trained on (s, 1/s) pairs to capture the close/wide
degeneracy. Both modes are reported with their relative
evidence (log-likelihood ratio).

Fallback: For events where the ANPE posterior has
unexpectedly low log-probability (indicating OOD input),
the system falls back to microlux + NumPyro HMC with
multi-start initialization seeded by the flow samples.
"""

def __init__(self,
flow_checkpoint: Path,
n_posterior_samples: int = 10_000,
ood_threshold: float = -50.0,
fallback_to_hmc: bool = True):

def infer(self,
image_cube: torch.Tensor,
timestamps: torch.Tensor,
topology_prior: dict[str, float] | None = None
) -> PosteriorResult:
"""
Returns PosteriorResult with samples, log_probs,
mode_summary (close/wide), convergence diagnostics
(R-hat, ESS for HMC fallback), and wall_time_s.
Target: < 30 seconds per event for ANPE,
< 5 minutes for HMC fallback.
"""
## 4.6 Loss Function (Corrected)
The focal loss γ values in v1 were presented as fixed design choices. Reviewers correctly noted these are dataset-dependent hyperparameters. The v2 specification treats them as tunable with the following procedure:
Initial values: γ = 2.0 for 2L1S, γ = 1.0 for 1L1S and 1L2S, γ = 0.5 for contaminants. These are tuned via grid search over γ ∈ {0.5, 1.0, 2.0, 3.0} for each class, optimizing the per-class F1 score on the validation set. Focal loss is combined with stratified batch sampling: each mini-batch contains equal representation of all four classes. A reviewer asked whether the combination constitutes double-upweighting; the answer is that focal loss adjusts the gradient contribution per-sample (down-weighting easy examples), while stratified sampling adjusts the sampling frequency per-class. They operate on orthogonal axes and do not redundantly upweight.
## 4.7 Pretraining Strategy (Corrected)
Reviewers correctly questioned ImageNet pretraining on single-channel 64×64 NIR stamps. The v2 pretraining strategy is:
Self-supervised pretraining on synthetic Roman stamps: The spatial encoder (EfficientNet-B0) is first pretrained using a contrastive learning objective (SimCLR) on 1M unlabeled synthetic Roman stamps (generated from the crowding module without microlensing signals). This teaches the encoder Roman-specific features: PSF morphology, blend structure, noise patterns, detector artifacts. The pretrained encoder is then fine-tuned with the full labeled training set. This is compared against ImageNet initialization and random initialization in ablation A7.

# 5. Phase 6: Validation, Deployment, and Operations
## 5.1 Validation Metrics (Expanded)
v1 focused exclusively on classification accuracy. Reviewers requested reliability metrics, posterior validation, and stress testing on hard failure modes. The v2 validation suite covers three dimensions:
Classification metrics: Per-class precision, recall, F1, and AUROC on the held-out test set (200K events, 50K per class). Additionally, precision at a fixed daily Stage B budget (the operationally relevant metric): given that Stage B can process N events/day, what is the precision of the top-N scored events?
Probabilistic reliability: Expected Calibration Error (ECE), Brier score, and reliability diagrams on a prevalence-weighted test set. The ECE must be below 0.05 after temperature scaling. For Stage B, Simulation-Based Calibration (SBC) and coverage tests verify that the ANPE posterior has correct frequentist coverage at 68% and 95% credible intervals.
Stress suites (dedicated test sets for hard cases): Smooth non-caustic planetary anomalies (cusp approaches, q < 10⁻³); close/wide near-degenerate pairs (Δχ² < 1 between s and 1/s); faint sources (W146 > 22 mag) in high-crowding fields; saturated caustic peaks; partial sequences (early-alert conditions, < 50 epochs); and multi-window events with months-long gaps. Each stress suite reports a separate recall metric. The classifier must achieve > 80% recall on each stress suite individually, not just on the aggregate.
## 5.2 Centroid Validation (Quantitative, Not Visual)
A reviewer correctly flagged that visual inspection of centroid shifts in blink comparisons is not a reliable acceptance criterion. The v2 validation replaces this with quantitative checks:
Centroid residual distribution: Compare detected centroid shift (from DIA photometry) against the Stage 2 ground-truth centroid for 10K events, binned by source magnitude. The systematic bias must be < 0.005 pixels for W146 < 20, and the scatter must be consistent with the expected photometric centroid precision.
Recovery bias vs source brightness: Plot centroid shift recovery fraction as a function of W146 magnitude. This defines the magnitude below which the astrometric channel contributes information to the classifier. For sources fainter than this threshold, the classifier should receive a quality-gated astrometry mask (set to zero) so it learns not to rely on noise-dominated centroid measurements.
## 5.3 Deployment Architecture (Expanded)
Reviewers requested specifics on queue stability, backpressure handling, and cube assembly. The v2 deployment specification addresses these:
Message queue: Apache Kafka (not RabbitMQ) is selected for persistent, replayable message storage with exactly-once delivery semantics. Topics: roman.dia.stamps (incoming DIA stamps), roman.trigger.scores (Stage A outputs), roman.stageb.requests (Stage B escalations), roman.stageb.results (posteriors). Each message carries an idempotent event_id + epoch_index key to prevent duplicate processing.
Cube assembly: A stateful Kafka Streams processor accumulates DIA stamps per source_id into a rolling buffer of 256 epochs. When a new stamp arrives, the oldest is evicted. The buffer is serialized as a memory-mapped numpy array. When Stage A is invoked, it reads the buffer without copying. The trigger runs continuously as epochs arrive (streaming mode), not only after the full window.
Backpressure handling: If Stage B's GPU queue exceeds 1000 pending events, new requests are prioritized by trigger score (highest P(2L1S) first). Events below priority rank 1000 are deferred to a batch-processing queue that runs during non-observing gaps. A dead-letter topic captures events that fail inference after 3 retries. Alert: if the dead-letter topic exceeds 100 events/day, the operations team is notified to investigate systematic failures.
Throughput model: Expected candidate alert rate: Roman's GBTDS will observe ~200M stars. At a 0.01% variability flag rate, the upstream photometric detector generates ~20,000 variable candidates per day. Stage A processes these at > 10 events/second (SR-7), requiring < 1 GPU-hour/day. At 1% false positive rate (after calibration), Stage B receives ~200 candidates/day. At 30 seconds/event (ANPE), this requires ~1.7 GPU-hours/day, well within a single A100. During surge events (a high-magnification event triggers many neighboring sources), the backpressure policy handles the spike.
## 5.4 MLOps and On-Orbit Adaptation
Reviewers requested a model drift and retraining plan. The v2 specification includes:
Commissioning integration: During Roman's commissioning phase (~6 months), the detector noise model (Phase 1) is updated with on-orbit calibration data. The CycleGAN noise transfer model is retrained on real dark frames and flat fields. The classifier is fine-tuned on a small labeled set of confirmed microlensing events from commissioning observations (expected: 50–200 events in the first window). Fine-tuning uses a low learning rate (10⁻⁵) to preserve learned features while adapting to the real noise distribution.
Champion/challenger: The production model (champion) runs alongside a fine-tuned model (challenger). Both process all incoming events. The challenger's outputs are compared against the champion's for one full observing window. If the challenger achieves higher recall at equal FPR on confirmed events, it replaces the champion. Rollback criteria: if the challenger's false positive rate exceeds 2× the champion's on any magnitude bin, the champion is retained.
Retraining cadence: After each 72-day observing window, the confirmed event catalog is updated. A new challenger model is trained incorporating the new events. The cycle repeats for each of the 7 windows.
Model cards: Each deployed model version is accompanied by a model card (Mitchell et al. 2019 format) documenting: training data version, architecture, hyperparameters, calibration statistics (ECE, Brier), per-class and per-stress-suite recall, known limitations, and the container digest used for training.

# 6. Corrected Computational Budget
The v1 compute budget contained arithmetic errors that were identified by multiple reviewers. This section presents the corrected budget with explicit derivations.
## 6.1 Worked Example: Stage 2 (Physics Engine)
All 2M events now run through microlux (GPU). Average epochs per event: 200 (event-centered excerpt from the 6,912-epoch window). Throughput: ~10,000 epochs/second on A100 (configuration-dependent; worst case for resonant finite-source: ~1,000 epochs/second). Total epoch evaluations: 2M × 200 = 400M epochs. Wall time at 10K/s: 400M / 10K = 40,000 seconds ≈ 11 GPU-hours. Worst-case wall time (all resonant): 400,000 seconds ≈ 111 GPU-hours. With 10% resonant events: 0.9 × 11 + 0.1 × 111 ≈ 21 GPU-hours.
## 6.2 Storage Budget (Previously Absent)
Reviewers correctly identified that storage was entirely missing from v1. The v2 budget:
I/O throughput: Training on 20 TB of WebDataset shards at 4× A100 data-parallel training requires approximately 500 MB/s sustained read throughput. This is achievable on a Lustre parallel filesystem with 8+ OSTs and appropriate stripe width. For HPC environments without high-performance parallel I/O, the alternative is on-the-fly simulation: Stages 2–3 run as a data-loading pipeline during training, eliminating the need to materialize the full dataset. This increases training wall time by approximately 30% but eliminates the storage bottleneck entirely.

# 7. Expanded Risk Register
The v1 risk register rated the sim-to-real gap as Medium likelihood. Multiple reviewers argued this should be High because the detector model has never been tested against on-orbit data. The v2 register incorporates all reviewer-suggested additions.

# 8. Scope: In vs Out for v2.0
A reviewer recommended an explicit scope boundary to prevent scope creep. The following items are explicitly out of scope for v2.0:
Open science: The synthetic training dataset (2M events), model checkpoints, and SMIG pipeline code will be released publicly on Zenodo with a DOI and an open-source license (MIT for code, CC-BY-4.0 for data). Parameter catalogs and a representative subset of 10K image cubes will be deposited on MAST for community use. This positions SMIG as a community resource beyond the Roman mission.
| SR | Requirement | Pipeline Stages | Acceptance Test | Pass Threshold |
| --- | --- | --- | --- | --- |
| SR-1 | Caustic crossing temporal resolution | 2, 3 | Recover injected 2-hour caustic at 15-min cadence | Peak A(t) within 5% of oversampled truth |
| SR-2 | Finite source size range ρ* = 0.001–0.05 | 2, 3 | Magnification matches VBMicrolensing benchmark tables | |A_sim - A_bench| / A_bench < 10⁻⁴ |
| SR-3 | Astrometric centroid fidelity | 2, 3, 5 | Centroid recovery bias vs source magnitude | Bias < 0.01 pix for W146 < 21 mag |
| SR-4 | Crowding realism (∼10⁴ stars/arcmin²) | 1, 3 | Stamp neighbor count vs HST Bulge fields | Count within 20% of empirical |
| SR-5 | Class diversity (2L1S, 1L2S, 1L1S, FFP, contaminants) | 1, 4, 5 | Per-class recall on held-out test | Recall > 95% for 2L1S; > 90% others |
| SR-6 | Saturation handling at caustic peak (NEW) | 1 (Ph1), 3, 5 | Classifier accuracy on saturated events | No systematic rejection of A > 100 events |
| SR-7 | Inference throughput (NEW) | 5, 6 | Stage A inference rate on single A100 | > 10 events/second |
| SR-8 | Probability calibration (NEW) | 5, 6 | ECE on prevalence-weighted validation | ECE < 0.05 |
| ID | Ablation | What It Tests | Expected Outcome |
| --- | --- | --- | --- |
| A1 | 1D light curve + 47 LIA features (Random Forest) | v1 baseline; justifies entire image-cube approach | Fails on 2L1S (replicates Godines failure) |
| A2 | 1D light curve + Neural CDE (no images) | Whether temporal modeling alone suffices | Moderate 2L1S recall; misses smooth anomalies |
| A3 | DIA-only image cube (no direct images) | Operational feasibility (DIA is what Roman produces) | Strong performance; primary deployment path |
| A4 | Direct-only image cube (no DIA) | Whether DIA artifacts help or hurt | Comparable to A3 but less artifact-robust |
| A5 | Dual-stream (direct + DIA) | Whether complementary streams improve over single | Marginal gain over A3; may not justify 2× compute |
| A6 | A3 without centroid channel | Whether astrometric signal adds value at faint mags | Minimal loss for W146 > 21; significant for < 19 |
| A7 | A3 without detector effects (Phase 1 modules off) | Whether sim-to-real gap from detector physics matters | Degraded performance on injected artifacts |
| A8 | A3 with caustic-crossing events only (no smooth anomalies) | How much smooth anomaly training helps | Catastrophic failure on cusp-approach events |
| A9 | Backend consistency: microlux vs VBMicrolensing same events | Whether backend choice affects classifier | No significant difference if agreement < 10⁻⁴ |
| Reviewer Finding | Severity | Resolution |
| --- | --- | --- |
| DeltaFunction source contradicts finite-source physics (SR-2) | Critical | FiniteSourceRenderer with limb-darkened disk |
| PSF jitter value wrong (14 vs 5 mas) | High | Corrected to 5 mas/axis in config |
| PSF toolchain ambiguity (WebbPSF vs roman_imsim) | Medium | STPSF is authoritative; single rendering path |
| DIA reference template unrealistic (50 identical coadds) | High | Multi-epoch variable-PSF reference stack |
| Crowding density units dimensionally broken | Critical | Corrected: ~1.5×10⁴ stars/arcmin² above W146 = 26 |
| DIA computational cost not budgeted | High | Fixed-kernel subtraction for training; SFFT for validation |
| SFFT unstable on 64×64 stamps | Medium | 256×256 context stamp with 64×64 center crop |
| Code | Name | v1 Term (Retired) | Description |
| --- | --- | --- | --- |
| 1L1S | Single lens, single source | PSPL | Standard Paczyński event |
| 2L1S | Binary lens, single source | BLPL (retired) | Planetary and stellar binary caustic events |
| 1L2S | Single lens, binary source | BSPL (retired) | Binary source with optional xallarap |
| FFP | Free-floating planet | FFP | Short t_E, high u_0; folded into 1L1S for training |
| Contaminant Class | Count | % of Contaminant Pool | % of Total (2M) |
| --- | --- | --- | --- |
| Eclipsing binaries | 150K | 30% | 7.5% |
| Mira / semi-regular variables | 100K | 20% | 5% |
| Classical novae | 50K | 10% | 2.5% |
| Detector artifacts (dipoles, persistence, RTS) | 100K | 20% | 5% |
| AGN / background transients | 50K | 10% | 2.5% |
| Constant stars (null class) | 50K | 10% | 2.5% |
| Total contaminants | 500K | 100% | 25% |
| Stage | Optimistic | Nominal | Pessimistic | Hardware |
| --- | --- | --- | --- | --- |
| 1: Population synthesis | 0.5 hrs | 1 hr | 2 hrs | 1 CPU core |
| 2: microlux physics | 11 GPU-hrs | 21 GPU-hrs | 111 GPU-hrs | 1× A100 |
| 3: GalSim + detector chain | 1,500 GPU-hrs | 2,800 GPU-hrs | 5,000 GPU-hrs | GPU cluster |
| 3b: DIA subtraction | 200 GPU-hrs | 500 GPU-hrs | 1,200 GPU-hrs | GPU cluster |
| 4: Augmentation | 30 CPU-hrs | 56 CPU-hrs | 120 CPU-hrs | Parallel CPU |
| 5: Classifier training | 100 GPU-hrs | 200 GPU-hrs | 400 GPU-hrs | 4× A100 node |
| 5b: ANPE training | 50 GPU-hrs | 100 GPU-hrs | 200 GPU-hrs | 2× A100 |
| Total GPU-hours | ~1,860 | ~3,620 | ~6,910 |  |
| Data Product | Per Event | Total (2M) | Compression |
| --- | --- | --- | --- |
| Stage 1 catalog (Parquet) | ~2 KB | 4 GB | N/A |
| Stage 2 physics (HDF5) | ~50 KB | 100 GB | gzip |
| Stage 3 direct cubes (float32) | ~3.3 MB (200×64×64×4B) | 6.6 TB | zstd → ~4 TB |
| Stage 3 DIA cubes (float32) | ~3.3 MB | 6.6 TB | zstd → ~3 TB |
| Stage 4 augmented (WebDataset) | ~10 MB (with metadata) | 20 TB | Sharded tar |
| Total on-disk |  | ~27 TB (compressed) |  |
| Risk | Sev. | Like. | Mitigation |
| --- | --- | --- | --- |
| Sim-to-real gap on first Roman data | High | HIGH | Upgraded from Medium. Phase 1 detector effects + CycleGAN noise transfer. Commissioning fine-tuning within first window. Champion/challenger evaluation. |
| Close/wide degeneracy corrupts training labels | High | High | Two-component Gaussian mixture labels for s. ANPE trained on degenerate pairs. |
| DIA algorithm mismatch (SFFT vs Roman SOC pipeline) | High | Med | Train on fixed-kernel DIA (robust baseline). Validate subset on SFFT. Retrain on Roman SOC products during commissioning. |
| Label noise: ambiguous smooth 2L1S vs 1L1S | Med | High | Ensemble classifier + human-in-the-loop for gold subset. Auxiliary regression head forces feature learning at low anomaly amplitudes. |
| Alert volume exceeds Stage B capacity | High | Med | ANPE is 1000× faster than HMC. Backpressure queue with priority scoring. Deferred batch queue for overflow. |
| Library maintenance discontinuity (microlux, caustics) | Med | Med | VBMicrolensing retained as validation reference. Containerized environment pins exact versions. Fork maintenance plan if upstream abandons. |
| Model interpretability resistance from science community | Med | High | Saliency maps (Grad-CAM on spatial encoder) and attention weights published with every alert. Stage B posterior provides physically interpretable parameters. |
| JAX ecosystem breaking changes | Med | Med | Container digest pinning. CI/CD runs nightly against pinned JAX version. Migration budget allocated in each release cycle. |
| Data leakage inflates reported metrics | High | Med | Mandatory validate_splits.py pre-training check. Event-family-level splits. Starfield seed isolation. |
| Numerical divergence near resonant caustics | Med | Low | microlux adaptive precision. |A(t)| > 10³ capped with flag. 1000-event cross-validation against VBMicrolensing. |
| In Scope (v2.0) | Out of Scope (Future Work) |
| --- | --- |
| Binary lens (2L1S) detection and classification | Triple lens systems (3L1S) |
| Binary source (1L2S) with xallarap | Multi-band simultaneous simulation (F087, F146, F213) |
| W146 single-filter simulation | Roman grism / spectroscopic data |
| Event-centered 64×64 stamps | Full focal-plane tiling (18-SCA mosaic) |
| CycleGAN noise-domain transfer | Latent-space event generation (GANs for physics) |
| ANPE posterior estimation | Joint lens+source modeling with spectroscopic constraints |
| Roman GBTDS fields only | Generalization to LSST / Euclid / ground-based surveys |
| Kafka-based streaming deployment | Multi-observatory joint alert brokering |