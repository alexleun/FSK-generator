import numpy as np
import wave
import struct
import argparse
from scipy import signal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_fsk(data_bits, frequency, deviation, sample_rate=44100, bit_duration=0.01):
    """Generates an FSK signal."""

    bits = [int(bit) for bit in data_bits]
    num_bits = len(bits)
    total_duration = num_bits * bit_duration
    num_samples = int(sample_rate * total_duration)
    time = np.linspace(0, total_duration, num_samples, endpoint=False)

    signal_data = np.zeros(num_samples)
    for i, bit in enumerate(bits):
        start_sample = int(i * bit_duration * sample_rate)
        end_sample = int((i + 1) * bit_duration * sample_rate)
        frequency_to_use = frequency + deviation if bit else frequency - deviation

        signal_data[start_sample:end_sample] = np.sin(2 * np.pi * frequency_to_use * time[start_sample:end_sample])

    # Normalize the signal to float32 range (-1 to 1)
    signal_data = signal_data.astype(np.float32)

    # Log information about the generated signal
    logging.info(f"Generated FSK signal for bits: {data_bits}")
    logging.info(f"Number of bits: {num_bits}")
    logging.info(f"Total duration: {total_duration:.4f} seconds")
    logging.info(f"Number of samples: {num_samples}")
    logging.info(f"Bit duration used: {bit_duration:.4f} seconds")
    logging.info(f"Sample rate used: {sample_rate} Hz")
    logging.info(f"Frequency used: {frequency} Hz")
    logging.info(f"Deviation used: {deviation} Hz")


    with wave.open("output.wav", "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(4)  # Set sample width to 4 bytes for float32
        wf.setframerate(sample_rate)
        wf.setnframes(len(signal_data))
        wf.writeframes(signal_data.tobytes())

    print(f"FSK signal saved to output.wav")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate FSK signal')
    parser.add_argument('data_bits', type=str, help='Data bits as a string (e.g., "101100")')
    parser.add_argument('--frequency', type=float, default=10000, help='Carrier frequency')
    parser.add_argument('--deviation', type=float, default=500, help='Frequency deviation')
    parser.add_argument('--bit_duration', type=float, default=0.01, help='Duration of each bit in seconds')
    args = parser.parse_args()
    generate_fsk(args.data_bits, args.frequency, args.deviation, bit_duration=args.bit_duration)