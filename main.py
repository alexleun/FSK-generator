import sys
from argparse import ArgumentParser
import numpy as np
from scipy.io import write_csv_rows
from scipy.signal import square

def generate_fsk(data, center_freq, deviation):
    fs = 1000000  # Sampling frequency in Hz
    t = np.arange(0, len(data), 1/fs)  # Time array
    carrier_freq = center_freq + deviation
    modulated_signal = square(2 * np.pi * carrier_freq * t, duty=0.5)

    return modulated_signal

def main():
    parser = ArgumentParser(description='Generate an FSK signal from a binary data file.')
    parser.add_argument('input_file', help='Path to the input binary data file')
    parser.add_argument('--frequency', type=int, default=50000, help='Center frequency in Hz (default: 50kHz)')
    parser.add_argument('--deviation', type=int, default=700, help='Deviation from center frequency in Hz (default: +- 700Hz)')
    args = parser.parse_args()

    with open(args.input_file, 'r') as f:
        data = [line.strip() for line in f]

    signal = generate_fsk(data, args.frequency, args.deviation)

    output_file = args.input_file.replace('.txt', '-fsk-{}.csv'.format(args.frequency))
    write_csv_rows(output_file, [list(signal)], header=None)

if __name__ == "__main__":
    main()
