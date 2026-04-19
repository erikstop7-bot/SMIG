"""2L1S binary lens magnification via pinned VBBinaryLensing backend.

Source trajectory (rectilinear, no parallax):
    tau = (t - t0) / tE
    y1  = tau * cos(alpha) - u0 * sin(alpha)   # along binary axis
    y2  = tau * sin(alpha) + u0 * cos(alpha)   # perpendicular to binary axis

Failure modes classified per docs/phase3_2_design.md §4.2:
    - Python exception from native binding
    - NaN or Inf return value
    - A < 1.0 (magnification always >= 1 for any physical configuration)
All failures raise MicrolensingComputationError with the parameter dict.
"""
from __future__ import annotations

import numpy as np

from smig.microlensing.errors import MicrolensingComputationError

# VBBL tolerances used for all calls
_TOL = 1e-3
_REL_TOL = 1e-3


def magnification_2l1s(
    t_mjd: np.ndarray,
    t0: float,
    tE: float,
    u0: float,
    rho: float,
    alpha: float,
    q: float,
    s: float,
) -> np.ndarray:
    """Binary-lens finite-source magnification via VBBinaryLensing.BinaryMag2.

    Args:
        t_mjd: Time array (MJD).
        t0:    Time of closest approach to centre of mass (MJD).
        tE:    Einstein crossing time (days).
        u0:    Impact parameter at t0 (θ_E units).
        rho:   Source radius (θ_E units).
        alpha: Angle of source trajectory relative to binary axis (radians).
        q:     Mass ratio m2/m1.
        s:     Projected binary separation (θ_E units).

    Returns:
        Magnification array with same shape as t_mjd.

    Raises:
        MicrolensingComputationError: On any VBBL failure.
    """
    import VBBinaryLensing  # deferred import; module assertion in backends.py fires first

    vb = VBBinaryLensing.VBBinaryLensing()
    vb.Tol = _TOL
    vb.RelTol = _REL_TOL

    cos_a = np.cos(alpha)
    sin_a = np.sin(alpha)
    tau = (t_mjd - t0) / tE
    y1_arr = tau * cos_a - u0 * sin_a
    y2_arr = tau * sin_a + u0 * cos_a

    result = np.empty(len(t_mjd))
    for i, (y1, y2) in enumerate(zip(y1_arr, y2_arr)):
        params = {"s": s, "q": q, "y1": float(y1), "y2": float(y2), "rho": rho,
                  "t_mjd": float(t_mjd[i])}
        try:
            A = vb.BinaryMag2(s, q, float(y1), float(y2), rho)
        except Exception as exc:
            raise MicrolensingComputationError(params=params, cause=exc) from exc
        if np.isnan(A) or np.isinf(A) or A < 1.0:
            raise MicrolensingComputationError(
                params=params,
                cause=ValueError(f"Unphysical magnification A={A}"),
            )
        result[i] = A
    return result
