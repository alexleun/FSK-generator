import argparse
import logging
import numpy as np
from scipy.io import wavfile
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, sosfiltfilt
import wave

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    if lowcut <= 0 or highcut >= nyq or lowcut >= highcut:
        logging.error("Invalid filter cutoff frequencies. Check lowcut and highcut values.")
        return None
    sos = butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos') # Use SOS for numerical stability
    y = sosfiltfilt(sos, data) # Use sosfiltfilt for zero-phase filtering
    return y

def find_dominant_frequencies(data, sample_rate, n, min_deviation=None):
    """Finds the top n most frequent frequencies in a WAV file using FFT."""
    
    # Preprocessing: Remove DC component and apply a Hamming window
    data = data - np.mean(data)
    from scipy import signal
    data = data * signal.windows.hamming(len(data))

    # Perform FFT
    fft_data = np.fft.fft(data)  # Use numpy's FFT function for compatibility
    frequencies = np.fft.fftfreq(len(data), d=1 / sample_rate)

    # Calculate magnitudes (exclude DC component at index 0)
    magnitudes = np.abs(fft_data[1:])  # Exclude the first element (DC offset)

    # Find indices of top n peaks in positive half
    peak_indices_positive = np.argsort(magnitudes)[-n:]
    
    # Collect all frequencies and their magnitudes
    all_peaks = []
    for idx in peak_indices_positive:
        freq_pos = frequencies[idx + 1]
        mag = magnitudes[idx]
        if freq_pos > 0:
            all_peaks.append((freq_pos, mag))

    # Consider negative half as well to ensure we capture the highest magnitude
    peak_magnitudes_sorted = np.argsort(magnitudes)[::-1][:n]
    for idx in peak_magnitudes_sorted:
        freq_neg = frequencies[idx + 1]
        if abs(freq_neg) > 0:  # Ensure we don't include zero frequency (DC component)
            mag = magnitudes[idx]
            all_peaks.append((abs(freq_neg), mag))

    # Remove duplicates and ensure sufficient deviation between peaks
    unique_peaks = []
    seen_frequencies = set()
    if min_deviation is None:
        for freq, mag in sorted(all_peaks, key=lambda x: -x[1]):
            if not (seen_frequencies and any(abs(f - freq) < 0.5 * abs(seen_frequencies.pop()) for f in seen_frequencies)):
                unique_peaks.append((freq, mag))
                seen_frequencies.add(freq)
    else:
        for freq, mag in sorted(all_peaks, key=lambda x: -x[1]):
            if not any(abs(f - freq) < min_deviation for f in seen_frequencies):
                unique_peaks.append((freq, mag))
                seen_frequencies.add(freq)

    # Select top n peaks based on magnitude
    peak_frequencies = [peak[0] for peak in sorted(unique_peaks, key=lambda x: -x[1])][:n]
    peak_magnitudes = [peak[1] for peak in sorted(unique_peaks, key=lambda x: -x[1])][:n]

    # Calculate middle frequency and deviation
    if len(peak_frequencies) >= 2:
        middle_frequency = (peak_frequencies[0] + peak_frequencies[1]) / 2
        logging.info(f"Middle frequency between detected frequency 1 and 2: {middle_frequency/1000:.2f} kHz")
        
        # Calculate deviation value
        freq_deviation = abs(peak_frequencies[0] - peak_frequencies[1])
        logging.info(f"Deviation from the middle frequency: {freq_deviation / 2:.2f} Hz")

    return peak_frequencies, sample_rate, magnitudes[:len(frequencies)-1], frequencies[1:], peak_magnitudes

def decode_fsk(file_path, frequency=None, deviation=None, bit_duration=0.0):
    try:
        sr, data = wavfile.read(file_path)
        logging.info(f"Original sample rate: {sr} Hz")
    except FileNotFoundError:
        logging.error(f"File not found at {file_path}")
        return
    except wave.Error as e:
        logging.error(f"Error reading WAV file: {e}")
        return

    # Resample to a lower rate
    data = librosa.resample(data.astype(np.float32), orig_sr=sr, target_sr=200000)
    sr = 200000
    logging.info(f"Resampled to: {sr} Hz")

    # Improved clipping check and normalization
    data = np.clip(data, -1, 1) # Clip values to prevent issues

    if frequency is None or deviation is None:
        peak_frequencies, _, _, _, _ = find_dominant_frequencies(data, sr, n=2)
        
        if len(peak_frequencies) < 2:
            logging.error("Failed to detect two dominant frequencies. Please provide manual values.")
            return

        middle_frequency = (peak_frequencies[0] + peak_frequencies[1]) / 2
        freq_deviation = abs(peak_frequencies[0] - peak_frequencies[1])
        
        frequency = middle_frequency if frequency is None else frequency
        deviation = freq_deviation if deviation is None else deviation

    nyquist_frequency = sr / 2
    if frequency + deviation > nyquist_frequency:
        logging.error(f"Carrier frequency + deviation ({frequency + deviation} Hz) exceeds the Nyquist frequency ({nyquist_frequency} Hz). Reduce the carrier frequency or increase the sample rate.")
        return

    lowcut = frequency - deviation - 200
    highcut = frequency + deviation + 200
    filtered_data = butter_bandpass_filter(data, lowcut, highcut, sr)
    if filtered_data is None:
        return

    stft = librosa.stft(filtered_data, n_fft=2048, hop_length=512)
    magnitudes = np.abs(stft)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=2048)

    decoded_data = ""
    samples_per_bit = int(sr * bit_duration)
    num_frames = int(np.ceil(len(filtered_data) / samples_per_bit)) # Corrected frame calculation

    for i in range(num_frames):
        start_sample = i * samples_per_bit
        end_sample = min((i + 1) * samples_per_bit, len(filtered_data))
        if start_sample >= len(filtered_data) or start_sample == end_sample:
            continue

        frame_magnitudes = magnitudes[:, int(start_sample / 512):int(end_sample / 512)]

        if frame_magnitudes.size == 0:
            continue

        avg_magnitudes = np.mean(frame_magnitudes, axis=1)
        peak_index = np.argmax(avg_magnitudes)
        peak_frequency = frequencies[peak_index]
        logging.debug(f"Frame {i}: Peak frequency = {peak_frequency:.2f} Hz") # Added logging

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
    logging.info(f"Frequency used: {frequency:.2f} Hz")
    logging.info(f"Deviation used: {deviation:.2f} Hz")

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.power_to_db(magnitudes, ref=np.max),
                             sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('FSK Spectrogram')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Auto-detect and decode FSK signal')
    parser.add_argument('file_path', type=str, help='Path to the WAV file')
    parser.add_argument('--frequency', type=float, required=False, default=None, help='Carrier frequency in Hz (optional)')
    parser.add_argument('--deviation', type=float, required=False, default=None, help='Frequency deviation in Hz (optional)')
    parser.add_argument('--baud-rate', type=float, required=True, help='Baud rate')
    parser.add_argument('--debug', type=int, default=20, choices=[10, 20, 30, 40, 50], help='Debug level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)')
    args = parser.parse_args()

    numeric_level = args.debug
    logging.basicConfig(level=numeric_level)

    bit_duration = 1.0 / args.baud_rate

    decode_fsk(args.file_path, frequency=args.frequency, deviation=args.deviation, bit_duration=bit_duration)
