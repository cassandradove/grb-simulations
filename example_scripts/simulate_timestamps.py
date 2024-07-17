from grb_simulator import parse_args, read_yaml
from grb_simulator import simulate_timestamps as sim

# Read input yaml file
input_file = parse_args([['-y', '--yaml', 'Path to input .yaml file']]).yaml
inputs = read_yaml(input_file)

# Create simulated photon arrival timestamps files
events = sim.simulate_timestamps(inputs)
events.lightcurve_to_photon_arrivals()
#events.make_spectra_lightcurves()