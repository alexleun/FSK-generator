import argparse
import numpy as np
import wave
import struct
import logging

# Configure logging to output INFO, WARNING, and ERROR messages with timestamps
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_fsk_signal(bits, frequency, deviation, bit_duration=0.01, sample_rate=44100):
    """
    Generates an FSK (Frequency Shift Keying) signal from a binary string.

    Args:
        bits (str): The binary string representing the data to encode (e.g., "101100").
        frequency (float): The carrier frequency in Hz.
        deviation (float): The frequency deviation in Hz (difference between mark and space frequencies).
        bit_duration (float, optional): The duration of each bit in seconds. Defaults to 0.01 seconds.
        sample_rate (int, optional): The sample rate in Hz. Defaults to 44100 Hz.

    Returns:
        numpy.ndarray: A NumPy array containing the generated FSK signal.  Returns None if input is invalid.
    """
    try:
        # Validate input: Check if the input is a valid binary string
        if not all(bit in '01' for bit in bits):
            logging.error("Invalid input: bits string must contain only '0' and '1'.")
            return None

        num_bits = len(bits)
        total_samples = int(num_bits * bit_duration * sample_rate)
        signal = np.zeros(total_samples)

        # Calculate mark and space frequencies
        mark_frequency = frequency + deviation
        space_frequency = frequency - deviation

        # Generate the FSK signal
        sample_index = 0
        for bit in bits:
            frequency_to_use = mark_frequency if bit == '1' else space_frequency
            # Calculate the number of samples for the current bit
            num_samples_per_bit = int(bit_duration * sample_rate)
            # Generate a sine wave for the current bit
            t = np.linspace(0, bit_duration, num_samples_per_bit, endpoint=False)
            sine_wave = np.sin(2 * np.pi * frequency_to_use * t)
            # Add the sine wave to the signal
            signal[sample_index:sample_index + num_samples_per_bit] = sine_wave
            sample_index += num_samples_per_bit

        return signal

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        return None


def save_wav_file(file_path, signal, sample_rate):
    """Saves the generated FSK signal to a WAV file."""
    try:
        #Ensure signal is within the range [-1,1]
        signal = np.clip(signal,-1,1)
        #Scale to 16-bit range
        signal = (signal * 32767).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit samples
            wf.setframerate(sample_rate)
            wf.setnframes(len(signal))
            wf.writeframes(signal.tobytes())
        logging.info(f"FSK signal saved to {file_path}")
    except Exception as e:
        logging.exception(f"An error occurred while saving the WAV file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Encode data into an FSK signal')
    parser.add_argument('bits', type=str, help='Binary string to encode')
    parser.add_argument('--frequency', type=float, required=True, help='Carrier frequency in Hz')
    parser.add_argument('--deviation', type=float, required=True, help='Frequency deviation in Hz')
    parser.add_argument('--output', type=str, default='output.wav', help='Output WAV file name')
    args = parser.parse_args()

    signal = generate_fsk_signal(args.bits, args.frequency, args.deviation)
    if signal is not None:
        num_bits = len(args.bits)
        total_duration = num_bits * 0.01 # Assuming 10ms per bit
        num_samples = len(signal)
        logging.info(f"Generated FSK signal for bits: {args.bits}")
        logging.info(f"Number of bits: {num_bits}")
        logging.info(f"Total duration: {total_duration:.4f} seconds")
        logging.info(f"Number of samples: {num_samples}")
        logging.info(f"Bit duration used: 0.01 seconds")
        logging.info(f"Sample rate used: 44100 Hz")
        logging.info(f"Frequency used: {args.frequency} Hz")
        logging.info(f"Deviation used: {args.deviation} Hz")
        save_wav_file(args.output, signal, 44100)