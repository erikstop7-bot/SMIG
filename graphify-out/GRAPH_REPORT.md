# Graph Report - .  (2026-04-16)

## Corpus Check
- 44 files · ~45,809 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 915 nodes · 4061 edges · 36 communities detected
- Extraction: 20% EXTRACTED · 80% INFERRED · 0% AMBIGUOUS · INFERRED: 3235 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]

## God Nodes (most connected - your core abstractions)
1. `DetectorConfig` - 284 edges
2. `PSFConfig` - 237 edges
3. `STPSFProvider` - 180 edges
4. `DIAConfig` - 170 edges
5. `H4RG10Detector` - 165 edges
6. `SimulationConfig` - 154 edges
7. `FiniteSourceRenderer` - 144 edges
8. `RenderingConfig` - 133 edges
9. `CrowdedFieldConfig` - 133 edges
10. `DIAPipeline` - 131 edges

## Surprising Connections (you probably didn't know these)
- `FiniteSourceRenderer` --uses--> `smig/rendering/validation/test_source.py =======================================`  [INFERRED]
  smig/rendering/source.py → smig\rendering\validation\test_source.py
- `IPCConfig` --uses--> `Build or load a normalised 9x9 IPC kernel.          If ``config.ipc_kernel_pat`  [INFERRED]
  smig/config/schemas.py → smig\sensor\ipc.py
- `IPCConfig` --uses--> `Validate that a loaded IPC kernel has the expected shape.          Parameters`  [INFERRED]
  smig/config/schemas.py → smig\sensor\ipc.py
- `smig/config/optics_schemas.py ============================= Immutable, validated` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\optics_schemas.py → smig/config/schemas.py
- `Configuration for the WebbPSF-based point-spread function model.      Controls t` --uses--> `DetectorConfig`  [INFERRED]
  smig\config\optics_schemas.py → smig/config/schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (179): BaseModel, ChargeDiffusionModel, smig/sensor/charge_diffusion.py ================================ Charge diffus, Apply charge diffusion and BFE to a charge image.          Applies static Gaus, Charge diffusion and brighter-fatter effect (BFE) model.      Models lateral c, Apply a static Gaussian diffusion kernel.          Uses ``scipy.ndimage.gaussi, Apply the brighter-fatter effect via iterative Jacobi redistribution., OneOverFNoise (+171 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (112): _BoundedCache, _normalize_sca_id(), _quantize_field_position(), smig/optics/psf.py ================== Field-varying polychromatic PSF provider f, Clamp each coordinate to ``[0, 1]`` and round to 4 decimal places.      Prevents, Thread-safe bounded cache using an insertion-ordered LRU eviction policy.      E, Compute a normalized monochromatic PSF at a single wavelength.          The resu, Compute a polychromatic, jitter-convolved PSF.          Assembles the polychroma (+104 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (66): CrowdedFieldRenderer, smig/rendering/crowding.py =========================== Phase 2 crowded-field sce, Render all catalog neighbors into a stamp centred on         *stamp_center_detec, Render a static crowded-field background from a neighbor star catalog.      The, _validate_catalog(), _count_filtered_neighbors(), _derive_event_seed(), _derive_stage_seed() (+58 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (44): Render a single source into *stamp* in-place.          Parameters         ------, _col_centroid(), _flux_total(), _make_psf(), _make_stamp(), psf(), smig/rendering/validation/test_source.py =======================================, Point source (unresolved): total rendered flux == flux_e within 0.1%. (+36 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (41): EventSceneOutput, Phase 2 top-level orchestrator.      Wraps :class:`~smig.sensor.detector.H4RG10D, Simulate a complete microlensing event end-to-end.          Builds a DIA referen, Output of a single simulated microlensing event.      All stamp arrays are cropp, SceneSimulator, Field-varying polychromatic PSF provider for the Roman WFI.      Computes wavele, STPSFProvider, _make_source_params() (+33 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (19): _make_gaussian_kernel(), smig/rendering/dia.py ===================== Difference Image Analysis (DIA) pipe, Alard-Lupton fixed-kernel convolution matching (MVP).          Uses 3 spatially-, Dynamic central crop to science_stamp_size.          Crop boundaries are compute, Inverse-variance weighted coadd of baseline epochs in rate space.          Each, detector(), dia_config(), _make_backgrounds() (+11 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (39): DIAPipeline, Build a 2D Gaussian kernel, normalized so its sum equals 1.0.          The kerne, MVP Difference Image Analysis pipeline.      Parameters     ----------     confi, DIAConfig, Configuration for the Difference Image Analysis (DIA) pipeline.      Controls th, Reject configs where the detector array is smaller than the DIA stamp., DetectorConfig, Immutable, fully-validated configuration for one Roman WFI H4RG-10 SCA.      I (+31 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (36): CrowdedFieldConfig, Placeholder configuration for the CrowdedFieldRenderer rendering pipeline., Configuration for the crowded-field stamp-based image renderer.      Controls th, Top-level immutable configuration for a Phase 2 SMIG simulation run.      Compos, RenderingConfig, SimulationConfig, AC-4: Static-field difference must be noise-consistent with zero signal., Parse *filepath* with the AST and return (module_name, names_str) pairs. (+28 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (31): smig/config/optics_schemas.py ============================= Immutable, validated, derive_event_seed(), derive_stage_seed(), smig/config/seed.py =================== Deterministic, hierarchical seed derivat, Derive a reproducible seed for a single microlensing event.      Combines the ma, Derive a reproducible seed for a named pipeline stage within an event.      Take, test_derive_event_seed_deterministic(), test_derive_event_seed_deterministic_across_custom_namespace() (+23 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (9): _make_source_params(), _make_timestamps(), sim_config(), simulator(), smoke_output(), TestDeterminism, TestInputValidation, TestProvenancePhase2Fields (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (31): FiniteSourceRenderer, Render a single source profile into a GalSim Image stamp.      Supports two rend, AC-2: ideal_image_e sum before detector is within 0.1% of injected flux., FiniteSourceRenderer.render_source must place flux_e e⁻ in the stamp.          C, |mean(residuals)| < 3 * std(residuals) / sqrt(N).          Tests the null hypoth, RMS of residuals must be within 2× the expected noise level.          Expected t, Use tracemalloc to measure peak Python-layer memory during pipeline run., AC-9: Rendering code may only import smig.sensor.detector; sensor may not import (+23 more)

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (26): PSFConfig, Configuration for the WebbPSF-based point-spread function model.      Controls t, Number of in-process cache hits (memory cache only)., Number of in-process cache misses (memory cache only)., Compute a polychromatic, jitter-convolved PSF.          Assembles the polychroma, SHA-256 cache key for a pre-jitter monochromatic PSF.          Excludes jitter p, SHA-256 cache key for the final polychromatic jitter-convolved PSF.          Inc, Lazily instantiate and return the WebbPSF Roman WFI instrument.          Uses do (+18 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (16): smig/sensor/persistence.py =========================== Two-component exponential, Two-component exponential persistence (residual image) model.      Tracks trappe, Apply persistence injection to a charge image.          Parameters         -----, # TODO: Implement physical model — two-component exponential decay from, # TODO: Apply exponential decay using delta_time_s and update, ChargeDiffusionTuning, ElectricalConfig, EnvironmentConfig (+8 more)

### Community 13 - "Community 13"
Cohesion: 0.14
Nodes (17): _collect_py_files(), _dia_setup(), _extract_imports(), _force_analytic_psf_backend(), _make_sim_config(), _make_small_detector(), smig/rendering/validation/test_integration_phase2.py ===========================, Return a DetectorConfig with overridden geometry (all other defaults). (+9 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (11): _find_bracket(), generate_synthetic_ipc_hdf5(), load_interpolated_kernel(), smig/sensor/calibration/ipc_kernels.py =======================================, Load and bilinearly interpolate an IPC kernel from an HDF5 file.      Paramete, # TODO: Memory optimization - slice specific neighborhood instead of, Find the lower grid index and fractional offset for interpolation.      Parame, Generate a synthetic HDF5 IPC kernel calibration file.      Creates spatially- (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.19
Nodes (9): Write *manifest_data* to a temp file, run validate_splits.py, return exit code., AC-10: validate_splits.py returns correct exit codes for leaky/clean manifests., No violations in a well-separated manifest → exit 0., Same event_id in two different splits → exit 1., Same starfield_seed in two different splits → exit 1., Events with all params within 5%% in different splits → exit 1., Similar params in the SAME split are allowed (no cross-split leakage) → exit 0., _run_validate_script() (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.21
Nodes (8): Convenience wrapper: construct SceneSimulator and run simulate_event., AC-6: Same (master_seed, event_id) → identical outputs., Float difference stamps: assert_allclose(rtol=1e-6, atol=1e-8)., Bool saturation masks: assert_array_equal (exact)., Bool CR masks: assert_array_equal (exact)., model_dump(mode='json') must match for every provenance record., _run_simulator(), TestSeedDeterminism

### Community 17 - "Community 17"
Cohesion: 0.29
Nodes (6): smig/provenance/schema.py ========================= Pydantic v2 model representi, Recursively convert numpy types in an RNG state dict to native Python.      Conv, _sanitize_numpy_types(), sanitize_rng_state(), test_sanitize_rng_state_rejects_non_dict(), smig/provenance/tracker.py ========================== Accumulates ProvenanceReco

### Community 18 - "Community 18"
Cohesion: 0.29
Nodes (1): smig.sensor.noise — Noise leaf modules for the H4RG-10 detector chain.

### Community 19 - "Community 19"
Cohesion: 0.33
Nodes (5): _aperture_flux(), Sum pixels within *radius* px of *(cx, cy)*, subtract edge background.      Impl, AC-3: Aperture photometry on rate_image * t_exp_s recovers flux within 5%., H4RG10Detector must conserve total photon flux through the signal chain., TestDetectorFluxConservation

### Community 20 - "Community 20"
Cohesion: 0.5
Nodes (3): get_peak_memory_mb(), smig/sensor/memory_profiler.py ================================ Peak memory meas, Return peak resident memory consumed so far, in megabytes.      Returns     ----

### Community 21 - "Community 21"
Cohesion: 0.5
Nodes (3): smig/sensor/noise/correlated.py ================================ Correlated nois, # TODO: Implement physical model — generate 1/f noise via FFT-based, # TODO: Implement physical model — sample a two-state Markov chain

### Community 22 - "Community 22"
Cohesion: 0.67
Nodes (2): smig/sensor/noise/cosmic_rays.py ================================= Clustered cos, # TODO: Implement physical model — sample hit positions, energies, and

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): smig/rendering/source.py ======================== Phase 2 source-profile renderi

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Inject 1/f correlated noise into an image.          Parameters         ---------

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Inject RTS noise into an image.          Parameters         ----------         i

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Inject cosmic-ray hits into a single read of a 3D MULTIACCUM ramp.          Inte

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Validate *df* and return a clean copy.          Enforces         --------

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Prevent analytic kernel from producing a negative centre pixel.          For t

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Sanitize numpy types in dict-form state; pass strings through unchanged.

## Knowledge Gaps
- **74 isolated node(s):** `Return ``True`` if every parameter in both dicts is within 5%% of the other.`, `Validate *manifest* for data leakage.  Return list of violation strings.      An`, `Parse arguments, validate manifest, print results, return exit code.`, `smig/rendering/source.py ======================== Phase 2 source-profile renderi`, `Render a single source profile into a GalSim Image stamp.      Supports two rend` (+69 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 23`** (2 nodes): `source.py`, `smig/rendering/source.py ======================== Phase 2 source-profile renderi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (2 nodes): `.apply()`, `Inject 1/f correlated noise into an image.          Parameters         ---------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (2 nodes): `Inject RTS noise into an image.          Parameters         ----------         i`, `.apply()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (2 nodes): `.inject_into_ramp()`, `Inject cosmic-ray hits into a single read of a 3D MULTIACCUM ramp.          Inte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Validate *df* and return a clean copy.          Enforces         --------`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Prevent analytic kernel from producing a negative centre pixel.          For t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Sanitize numpy types in dict-form state; pass strings through unchanged.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DetectorConfig` connect `Community 6` to `Community 0`, `Community 2`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 15`, `Community 16`, `Community 19`, `Community 21`, `Community 22`, `Community 24`, `Community 25`, `Community 26`?**
  _High betweenness centrality (0.287) - this node is a cross-community bridge._
- **Why does `PSFConfig` connect `Community 11` to `Community 0`, `Community 1`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 13`, `Community 15`, `Community 16`, `Community 19`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `FiniteSourceRenderer` connect `Community 10` to `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 9`, `Community 11`, `Community 13`, `Community 15`, `Community 16`, `Community 19`, `Community 23`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 281 inferred relationships involving `DetectorConfig` (e.g. with `EventSceneOutput` and `SceneSimulator`) actually correct?**
  _`DetectorConfig` has 281 INFERRED edges - model-reasoned connections that need verification._
- **Are the 234 inferred relationships involving `PSFConfig` (e.g. with `TestSmokeFullPipeline` and `TestDeterminism`) actually correct?**
  _`PSFConfig` has 234 INFERRED edges - model-reasoned connections that need verification._
- **Are the 163 inferred relationships involving `STPSFProvider` (e.g. with `EventSceneOutput` and `SceneSimulator`) actually correct?**
  _`STPSFProvider` has 163 INFERRED edges - model-reasoned connections that need verification._
- **Are the 167 inferred relationships involving `DIAConfig` (e.g. with `DIAPipeline` and `smig/rendering/dia.py ===================== Difference Image Analysis (DIA) pipe`) actually correct?**
  _`DIAConfig` has 167 INFERRED edges - model-reasoned connections that need verification._