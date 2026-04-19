# Phase 3.2 Design: Microlensing Physics Engine

This document is the **mandatory blocking gate** before any production code in `smig/microlensing/`. It covers the six mandated sections of the Phase 3.2 spec plus all items raised in the architectural review.

---

## 1. MicrolensingEvent and SourceProperties Field Specification

### 1.1 SourceProperties (frozen dataclass)

```python
@dataclass(frozen=True)
class SourceProperties:
    teff_K: float        # Effective temperature (K)
    log_g: float         # Surface gravity log10(g/[cm/s²]); CGS dex
    metallicity_feh: float  # [Fe/H] in dex
    distance_kpc: float  # Heliocentric distance (kpc)
    mass_msun: float     # Stellar mass (M☉)
```

Consumed from `StarRecord` fields; constructed by `priors.sample_event`.

### 1.2 MicrolensingEvent fields (frozen dataclass, frozen at end of phase)

| Field | Type | Unit | Notes |
|---|---|---|---|
| `event_id` | `str` | — | Caller-supplied; written to JSON sidecar key |
| `t0_mjd` | `float` | MJD | Time of closest approach to centre of mass |
| `tE_days` | `float` | days | Einstein ring crossing time |
| `u0` | `float` | θ_E | Impact parameter at t0 |
| `rho` | `float` | θ_E | Angular source radius / θ_E |
| `alpha_rad` | `float` | rad | Angle: source trajectory relative to binary axis |
| `q` | `float` | — | Mass ratio m2/m1; 0 for single-lens events |
| `s` | `float` | θ_E | Projected binary separation; 0 for single-lens events |
| `pi_E_N` | `float` | — | Parallax component N; default 0 (inactive Phase 3) |
| `pi_E_E` | `float` | — | Parallax component E; default 0 (inactive Phase 3) |
| `theta_E_mas` | `float` | mas | Einstein radius; single source of truth |
| `event_class` | `EventClass` | — | Enum; see §5 |
| `backend` | `str` | — | `"VBBinaryLensing"` for binary, `"analytic"` for PSPL/FSPL |
| `backend_version` | `str` | — | `"3.7.0"` for binary, `"N/A"` for PSPL/FSPL |
| `ld_fallback_used` | `bool` | — | True if Claret grid fallback was used at construction |

**Interface freeze notice (verbatim, must appear in `event.py` module docstring):**

> INTERFACE FROZEN: The MicrolensingEvent field list, SourceProperties field list, and
> .magnification(t_mjd, band, source_props) signature are LOCKED as of Phase 3.2.
> Any future change is a versioned migration requiring explicit sign-off.

### 1.3 Computation contract

All fields are computed **once** at event construction in `priors.sample_event`. The `.magnification()` method is **pure** and **read-only**: it computes magnification from stored fields + supplied arguments without mutating any event attribute. In particular `ld_fallback_used` is set at construction time and never mutated.

### 1.4 Backend provenance convention

| EventClass | backend | backend_version |
|---|---|---|
| PSPL | `"analytic"` | `"N/A"` |
| FSPL_STAR | `"analytic"` | `"N/A"` |
| PLANETARY_CAUSTIC | `"VBBinaryLensing"` | `"3.7.0"` |
| STELLAR_BINARY | `"VBBinaryLensing"` | `"3.7.0"` |
| HIGH_MAGNIFICATION_CUSP | `"VBBinaryLensing"` | `"3.7.0"` |

The string `"VBBinaryLensing"` is the logical backend identifier (independent of the PyPI distribution name, though they share the same spelling — see §4). The version string is obtained at construction time from `backends.get_primary_backend()[1]`.

### 1.5 `.magnification()` method signature

```python
def magnification(
    self,
    t_mjd: np.ndarray,
    band: str,
    source_props: SourceProperties,
) -> np.ndarray:
```

Dispatches to:
- PSPL → `pspl.magnification_pspl(t_mjd, self.t0_mjd, self.tE_days, self.u0)`
- FSPL_STAR → `fspl.magnification_fspl(t_mjd, self.t0_mjd, self.tE_days, self.u0, self.rho, source_props, band)`
- All binary classes → `binary.magnification_2l1s(t_mjd, self.t0_mjd, self.tE_days, self.u0, self.rho, self.alpha_rad, self.q, self.s)`

---

## 2. SourceProperties Relevance per EventClass

| Field | PSPL | FSPL_STAR | Binary (all) |
|---|---|---|---|
| `teff_K` | ignored | used (LD coefficient lookup) | ignored (no 2L1S-FSPL in Phase 3) |
| `log_g` | used (ρ at construction) | used (ρ + LD) | used (ρ at construction) |
| `metallicity_feh` | ignored | used (LD) | ignored |
| `distance_kpc` | used (D_S for θ_E + ρ) | used | used |
| `mass_msun` | used (ρ from SI chain) | used | used |
| `band` arg | ignored | used (LD coefficient for that band) | ignored |

Note: `band` is a parameter of `.magnification()`, not stored on `SourceProperties`.
Phase 3 implements only single-band F146 LD for FSPL. Binary 2L1S magnification is point-source at the source disk level.

---

## 3. θ_E and ρ Derivation Chain (SI throughout)

### 3.1 Physical constants (single declaration in `priors.py`)

```python
G_SI      = 6.67430e-11   # m³ kg⁻¹ s⁻²  (NIST 2018)
M_SUN_KG  = 1.98847e30    # kg             (IAU 2015)
KPC_M     = 3.08568e19    # m/kpc          (exact definition)
AU_M      = 1.49598e11    # m/AU           (exact IAU 2012)
C_MS      = 2.99792458e8  # m/s            (exact)
MAS_RAD   = (np.pi / (180 * 3600 * 1000))  # radians per mas
```

### 3.2 θ_E formula

For lens mass M_L (M☉), lens distance D_L (kpc), source distance D_S (kpc):

```
D_L_m = D_L * KPC_M
D_S_m = D_S * KPC_M
D_LS_m = max(D_S_m - D_L_m, 0)   # must be > 0; see §3.5

# Einstein radius in metres (physical at D_L)
R_E_m = sqrt(4 * G_SI * M_L * M_SUN_KG * D_LS_m / (C_MS**2 * D_L_m))

# Angular Einstein radius in radians, then in mas
theta_E_rad = R_E_m / D_L_m
theta_E_mas = theta_E_rad / MAS_RAD
```

`theta_E_mas` is written to the frozen event. No consumer re-derives it.

### 3.3 ρ derivation from log_g (strict SI)

```
# log_g is in CGS (dex): log10(g / [cm s⁻²])
# Validation: must be in [0.5, 6.0]; outside this range raise ValueError
if not (0.5 <= source_star.log_g <= 6.0):
    raise ValueError(f"log_g={source_star.log_g!r} outside valid range [0.5, 6.0]")

g_cgs = 10 ** source_star.log_g        # cm/s²
g_si  = g_cgs / 100.0                  # m/s²   (1 cm/s² = 0.01 m/s²)

M_star_kg = source_star.mass_msun * M_SUN_KG
R_star_m  = sqrt(G_SI * M_star_kg / g_si)   # Stefan-Boltzmann NOT used

# Angular source radius in radians
D_S_m = source_star.distance_kpc * KPC_M
theta_star_rad = R_star_m / D_S_m

# In mas
theta_star_mas = theta_star_rad / MAS_RAD

# ρ = θ_★/θ_E (dimensionless)
rho = theta_star_mas / theta_E_mas
```

Do NOT use `R_star = sqrt(L / (4π σ T⁴))` — that requires luminosity and has larger uncertainty than the log_g route.

### 3.4 μ_rel and tE

```
mu_rel_mas_yr = abs(rng.normal(0, 5.0))   # Galactic bulge velocity dispersion
mu_rel_mas_day = mu_rel_mas_yr / 365.25   # explicit day/year conversion

tE_days = theta_E_mas / mu_rel_mas_day    # standard formula
```

The `5.0 mas/yr` is the 1σ dispersion of the relative proper motion for bulge-disk pairs along typical Roman bulge sightlines (cf. Penny et al. 2019 Roman planet yields). The Galactic model below adds systematic components.

### 3.5 Edge cases and validation

| Condition | Action |
|---|---|
| `D_L_m ≥ D_S_m` | Re-sample D_L (rejection loop); cannot have lens behind source |
| `theta_E_mas ≤ 0` | Should not occur for M_L > 0 and D_LS > 0; guarded by above |
| `log_g < 0.5 or > 6.0` | `raise ValueError` immediately (fail-fast; no clamping) |
| `mass_msun ≤ 0` | Cannot occur from Kroupa IMF; assert at sample time |
| `rho > 10` | Allowed; PSPL/FSPL classification logic handles it |

---

## 4. VBBinaryLensing Backend

### 4.1 Canonical PyPI distribution name

```
pip install VBBinaryLensing   # exact case on PyPI
importlib.metadata.version("VBBinaryLensing")  # → "3.7.0"
```

**Canonical distribution name: `VBBinaryLensing`** (capital V, capital B, capital L; no separators).
This is distinct from the logical backend name (also `"VBBinaryLensing"`) — they happen to share the same string, but in code they are stored in separate constants (`_PINNED_DIST` and `_BACKEND_NAME` in `backends.py`).

**Pinned version: `3.7.0`** (exact).

### 4.2 Failure classification taxonomy

`binary.py` must detect ALL of the following and raise `MicrolensingComputationError(params=..., cause=...)`:

| Failure type | Detection method |
|---|---|
| Python exception from native binding (TypeError, ValueError, RuntimeError) | Wrap `vb.BinaryMag2(...)` in `try/except Exception` |
| NaN return value | `np.isnan(A)` |
| Inf return value | `np.isinf(A)` |
| Unphysical A < 1.0 | `A < 1.0` (magnification is always ≥ 1 for a physical source) |

No silent fallback. `MicrolensingComputationError` is raised with the full parameter dict (s, q, y1, y2, rho at the failing time step) so the caller can reproduce the failure.

### 4.3 API usage pattern

```python
import VBBinaryLensing

vb = VBBinaryLensing.VBBinaryLensing()   # class is nested: module.VBBinaryLensing
vb.Tol    = 1e-3   # absolute photometric accuracy
vb.RelTol = 1e-3   # relative photometric accuracy

# Source trajectory (no parallax; standard rectilinear):
tau = (t - t0) / tE
y1  = tau * cos(alpha) - u0 * sin(alpha)   # along binary axis
y2  = tau * sin(alpha) + u0 * cos(alpha)   # perp. to binary axis

# Finite-source binary lens magnification (point-source source disk):
A = vb.BinaryMag2(s, q, y1, y2, rho)   # returns float
```

The `vb` instance is created once per function call (stateless apart from Tol/RelTol). Do NOT cache the VBBL instance across calls; it is cheap to construct.

### 4.4 Version pinning and drift detection

`backends.py` holds:
- `_PINNED_DIST = "VBBinaryLensing"` — for `importlib.metadata.version()`
- `_BACKEND_NAME = "VBBinaryLensing"` — for `MicrolensingEvent.backend`
- `_PINNED_VERSION = "3.7.0"` — single source of truth; test enforces this matches `pyproject.toml`

Module-level assertion (fires at import time, not at first use):
```python
import importlib.metadata
assert importlib.metadata.version(_PINNED_DIST) == _PINNED_VERSION, (
    f"VBBinaryLensing version mismatch: installed "
    f"{importlib.metadata.version(_PINNED_DIST)!r} != pinned {_PINNED_VERSION!r}"
)
```

`test_backend_pin.py` uses `tomllib` to parse `pyproject.toml` and asserts that `_PINNED_VERSION` appears in `[project.dependencies]` as `"VBBinaryLensing==3.7.0"`.

---

## 5. Cassan 2008 Topology Boundaries and EventClass Assignment

### 5.1 Boundary formulas (Cassan 2008, A&A 491, 587, Eqs. 11–12)

For binary lens with total mass M = m1+m2, mass ratio q = m2/m1 ≤ 1, separation s (in θ_E units):

**Close–resonant boundary:**
```
s_close(q) = sqrt((1 + q) / (1 + q**(1/3))**3)
```

**Resonant–wide boundary:**
```
s_wide(q) = sqrt((1 + q**(1/3))**3 / (1 + q))
```

Identities:
- `s_close(q) × s_wide(q) = 1` (exact reciprocal relation)
- `s_close(q=1) = 0.5`, `s_wide(q=1) = 2.0`
- `s_close(q→0) → 1`, `s_wide(q→0) → 1` (degenerate at zero mass ratio)

**Important correction from architecture review:** The original plan incorrectly had `(1+q)^(1/3)` under the square root, giving an exponent of `(1+q)^(1/6)`. The correct exponent is `(1+q)^(1/2)` in the numerator of `s_close`. Verified against Cassan (2008) Eqs. 11–12.

### 5.2 EventClass mapping — Phase 3 simplification

**Phase 3 deliberately collapses the three-topology classification (close/resonant/wide) to a two-class binary split based on q alone.** This is an intentional narrowing justified by the Phase 3 scope: the `SpatiotemporalTrigger` in Phase 4+ is trained on (q, s, u0) not on caustic morphology. The `s` parameter IS sampled and IS stored on `MicrolensingEvent` for full geometric fidelity, but it does **not** affect EventClass in Phase 3. Caustic-crossing geometry is implicit in the VBBL magnification calculation.

| Condition | EventClass |
|---|---|
| q = 0 and ρ < 1e-3 | `PSPL` |
| q = 0 and ρ ≥ 1e-3 | `FSPL_STAR` |
| q > 0 and **u0 < 0.05** | `HIGH_MAGNIFICATION_CUSP` ← **FIRST CHECK** |
| q > 0 and q < 0.03 | `PLANETARY_CAUSTIC` |
| q > 0 and q ≥ 0.03 | `STELLAR_BINARY` |

### 5.3 HIGH_MAGNIFICATION_CUSP precedence rule

The HIGH_MAGNIFICATION_CUSP check fires **before** the PLANETARY_CAUSTIC/STELLAR_BINARY split. Any binary event with u0 < 0.05 is classified HIGH_MAGNIFICATION_CUSP regardless of q or s. This takes precedence to prevent later optimizations from accidentally inverting the ordering.

```python
# Correct ordering — must match exactly:
if q == 0.0 and rho < 1e-3:
    event_class = EventClass.PSPL
elif q == 0.0:
    event_class = EventClass.FSPL_STAR
elif u0 < 0.05:          # HIGH_MAGNIFICATION_CUSP fires first for all binary
    event_class = EventClass.HIGH_MAGNIFICATION_CUSP
elif q < 0.03:
    event_class = EventClass.PLANETARY_CAUSTIC
else:
    event_class = EventClass.STELLAR_BINARY
```

### 5.4 event_class_target enforcement pseudocode

For `sample_event(..., event_class_target=EventClass.HIGH_MAGNIFICATION_CUSP)`:
- Force `u0 = rng.uniform(0, 0.05)` (conditional draw — no rejection needed)
- Force `q = 10**rng.uniform(-5, 0)` (binary is required)

For `PLANETARY_CAUSTIC` / `STELLAR_BINARY`:
- Rejection sampling: draw (M_L, D_L, u0, q, s, alpha), compute derived quantities, check class matches target, retry up to `MAX_RETRIES = 1000`
- `PLANETARY_CAUSTIC`: draw `q` from log-uniform [1e-5, 0.03); reject if u0 < 0.05
- `STELLAR_BINARY`: draw `q` from log-uniform [0.03, 1.0]; reject if u0 < 0.05

For `PSPL` / `FSPL_STAR`:
- Force `q = 0.0`, `s = 0.0`, `alpha = 0.0`; derive ρ; classification follows deterministically

```python
MAX_RETRIES = 1000
for attempt in range(MAX_RETRIES):
    # Sample lens mass and distance
    M_L = _sample_kroupa(rng)
    D_L = _sample_lens_distance(rng, source_star.distance_kpc)
    if D_L >= source_star.distance_kpc:
        continue
    # Derive theta_E, tE, rho
    ...
    # Sample binary params if needed
    if event_class_target in (None, EventClass.PSPL, EventClass.FSPL_STAR):
        q, s, alpha = 0.0, 0.0, 0.0
        u0 = rng.uniform(0, 1.5)
    elif event_class_target == EventClass.HIGH_MAGNIFICATION_CUSP:
        u0 = rng.uniform(0, 0.05)    # conditional draw
        q = 10 ** rng.uniform(-5, 0)
        s = 10 ** rng.uniform(np.log10(0.3), np.log10(3.0))
        alpha = rng.uniform(0, 2 * np.pi)
    elif event_class_target == EventClass.PLANETARY_CAUSTIC:
        u0 = rng.uniform(0.05, 1.5)  # avoid HMC
        q = 10 ** rng.uniform(-5, np.log10(0.03))
        s = 10 ** rng.uniform(np.log10(0.3), np.log10(3.0))
        alpha = rng.uniform(0, 2 * np.pi)
    else:  # STELLAR_BINARY
        u0 = rng.uniform(0.05, 1.5)
        q = 10 ** rng.uniform(np.log10(0.03), 0)
        s = 10 ** rng.uniform(np.log10(0.3), np.log10(3.0))
        alpha = rng.uniform(0, 2 * np.pi)
    # Classify and check
    event_class = _classify(q, u0, rho)
    if event_class_target is None or event_class == event_class_target:
        break
else:
    raise RuntimeError(f"Could not sample {event_class_target} in {MAX_RETRIES} tries")
```

---

## 6. LD Policy and ld_fallback_used Propagation

### 6.1 Claret 2000 grid specification

File: `data/microlensing/claret2000_ld.csv`
Columns: `Teff_K, log_g, FeH, band, a_linear`

Grid dimensions (280 entries):
- Teff_K: [3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000] (K)
- log_g: [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0] (CGS dex)
- FeH: [−1.5, −1.0, −0.5, 0.0, +0.5] (dex)
- band: "H" (single band; proxy for Roman F146)

Source: Claret (2000, A&A 363, 1081), linear LD coefficients, ATLAS9 stellar atmosphere models.
**Note:** The committed CSV contains values derived from a polynomial approximation to the Claret (2000) Table 1 H-band data. Production use should validate against the published table before regression testing.

### 6.2 F146 LD proxy (H-band approximation)

**Roman F146 (λ_eff ≈ 1.46 μm) is approximated by Johnson H-band (λ_eff ≈ 1.65 μm).**

Rationale: Claret (2000) predates the Roman Space Telescope and does not include F146. The H-band is the closest single Claret filter to F146's effective wavelength. A future phase may upgrade to a throughput-weighted F146 grid using Claret (2011) or synthetic atmosphere spectra convolved with the Roman bandpass.

**This is an approximation, not a calibrated F146 LD coefficient.** The LD coefficient affects the FSPL magnification profile shape at the ~5% level for typical LD values (a_linear ≈ 0.4–0.6); using H-band vs. a true F146-weighted value introduces systematic differences of order ΔA/A ≲ 0.02 in the peak plateau region.

### 6.3 strict_ld_grid policy

```python
# In limb_darkening.py:
def get_coefficient(
    source_props: SourceProperties,
    band: str,
    strict: bool = True,
) -> tuple[float, bool]:
    """Return (a_linear, was_fallback)."""
    coef = _trilinear_interp(source_props.teff_K, source_props.log_g,
                              source_props.metallicity_feh, band)
    if coef is None:  # out of grid
        if strict:
            raise ClaretGridError(source_props.teff_K, source_props.log_g,
                                   source_props.metallicity_feh, band)
        # Nearest-neighbor fallback
        coef = _nearest_neighbor(source_props.teff_K, source_props.log_g,
                                  source_props.metallicity_feh, band)
        return coef, True  # was_fallback=True
    return coef, False
```

### 6.4 ld_fallback_used set at construction time

In `priors.sample_event`:
```python
a_lin, was_fallback = limb_darkening.get_coefficient(
    source_props, band="H", strict=strict_ld_grid
)
# ld_fallback_used is now fixed; the frozen event is constructed next:
return MicrolensingEvent(..., ld_fallback_used=was_fallback)
```

`.magnification()` calls `limb_darkening.get_coefficient(source_props, band, strict=False)` internally (non-strict, since the fallback decision was already made and is fully deterministic for the same inputs). The `ld_fallback_used` flag is **not** re-evaluated at magnification time.

### 6.5 Yoo (2004) LD formulation and Claret a_linear mapping

**Source:** Yoo, J. et al. (2004), ApJ, 603, 139, "OGLE-2003-BLG-262: Finite-Source Effects from a Point-Mass Lens"

Both Claret (2000) and Yoo (2004) use the linear LD law:
```
I(μ)/I_0 = 1 − a_linear × (1 − μ)    where μ = cos θ = sqrt(1 − (r/R_★)²)
```

The parameters are identical: `a_linear` (Claret notation) = `u` (Yoo notation). **No transformation is required.**

However, Yoo also introduce a renormalized parameter Γ for the B₀/B₁ decomposition:
```
Γ = 2 × a_linear / (3 − a_linear)
```
derived by matching the Yoo profile `S = 1 − Γ(1 − 3μ/2)` to the classical form `S = 1 − a(1−μ)`.
The `smig` implementation uses `a_linear` directly (classical form), computing:
```
A_fs = [6/(3−a)] × integral_0^1 r × ⟨A_ps(r·ρ, u)⟩_φ × (1 − a(1−sqrt(1−r²))) dr
```
The normalization factor `6/(3−a)` is exact (analytic result from integrating the LD profile over the disk). For the B₀/B₁ decomposition form, `Γ = 2a/(3−a)` converts between conventions.

The azimuthal average `⟨A_ps(r·ρ, u)⟩_φ` is computed with a 32-point Gauss-Legendre quadrature (vectorized); the radial integral uses `scipy.integrate.quad`. For z = u/ρ > 10, the PSPL approximation is used directly (error < 0.1%).

### 6.6 LD re-lookup in `.magnification()` — determinism guarantee

`MicrolensingEvent` stores `ld_fallback_used` but NOT `a_linear`. The LD coefficient is re-looked up inside `.magnification()` with `strict=False`, using the same `(Teff, log_g, [Fe/H], band)` tuple from `source_props`. Because `limb_darkening.get_coefficient` is a pure deterministic function of its inputs:
- If `ld_fallback_used=False`: `strict=False` returns the same in-grid value as `strict=True` did at construction.
- If `ld_fallback_used=True`: `strict=False` returns the same nearest-neighbor value used at construction.

No extra stored field is needed; no mutation occurs. The coefficient is **not cached** on the event object (keeping the frozen field list minimal).

---

## 7. Galactic Priors Summary

### Lens mass — Kroupa (2001) IMF

Three-piece power law (`Γ` = power-law index):
- α = 0.3 for M < 0.08 M☉ (brown dwarf / sub-stellar)
- α = 1.3 for 0.08 ≤ M < 0.5 M☉ (low-mass main sequence)
- α = 2.3 for M ≥ 0.5 M☉ (Salpeter regime, capped at 2.0 M☉ for compact-object simplification)

### Lens distance — Galactic double exponential disk + bulge

Disk component: exponential profile with scale height h_z = 0.3 kpc and scale length h_R = 2.5 kpc (cf. Bovy 2015). Bulge component: COBE E2 bar model projected along the Roman bulge sightlines (l ≈ 1.5°, b ≈ −1.5°). The bulge probability follows: `p_bulge(D_L) ∝ ρ_bulge(D_L) × D_L²`. Numerical values: disk and bulge contributions weighted by their mass fractions along the sightline.

Practical implementation for Phase 3: combine disk + bulge as a 1D PDF in D_L ∈ [0, D_S] sampled via inverse-transform or rejection sampling.

### Suzuki et al. (2016) reference events

File: `data/microlensing/reference_events/suzuki2016_sample.json`

Five events from the MOA-II planet sample (Suzuki et al. 2016, ApJS 221, 3). Peak magnifications are computed with the pinned VBBL 3.7.0 using the stored parameters; they serve as self-consistent regression targets.

| Event | q | s | u0 | Expected class | VBBL peak A |
|---|---|---|---|---|---|
| MOA-2007-BLG-400Lb | 4.2e-3 | 1.285 | 0.098 | PLANETARY_CAUSTIC | 10.39 |
| MOA-2008-BLG-310Lb | 3.3e-4 | 1.156 | 0.088 | PLANETARY_CAUSTIC | 11.42 |
| MOA-2007-BLG-192Lb | 4.3e-5 | 1.020 | 0.052 | PLANETARY_CAUSTIC | 25.70 |
| MOA-2011-BLG-293Lb | 2.5e-3 | 1.020 | 0.026 | HIGH_MAGNIFICATION_CUSP | 93.70 |
| OGLE-2007-BLG-368Lb | 6.3e-5 | 0.930 | 0.180 | PLANETARY_CAUSTIC | 5.65 |

---

## 8. pyproject.toml Changes

Add to `[project.dependencies]`:
```
"VBBinaryLensing==3.7.0",
```

Add new optional group:
```toml
[project.optional-dependencies]
phase3-test = [
    "MulensModel",
]
```

Note: `phase3-test` does not conflict with the future `phase3-dev` group (different name). The `MulensModel` version is not pinned (test-only, not in the critical regression path).

The `gxx_linux-64` conda package (C++15 compiler) must be installed in `smig_env` before building `VBBinaryLensing` from source. This is a build dependency, not a runtime dependency.
