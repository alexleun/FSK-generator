import numpy as np
from scipy.io import write_csv_rows
from scipy.signal import square

# Function to generate FSK signal
def generate_fsk(data, center_freq, deviation):
    fs = 1000000  # Sampling frequency in Hz
    t = np.arange(0, len(data), 1/fs)  # Time array
    carrier_freq = center_freq + deviation
    modulated_signal = square(2 * np.pi * carrier_freq * t, duty=0.5)

    return modulated_signal

# Read data from txt file
with open('data.txt', 'r') as f:
    data = [line.strip() for line in f]

# Set center frequency and deviation
center_freq = 50000  # Hz
deviation = 700  # Hz

# Generate FSK signal
signal = generate_fsk(data, center_freq, deviation)

# Write FSK signal to csv file
write_csv_rows('output.csv', [list(signal)], header=None)
