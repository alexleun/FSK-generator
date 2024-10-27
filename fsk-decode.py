import argparse
import numpy as np
from scipy.io import wavfile
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """Designs and applies a Butterworth bandpass filter."""
    nyq = 0.5 * fs
    if lowcut <= 0 or highcut >= nyq or lowcut >= highcut:
        print("Error: Invalid filter cutoff frequencies. Check lowcut and highcut values.")
        return data # Return original data if filter parameters are invalid

    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

def decode_fsk(file_path, frequency, deviation, sample_rate=44100, window_size=2048, hop_length=512):
    """Decodes an FSK signal from a WAV file."""

    try:
        sr, data = wavfile.read(file_path)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except wave.Error as e:
        print(f"Error reading WAV file: {e}")
        return

    if data.dtype != np.float32:
        data = data.astype(np.float32) / np.iinfo(data.dtype).max

    nyquist_frequency = sr / 2
    if frequency + deviation > nyquist_frequency:
        print(f"Error: Carrier frequency + deviation ({frequency + deviation} Hz) exceeds the Nyquist frequency ({nyquist_frequency} Hz). Reduce the carrier frequency.")
        return

    # Apply bandpass filter. Add error handling for invalid filter parameters.
    lowcut = frequency - deviation - 200  # Add margin for robustness
    highcut = frequency + deviation + 200  # Add margin for robustness
    filtered_data = butter_bandpass_filter(data, lowcut, highcut, sr)
    if filtered_data is None: # Check if filter application failed
        return


    stft = librosa.stft(filtered_data, n_fft=window_size, hop_length=hop_length)
    magnitudes = np.abs(stft)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=window_size)

    decoded_data = ""
    for frame in magnitudes.T:
        # Find the two highest peaks. Handle cases with fewer than 2 peaks.
        indices = np.argsort(frame)[-2:]
        if len(indices) < 2:
            print("Warning: Fewer than 2 peaks detected in a frame. Skipping frame.")
            continue
        peak_frequencies = frequencies[indices]

        if peak_frequencies[1] > frequency:
            decoded_data += "1"
        else:
            decoded_data += "0"


    # Plot the spectrogram
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.power_to_db(magnitudes, ref=np.max),
                             sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('FSK Spectrogram')
    plt.tight_layout()
    plt.show()

    print("Decoded data:", decoded_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode FSK signal')
    parser.add_argument('file_path', type=str, help='Path to the WAV file')
    parser.add_argument('--frequency', type=float, default=10000, help='Carrier frequency')
    parser.add_argument('--deviation', type=float, default=500, help='Frequency deviation')
    args = parser.parse_args()
    decode_fsk(args.file_path, args.frequency, args.deviation)