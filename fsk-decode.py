import argparse
import numpy as np
from scipy.io import wavfile
import librosa

def decode_fsk(file_path, frequency, deviation, sample_rate=44100, window_size=1024, hop_length=512):
    """Decodes an FSK signal from a WAV file."""

    # Load the WAV file
    sr, data = wavfile.read(file_path)
    
        #Normalize and convert to float32 if necessary
    if data.dtype != np.float32:
        data = data.astype(np.float32) / np.iinfo(data.dtype).max

    # Perform Short-Time Fourier Transform (STFT)
    stft = librosa.stft(data, n_fft=window_size, hop_length=hop_length)
    magnitudes = np.abs(stft)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=window_size)

    # Find peak frequencies for each frame
    peak_frequencies = []
    for frame in magnitudes.T:
        peak_index = np.argmax(frame)
        peak_frequencies.append(frequencies[peak_index])

    # Decode the data based on peak frequencies
    decoded_data = ""
    threshold = frequency
    for freq in peak_frequencies:
        if freq > threshold:
            decoded_data += "1"
        else:
            decoded_data += "0"

    print("Decoded data:", decoded_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode FSK signal')
    parser.add_argument('file_path', type=str, help='Path to the WAV file')
    parser.add_argument('--frequency', type=float, default=10000, help='Carrier frequency')
    parser.add_argument('--deviation', type=float, default=500, help='Frequency deviation')
    args = parser.parse_args()
    decode_fsk(args.file_path, args.frequency, args.deviation)