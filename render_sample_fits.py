import numpy as np
import pandas as pd
from astropy.io import fits
from pathlib import Path

from smig.config.utils import load_simulation_config
from smig.rendering.pipeline import SceneSimulator

def main():
    # 1. Load the unified config (ensuring it's pulling the 256x256 geometry)
    config_path = Path("smig/config/simulation.yaml")
    config = load_simulation_config(config_path)

    # 2. Generate a synthetic neighbor catalog for the crowded field
    # (Simulating a moderately dense Bulge field)
    np.random.seed(42)
    n_stars = 150
    neighbor_catalog = pd.DataFrame({
        "x_pix": np.random.uniform(0, 256, n_stars),
        "y_pix": np.random.uniform(0, 256, n_stars),
        "flux_e": np.random.lognormal(mean=5.0, sigma=1.5, size=n_stars),
        "mag_w146": np.random.uniform(18.0, 26.0, n_stars)
    })

    # 3. Create a mock source sequence (e.g., 3 epochs of a rising microlensing event)
    # Using a resolved source size typical for Roman (rho* ~ 0.05")
    epochs = 3
    timestamps_mjd = np.array([60000.0, 60000.1, 60000.2])
    epochs = 3
    timestamps_mjd = np.array([60000.0, 60000.1, 60000.2])
    
    # ADD THIS: Mock a constant sky background of 0.5 e-/s for all 3 epochs
    backgrounds_e_per_s = np.full(epochs, 0.5)
    base_flux = 5000.0
    source_params_seq = []
    for i in range(epochs):
        magnification = 1.0 + (i * 2.5) # Simulating a rise in magnification
        source_params_seq.append({
            "flux_e": base_flux * magnification,
            "centroid_offset_pix": (0.1, -0.05), # Slight sub-pixel offset
            "rho_star_arcsec": 0.05, 
            "limb_darkening_coeffs": None
        })

    # 4. Initialize the orchestrator
    print("Initializing SceneSimulator (this will warm up the STPSF cache)...")
    simulator = SceneSimulator(config, master_seed=999)

    # Inject the mock catalog into the renderer's state (since Phase 3 catalogs aren't wired yet)
    # Note: Depending on your exact pipeline.py init, you may need to pass the catalog in differently.
# Safely find whatever Claude Code named the crowded field renderer attribute
    for attr_name in dir(simulator):
        if 'crowd' in attr_name.lower():
            renderer_instance = getattr(simulator, attr_name)
            # Inject the catalog into the renderer
            renderer_instance._catalog = neighbor_catalog
            print(f"Successfully injected custom catalog into simulator.{attr_name}")
            break
    # 5. Run the end-to-end event
    # 5. Run the end-to-end event
    print(f"Simulating {epochs} epochs through optics and detector physics...")
    event_output = simulator.simulate_event(
        event_id="test_ob260001",
        source_params_sequence=source_params_seq,
        timestamps_mjd=timestamps_mjd,
        backgrounds_e_per_s=backgrounds_e_per_s  # <-- ADD THIS LINE
    )
    # 6. Save outputs to FITS
    output_dir = Path("sample_fits_output")
    output_dir.mkdir(exist_ok=True)

    # Depending on how EventSceneOutput is structured, extract the cubes.
    # Assuming standard attribute names based on the spec:
    for i in range(epochs):
        # Full 256x256 detector rate image (e-/s)
        full_rate_fits = output_dir / f"epoch_{i}_rate_256x256.fits"
        fits.writeto(full_rate_fits, event_output.rate_cube[i], overwrite=True)
        
        # 64x64 DIA difference stamp
        # (Assuming your pipeline returns the extracted stamps in a list or array)
        if hasattr(event_output, 'dia_stamps'):
            dia_fits = output_dir / f"epoch_{i}_dia_64x64.fits"
            fits.writeto(dia_fits, event_output.dia_stamps[i], overwrite=True)

    print(f"Success! FITS files saved to {output_dir.absolute()}")

if __name__ == "__main__":
    main()