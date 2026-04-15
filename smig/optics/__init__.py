"""
smig.optics — Phase 2 optical rendering sub-package.

Provides PSF generation and optical diffraction modelling for the Roman WFI
crowded-field scene builder (CrowdedFieldRenderer).

NOTE: Phase 2 imports (galsim, webbpsf, poppy, synphot) must be guarded with
try/except ImportError blocks so that `import smig.optics` succeeds under a
base-only install.  Do NOT add bare top-level Phase 2 imports to this file.
"""
