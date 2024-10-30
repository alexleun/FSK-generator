import argparse
import logging
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

# Configure logging for our application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress matplotlib's debug messages
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)

def find_dominant_frequencies(data, sample_rate, n, min_deviation):
    """Finds the top n most frequent frequencies in a WAV file using FFT."""
    
    # Preprocessing: Remove DC component and apply a Hamming window
    data = data - np.mean(data)
    from scipy import signal
    data = data * signal.windows.hamming(len(data))

    # Perform FFT
    fft_data = fft(data)
    frequencies = fftfreq(len(data), 1 / sample_rate)

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

def plot_fft(peak_frequencies, magnitudes, frequencies, sampling_rate):
    """Plots the FFT chart."""
    plt.figure(figsize=(14, 6))

    # Plot the FFT spectrum
    plt.plot(frequencies[:len(magnitudes)], magnitudes)
    
    # Highlight peak frequencies on the graph
    for freq in peak_frequencies:
        if freq > 0:  # Only plot positive frequencies to avoid double plotting
            plt.axvline(x=freq, color='r', linestyle='--')
        
    plt.title('FFT Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim(0, sampling_rate / 2)
    
    # Show plot
    plt.show()

def format_frequency(frequency):
    """Format frequency to a more readable unit."""
    if frequency >= 1e6:
        return f"{frequency / 1e6:.2f} MHz"
    elif frequency >= 1e3:
        return f"{frequency / 1e3:.2f} kHz"
    else:
        return f"{frequency:.2f} Hz"

def format_magnitude(magnitude):
    """Format magnitude to a more readable unit."""
    if magnitude >= 1e6:
        return f"{magnitude / 1e6:.4f} M"
    elif magnitude >= 1e3:
        return f"{magnitude / 1e3:.4f} K"
    else:
        return f"{magnitude:.4f}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find the top n most frequent frequencies in a WAV file')
    parser.add_argument('file_path', type=str, help='Path to the WAV file')
    parser.add_argument('--n', type=int, default=10, help='Number of dominant frequencies to find (default is 10)')
    parser.add_argument('--min-deviation', type=float, default=None, help='Minimum allowed deviation between peaks (in Hz). If not specified, defaults to the sample rate divided by the number of samples.')
    parser.add_argument('--debug', type=int, default=20, choices=[10, 20, 30, 40, 50], help='Debug level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)')
    args = parser.parse_args()

    numeric_level = args.debug
    logging.basicConfig(level=numeric_level)

    # Read the WAV file and get sample rate
    try:
        sr, data = wavfile.read(args.file_path)
        logging.info(f"Detected sample rate: {sr / 1000:.2f} kHz")
        
        if args.min_deviation is None:
            # If min deviation not specified, use a reasonable default value (sampling rate divided by the number of samples)
            min_deviation = 1.0 * args.n / len(data) if 'magnitudes' in locals() else 1.0
        else:
            min_deviation = args.min_deviation

        peak_frequencies, sampling_rate, magnitudes, frequencies, peak_magnitudes = find_dominant_frequencies(data, sr, args.n, min_deviation)

        if peak_frequencies is not None:
            for i, freq in enumerate(peak_frequencies):
                logging.info(f"Detected {i+1} most frequent frequency: {format_frequency(freq)}")
                logging.info(f"Magnitude of {i+1} most frequent frequency: {format_magnitude(peak_magnitudes[i])}")
            
            plot_fft(peak_frequencies, magnitudes[:len(frequencies)-1], frequencies[1:], sampling_rate)
        else:
            logging.error("Failed to detect frequencies or sample rate")

    except FileNotFoundError:
        logging.error(f"File not found at {args.file_path}")
    except Exception as e:
        logging.error(f"Error reading WAV file: {e}")
