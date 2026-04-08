# Graph Report - .  (2026-04-08)

## Corpus Check
- Corpus is ~10,967 words - fits in a single context window. You may not need a graph.

## Summary
- 35 nodes · 38 edges · 6 communities detected
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `H4RG10Detector Orchestrator` - 12 edges
2. `SpatiotemporalTrigger Stage A Classifier` - 5 edges
3. `ProvenanceTracker` - 4 edges
4. `MicroluxEngine (Physics Engine)` - 4 edges
5. `FieldDependentIPC Module` - 3 edges
6. `DetectorConfig (Pydantic v2)` - 3 edges
7. `STPSFProvider (Optical PSF)` - 3 edges
8. `CrowdedFieldRenderer` - 3 edges
9. `BAGLE Orbital Dynamics` - 3 edges
10. `ChargeDiffusionModel + BFE` - 2 edges

## Surprising Connections (you probably didn't know these)
- `CycleGAN Noise-Domain Transfer` --conceptually_related_to--> `H4RG10Detector Orchestrator`  [INFERRED]
  graphify-out/converted/smig_v2_phases2to6_spec_5787f657.md → graphify-out/converted/smig_v2_phase1_spec_d6fa7396.md
- `STPSFProvider (Optical PSF)` --references--> `DetectorConfig (Pydantic v2)`  [INFERRED]
  graphify-out/converted/smig_v2_phases2to6_spec_5787f657.md → graphify-out/converted/smig_v2_phase1_spec_d6fa7396.md
- `CrowdedFieldRenderer` --calls--> `H4RG10Detector Orchestrator`  [EXTRACTED]
  graphify-out/converted/smig_v2_phases2to6_spec_5787f657.md → graphify-out/converted/smig_v2_phase1_spec_d6fa7396.md
- `Reproducibility Contract` --conceptually_related_to--> `ProvenanceTracker`  [INFERRED]
  graphify-out/converted/smig_v2_phases2to6_spec_5787f657.md → graphify-out/converted/smig_v2_phase1_spec_d6fa7396.md

## Hyperedges (group relationships)
- **H4RG10 Fixed Signal Chain** — smig_v2_phase1_H4RG10Detector, smig_v2_phase1_ChargeDiffusionModel, smig_v2_phase1_FieldDependentIPC, smig_v2_phase1_DynamicPersistence, smig_v2_phase1_NonLinearityModel, smig_v2_phase1_MultiAccumSimulator, smig_v2_phase1_ClusteredCosmicRayInjector [EXTRACTED 1.00]
- **Stage A Classifier Architecture** — smig_v2_phases2to6_SpatiotemporalTrigger, smig_v2_phases2to6_NeuralCDE, smig_v2_phases2to6_EfficientNetEncoder, smig_v2_phases2to6_TriggerCalibrator [EXTRACTED 1.00]
- **Reproducibility Triad** — smig_v2_phases2to6_ReproducibilityContract, smig_v2_phase1_ProvenanceTracker, smig_v2_phase1_DetectorConfig, smig_v2_phases2to6_SnakemakeDVC [EXTRACTED 0.95]

## Communities

### Community 0 - "Detector Readout and Noise"
Cohesion: 0.22
Nodes (9): ClusteredCosmicRayInjector, DynamicPersistence Module, H4RG10Detector Orchestrator, MultiAccumSimulator, Nonlinearity Calibration Loader, NonLinearityModel, OneOverFNoise (1/f Noise), RTSNoise (Random Telegraph Signal) (+1 more)

### Community 1 - "Classifier and Training"
Cohesion: 0.22
Nodes (9): Ablation Plan (A3 vs A5), Data Leakage Prevention Policy, EfficientNet-B0 Spatial Encoder, Multi-Window Event Handling, Neural CDE Temporal Encoder, Three-Tier Prior Separation Policy, SpatiotemporalTrigger Stage A Classifier, Stage B Parameter Estimation (HMC) (+1 more)

### Community 2 - "Config Provenance Reproducibility"
Cohesion: 0.4
Nodes (5): DetectorConfig (Pydantic v2), ProvenanceRecord (Pydantic), ProvenanceTracker, Reproducibility Contract, Snakemake + DVC Workflow Orchestration

### Community 3 - "IPC and Charge Physics"
Cohesion: 0.5
Nodes (4): ChargeDiffusionModel + BFE, FieldDependentIPC Module, HDF5 Field-Dependent IPC Kernel Loader, Fixed Signal Chain Order Rationale

### Community 4 - "Optical Rendering and Scene"
Cohesion: 0.5
Nodes (4): CrowdedFieldRenderer, FiniteSourceRenderer, Physics-Aware Augmentation, STPSFProvider (Optical PSF)

### Community 5 - "Microlensing Physics Engine"
Cohesion: 0.67
Nodes (4): BAGLE Orbital Dynamics, MicroluxEngine (Physics Engine), VBMicrolensing (Validation Reference), Xallarap (1L2S Orbital Motion)

## Knowledge Gaps
- **16 isolated node(s):** `DynamicPersistence Module`, `MultiAccumSimulator`, `OneOverFNoise (1/f Noise)`, `RTSNoise (Random Telegraph Signal)`, `ClusteredCosmicRayInjector` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `H4RG10Detector Orchestrator` connect `Detector Readout and Noise` to `Config Provenance Reproducibility`, `IPC and Charge Physics`, `Optical Rendering and Scene`?**
  _High betweenness centrality (0.594) - this node is a cross-community bridge._
- **Why does `STPSFProvider (Optical PSF)` connect `Optical Rendering and Scene` to `Config Provenance Reproducibility`?**
  _High betweenness centrality (0.501) - this node is a cross-community bridge._
- **Why does `MicroluxEngine (Physics Engine)` connect `Microlensing Physics Engine` to `Optical Rendering and Scene`?**
  _High betweenness centrality (0.490) - this node is a cross-community bridge._
- **What connects `DynamicPersistence Module`, `MultiAccumSimulator`, `OneOverFNoise (1/f Noise)` to the rest of the system?**
  _16 weakly-connected nodes found - possible documentation gaps or missing edges._