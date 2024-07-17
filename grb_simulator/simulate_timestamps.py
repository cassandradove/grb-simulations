'''
Simulate Timestamps Class
Cassandra Dove 2024
This class can convert megalib .dat lightcurve files to a .txt file with simulated photon arrival times
Those .txt files can be used to test trigger algorithms
'''

import numpy as np
import os
from .config import define_paths

class simulate_timestamps() :
    # Input path : Megalib .dat lightcurve files
    # Output path : Where to store simulated photon lists
    # Random seed : Seed for reproducability
    def __init__(self, inputs):
        [self.input_path, self.output_path] = define_paths([inputs['input_path'], inputs['output_path']], [False, True])
        self.random_seed = inputs['random_seed']
        self.random = np.random.default_rng(seed=self.random_seed)
        self.simulated_background_duration = 30
        self.simulated_background_rate = 57

    # Returns a list of simulated photon arrival times given a dat lightcurve file with timestamps and counts
    def lightcurve_to_sim_timestamps(self, dat_file_name) :

        # Open file and extract timestamps/counts data
        path = os.path.join(self.input_path, dat_file_name)
        data = np.genfromtxt(path, skip_header=4, skip_footer=1, delimiter=' ', invalid_raise=False, usecols=(1, 2))
        timestamps = data[:, 0]
        counts = data [:, 1]
        
        # Create background rates for before burst
        background_before_burst = self.simulate_background(self.simulated_background_duration, self.simulated_background_rate)
        generated_timestamps = background_before_burst
        
        # Simulate photon arrivate timestamps given counts from .dat file
        index = 0
        for count in counts[1:] :
            generated_timestamps.extend(
                self.simulate_photon_arrival_times(
                    timestamps[index] + self.simulated_background_duration, 
                    timestamps[index + 1] + self.simulated_background_duration,
                    count
                )
            )
            index += 1
        
        generated_timestamps.append(timestamps[-1] + self.simulated_background_duration)
        
        # Add in background rates following burst
        background_after_burst = self.simulate_background(self.simulated_background_duration, self.simulated_background_rate)
        background_after_burst_addition = [b + generated_timestamps[-1] for b in background_after_burst]
        generated_timestamps.extend(background_after_burst_addition)

        return generated_timestamps

    # Returns a list of simulated photon arrival times within some interval, given a number of counts
    def simulate_photon_arrival_times(self, start_time, end_time, counts) :    
        if counts == 0 :
            return []
        elif counts == 1 :
            return [start_time]
        else :
            time_stamps = [start_time, end_time]
            # Adding divisions to the list (this will overshoot the counts number)
            while len(time_stamps) < counts :
                time_stamps = self.split_list(time_stamps)
            
            # Deleting indices until we have exactly counts indices
            while len(time_stamps) > counts :
                delete_index = self.random.integers(1, len(time_stamps) - 1)
                time_stamps.pop(delete_index)

            return time_stamps[:-1]

    # Generates a list of photon arrival times to simulate background rates
    def simulate_background(self, duration, rate) :
        background = [0]
        current_time = 0
        while current_time < duration :
            time_to_next = self.random.exponential(1/rate)
            current_time += time_to_next
            background.append(current_time)
        return background
 
    # Helper function that adds randomly placed and generated numbers in between each adjacent index of a list
    # Example -- [1,5,10] -> [1, 2.34, 5, 7.29, 10]
    def split_list(self, list) :
        i = 0
        while i < len(list) - 1 :
            list.insert(i + 1, self.random_split_generator(list[i], list[i + 1]))
            i += 2
        return list

    # Returns a time randomly split between a start_time and end_time
    def random_split_generator(self, start_time, end_time) :
        # Guaruntees we're splitting near but not exactly at the middle (balances even split distribution with some element of randomness)
        split_ratio = self.random.uniform(low=0.4, high=0.6, size=None)
        time_to_split = end_time - start_time
        return start_time + time_to_split * split_ratio

    # Loops through a directory and creates simulated photon arrival times based on lightcurve data
    def lightcurve_to_photon_arrivals(self) :
        i = 1
        len = self.dat_files_in_directory(self.input_path)

        for file in os.listdir(self.input_path) :
            if file.endswith('.dat'):
                filename = os.fsdecode(file)
                self.save_list(self.lightcurve_to_sim_timestamps(file), filename)
                print('(' + str(i) + '/' + str(len) + ') Saving ' + filename.rsplit('_')[0] + '_sim_times.dat...')
                i += 1

    # Returns number of .dat files in a directory
    def dat_files_in_directory(self, path) :
        count = 0
        for file in os.listdir(path) :
            if file.endswith('.dat') :
                count += 1  
        return count      

    # Saves a list as a .txt file 
    def save_list(self, list, filename) :
        path = os.path.join(self.output_path, filename.rsplit('_')[0] + '_sim_times.dat')
        file = open(path, 'w')
        for item in list :
            line = str(item) + '\n'
            file.write(line)
        file.close()

# Lines used to test class methods
#test_sim = simulate_timestamps('./example_scripts/example_yaml_files/test_lightcurve.dat')
#test_list = test_sim.lightcurve_to_sim_timestamps()
#print('length of test list: ' + str(len(test_list)))
# print(test_list)
# time_stamps = simulate_photon_arrival_times(0,10,10)
# print(time_stamps)
# print('\nlength: ' + str(len(time_stamps)))