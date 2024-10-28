# FSK Modulation and Demodulation: A Robust Python Implementation

This repository provides Python scripts for encoding and decoding Frequency-Shift Keying (FSK) signals. FSK is a digital modulation technique that represents digital data by variations in the frequency of a carrier wave. This implementation prioritizes accuracy and robustness, particularly in noisy environments.

## Key Features

* **`fsk-encode.py`:**  Encodes binary data into an FSK audio signal (WAV file).  Customize carrier frequency, frequency deviation, baud rate (bits per second), and sample rate.
* **`fsk-decode.py`:** Decodes FSK signals from WAV files, outputting the original binary data. Employs a refined Short-Time Fourier Transform (STFT) based algorithm for accurate frequency analysis.  Includes detailed logging for debugging.

## Enhanced Decoding Algorithm

This version boasts a significantly improved decoding algorithm compared to previous iterations:

* **Robust Peak Detection:**  A refined peak detection method minimizes the effects of noise and interference on decoding accuracy.
* **Precise Bit Synchronization:** The decoder utilizes the specified baud rate for precise bit boundary identification, eliminating synchronization errors.  **Crucially, the baud rate used for decoding *must* match the encoding baud rate.**
* **Improved Error Handling:** The code includes comprehensive error handling to gracefully manage various scenarios, such as invalid input parameters or file errors.
* **Detailed Logging:**  The decoder provides detailed logging at various levels (DEBUG, INFO, WARNING, ERROR, CRITICAL), allowing for in-depth analysis of the decoding process.

## Installation

This project requires several Python libraries. Install them using pip:

```bash
pip install numpy scipy wave librosa argparse matplotlib
```

The following libraries are used:

* **NumPy:** For numerical operations.
* **SciPy:** For signal processing functions (e.g., filtering).
* **Wave:** For WAV file I/O.
* **Librosa:** For audio analysis (STFT).
* **Argparse:** For command-line argument parsing.
* **Matplotlib:** (Optional) For visualizing spectrograms.

## Usage

### Encoding (`fsk-encode.py`)

Encode binary data:

```bash
python fsk-encode.py "101101001010" --frequency 10000 --deviation 500 --baud-rate 1000 --sample-rate 44100 --output encoded.wav --debug 20
```

* `"101101001010"`:  The binary data to encode.
* `--frequency 10000`: Carrier frequency (Hz).
* `--deviation 500`: Frequency deviation (Hz).
* `--baud-rate 1000`: Baud rate (bits per second).
* `--sample-rate 44100`: Sample rate (Hz).  (Default: 44100 Hz)
* `--output encoded.wav`: Output WAV file name. (Default: output.wav)
* `--debug 20`: Sets the logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL). Default is 20 (INFO).


### Decoding (`fsk-decode.py`)

Decode a WAV file:

```bash
python fsk-decode.py encoded.wav --frequency 10000 --deviation 500 --baud-rate 1000 --debug 10
```

* `encoded.wav`: Path to the WAV file.
* `--frequency 10000`: Carrier frequency (Hz) — *must match encoding*.
* `--deviation 500`: Frequency deviation (Hz) — *must match encoding*.
* `--baud-rate 1000`: Baud rate (bits per second) — *must match encoding*.
* `--debug 10`: Sets the logging level.  Use `--debug 10` for detailed DEBUG messages.


## Example Workflow

1. **Encode:** `python fsk-encode.py "11001100" --frequency 12000 --deviation 1000 --baud-rate 500 --output my_signal.wav --debug 20`
2. **Decode:** `python fsk-decode.py my_signal.wav --frequency 12000 --deviation 1000 --baud-rate 500 --debug 10`


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.  Ensure your code adheres to the existing style and includes comprehensive tests.
```
