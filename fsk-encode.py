import argparse
import numpy as np
import wave
import struct
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_fsk_signal(bits, frequency, deviation, baud_rate, sample_rate=44100):
    """Generates an FSK signal from a binary string using baud rate."""
    try:
        if not all(bit in '01' for bit in bits):
            logging.error("Invalid input: bits string must contain only '0' and '1'.")
            return None

        bit_duration = 1.0 / baud_rate
        num_bits = len(bits)
        total_samples = int(num_bits * bit_duration * sample_rate)
        signal = np.zeros(total_samples)

        mark_frequency = frequency + deviation
        space_frequency = frequency - deviation

        sample_index = 0
        for bit in bits:
            frequency_to_use = mark_frequency if bit == '1' else space_frequency
            num_samples_per_bit = int(bit_duration * sample_rate)
            t = np.linspace(0, bit_duration, num_samples_per_bit, endpoint=False)
            sine_wave = np.sin(2 * np.pi * frequency_to_use * t)
            signal[sample_index:sample_index + num_samples_per_bit] = sine_wave
            sample_index += num_samples_per_bit

        return signal

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        return None


def save_wav_file(file_path, signal, sample_rate):
    """Saves the generated FSK signal to a WAV file."""
    try:
        signal = np.clip(signal, -1, 1)
        signal = (signal * 32767).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
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
    parser.add_argument('--baud-rate', type=float, required=True, help='Baud rate')
    parser.add_argument('--output', type=str, default='output.wav', help='Output WAV file name')
    parser.add_argument('--sample-rate', type=int, default=44100, help='Sample rate in Hz')
    parser.add_argument('--debug', type=int, default=20, choices=[10, 20, 30, 40, 50], help='Debug level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)')
    args = parser.parse_args()

    numeric_level = args.debug
    logging.basicConfig(level=numeric_level)

    signal = generate_fsk_signal(args.bits, args.frequency, args.deviation, args.baud_rate, args.sample_rate)
    if signal is not None:
        num_bits = len(args.bits)
        bit_duration = 1.0 / args.baud_rate
        total_duration = num_bits * bit_duration
        num_samples = len(signal)
        logging.info(f"Generated FSK signal for bits: {args.bits}")
        logging.info(f"Number of bits: {num_bits}")
        logging.info(f"Total duration: {total_duration:.4f} seconds")
        logging.info(f"Number of samples: {num_samples}")
        logging.info(f"Baud rate used: {args.baud_rate} baud")
        logging.info(f"Sample rate used: {args.sample_rate} Hz")
        logging.info(f"Frequency used: {args.frequency} Hz")
        logging.info(f"Deviation used: {args.deviation} Hz")
        save_wav_file(args.output, signal, args.sample_rate)