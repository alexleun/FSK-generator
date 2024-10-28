import argparse
import logging
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def estimate_fsk_parameters(file_path):
    """Estimates FSK parameters (center frequency, deviation range) from a WAV file using FFT."""
    try:
        sr, data = wavfile.read(file_path)
        logging.info(f"Detected sample rate: {sr} Hz")
    except FileNotFoundError:
        logging.error(f"File not found at {file_path}")
        return None, None, None
    except Exception as e:
        logging.error(f"Error reading WAV file: {e}")
        return None, None, None

    # Preprocessing: Remove DC component and apply a Hamming window
    data = data - np.mean(data)
    from scipy import signal
    data = data * signal.windows.hamming(len(data))

    # Perform FFT
    fft_data = fft(data)
    frequencies = fftfreq(len(data), 1 / sr)
    magnitudes = np.abs(fft_data)

    # Find peaks using scipy.signal.find_peaks (adjust parameters as needed)
    peaks, properties = find_peaks(magnitudes, height=1000, distance=500, prominence=500) #Increased parameters


    if len(peaks) < 2:
        logging.warning("Insufficient peaks found in FFT. FSK parameter estimation failed.")
        return None, None, None
        
        
    #Sort peaks by magnitude (height) in descending order
    peak_indices = np.argsort(properties["peak_heights"])[::-1]
    peak_frequencies = frequencies[peaks[peak_indices]][:2] #Take the two largest peaks

    #Estimate center frequency and deviation
    center_frequency = np.mean(peak_frequencies)
    deviation = np.abs(peak_frequencies[1] - peak_frequencies[0]) / 2

    #Calculate positive and negative deviation ranges
    positive_deviation = center_frequency + deviation
    negative_deviation = center_frequency - deviation

    #Plot the FFT for visualization (optional)
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, magnitudes)
    plt.plot(peak_frequencies, magnitudes[peaks[peak_indices][:2]], "x") #Mark peaks
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title("FFT of the Signal")
    plt.xlim(0, sr / 2)  # Show only positive frequencies
    plt.show()

    return center_frequency, deviation, (negative_deviation, positive_deviation)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Estimate FSK parameters from WAV file using FFT')
    parser.add_argument('file_path', type=str, help='Path to the WAV file')
    parser.add_argument('--debug', type=int, default=20, choices=[10, 20, 30, 40, 50], help='Debug level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)')
    args = parser.parse_args()

    numeric_level = args.debug
    logging.basicConfig(level=numeric_level)

    center_freq, deviation, deviation_range = estimate_fsk_parameters(args.file_path)

    if center_freq is not None:
        logging.info(f"Estimated center frequency: {center_freq:.2f} Hz")
        logging.info(f"Estimated frequency deviation: {deviation:.2f} Hz")
        logging.info(f"Estimated deviation range: {deviation_range[0]:.2f} Hz - {deviation_range[1]:.2f} Hz")
    else:
        logging.error("FSK parameter estimation failed.")