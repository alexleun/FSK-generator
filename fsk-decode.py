import argparse
import logging
import numpy as np
from scipy.io import wavfile
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import wave

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """
    Designs and applies a Butterworth bandpass filter.
    """
    nyq = 0.5 * fs
    if lowcut <= 0 or highcut >= nyq or lowcut >= highcut:
        logging.error("Invalid filter cutoff frequencies. Check lowcut and highcut values.")
        return data
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

def decode_fsk(file_path, frequency, deviation, bit_duration, window_size=2048, hop_length=512):
    """
    Decodes an FSK signal from a WAV file, automatically detecting the sample rate.

    Args:
        file_path (str): Path to the WAV file.
        frequency (float): The carrier frequency in Hz.
        deviation (float): The frequency deviation in Hz.
        bit_duration (float): Duration of each bit in seconds.
        window_size (int, optional): The window size for STFT. Defaults to 2048.
        hop_length (int, optional): The hop length for STFT. Defaults to 512.
    """
    try:
        # Read WAV file and automatically get sample rate
        sr, data = wavfile.read(file_path)
        logging.info(f"Detected sample rate: {sr} Hz")
    except FileNotFoundError:
        logging.error(f"File not found at {file_path}")
        return
    except wave.Error as e:
        logging.error(f"Error reading WAV file: {e}")
        return

    if data.dtype != np.float32:
        data = data.astype(np.float32) / np.iinfo(data.dtype).max

    nyquist_frequency = sr / 2
    if frequency + deviation > nyquist_frequency:
        logging.error(f"Carrier frequency + deviation ({frequency + deviation} Hz) exceeds the Nyquist frequency ({nyquist_frequency} Hz). Reduce the carrier frequency or increase the sample rate.")
        return

    lowcut = frequency - deviation - 200
    highcut = frequency + deviation + 200
    filtered_data = butter_bandpass_filter(data, lowcut, highcut, sr)
    if filtered_data is None:
        return

    stft = librosa.stft(filtered_data, n_fft=window_size, hop_length=hop_length)
    magnitudes = np.abs(stft)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=window_size)

    decoded_data = ""
    samples_per_bit = int(sr * bit_duration)
    num_frames = int(len(data) / samples_per_bit)

    for i in range(num_frames):
        start_sample = i * samples_per_bit
        end_sample = (i + 1) * samples_per_bit
        frame_magnitudes = magnitudes[:, int(start_sample / hop_length):int(end_sample / hop_length)]
        # Average across frames for better peak detection
        avg_magnitudes = np.mean(frame_magnitudes, axis=1)
        peak_index = np.argmax(avg_magnitudes)
        peak_frequency = frequencies[peak_index]

        if peak_frequency > frequency + deviation / 2:
            decoded_data += "1"
        else:
            decoded_data += "0"

    num_bits = len(decoded_data)
    total_duration = num_bits * bit_duration
    num_samples = len(data)

    logging.info(f"Decoded data: {decoded_data}")
    logging.info(f"Number of bits: {num_bits}")
    logging.info(f"Total duration: {total_duration:.4f} seconds")
    logging.info(f"Number of samples: {num_samples}")
    logging.info(f"Sample rate used: {sr} Hz")
    logging.info(f"Frequency used: {frequency} Hz")
    logging.info(f"Deviation used: {deviation} Hz")

    # Spectrogram plotting
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.power_to_db(magnitudes, ref=np.max),
                             sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('FSK Spectrogram')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode FSK signal')
    parser.add_argument('file_path', type=str, help='Path to the WAV file')
    parser.add_argument('--frequency', type=float, required=True, help='Carrier frequency in Hz')
    parser.add_argument('--deviation', type=float, required=True, help='Frequency deviation in Hz')
    parser.add_argument('--bit-duration', type=float, required=True, help='Duration of each bit in seconds')
    args = parser.parse_args()
    decode_fsk(args.file_path, args.frequency, args.deviation, args.bit_duration)