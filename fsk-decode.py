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

    Args:
        data (numpy.ndarray): The input signal.
        lowcut (float): The lower cutoff frequency in Hz.
        highcut (float): The upper cutoff frequency in Hz.
        fs (float): The sample rate in Hz.
        order (int, optional): The filter order. Defaults to 5.

    Returns:
        numpy.ndarray: The filtered signal. Returns the original data if filter parameters are invalid.
    """
    nyq = 0.5 * fs
    if lowcut <= 0 or highcut >= nyq or lowcut >= highcut:
        logging.error("Invalid filter cutoff frequencies. Check lowcut and highcut values.")
        return data  # Return original data if filter parameters are invalid

    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

def decode_fsk(file_path, frequency, deviation, sample_rate=44100, window_size=2048, hop_length=512):
    """
    Decodes an FSK signal from a WAV file.

    Args:
        file_path (str): Path to the WAV file.
        frequency (float): The carrier frequency in Hz.
        deviation (float): The frequency deviation in Hz.
        sample_rate (int, optional): The sample rate in Hz. Defaults to 44100 Hz.
        window_size (int, optional): The window size for STFT. Defaults to 2048.
        hop_length (int, optional): The hop length for STFT. Defaults to 512.
    """
    try:
        sr, data = wavfile.read(file_path)
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
        logging.error(f"Carrier frequency + deviation ({frequency + deviation} Hz) exceeds the Nyquist frequency ({nyquist_frequency} Hz). Reduce the carrier frequency.")
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
    for frame in magnitudes.T:
        indices = np.argsort(frame)[-2:]
        if len(indices) < 2:
            logging.warning("Fewer than 2 peaks detected in a frame. Skipping frame.")
            continue
        peak_frequencies = frequencies[indices]

        if peak_frequencies[1] > frequency:
            decoded_data += "1"
        else:
            decoded_data += "0"

    num_bits = len(decoded_data)
    total_duration = num_bits * (1/sr) # Assuming 1 bit per sample
    num_samples = len(data)

    logging.info(f"Decoded data: {decoded_data}")
    logging.info(f"Number of bits: {num_bits}")
    logging.info(f"Total duration: {total_duration:.4f} seconds")
    logging.info(f"Number of samples: {num_samples}")
    logging.info(f"Sample rate used: {sr} Hz")
    logging.info(f"Frequency used: {frequency} Hz")
    logging.info(f"Deviation used: {deviation} Hz")

    # Plot the spectrogram (optional - remove if not needed)
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
    args = parser.parse_args()
    decode_fsk(args.file_path, args.frequency, args.deviation)