# FSK Modulation and Demodulation

This repository contains Python scripts for encoding and decoding Frequency-Shift Keying (FSK) signals.  FSK is a digital modulation scheme that represents digital data as variations in the frequency of a carrier wave.

## Features

* **fsk-encode.py:** Encodes a binary string into an FSK signal and saves it as a WAV file.  Allows for customization of carrier frequency, frequency deviation, and bit duration.
* **fsk-decode.py:** Decodes an FSK signal from a WAV file and outputs the decoded binary string.  Uses Short-Time Fourier Transform (STFT) for frequency analysis.

## Installation

The code requires the following Python libraries:

* NumPy
* SciPy
* Wave
* Librosa
* Argparse
* Matplotlib (optional, for visualization - not used in core functionality)

You can install them using pip:

```bash
pip install numpy scipy wave librosa argparse matplotlib
```

## Usage

### Encoding (fsk-encode.py)

To encode data, run the script with the desired parameters:

```bash
python fsk-encode.py "10110100" --frequency 10000 --deviation 500 --bit_duration 0.01
```

This command will:

* Encode the binary string "10110100".
* Use a carrier frequency of 10000 Hz.
* Use a frequency deviation of 500 Hz.
* Set the bit duration to 0.01 seconds.

The resulting FSK signal will be saved as `output.wav`.  You can adjust the parameters as needed.  If parameters are omitted, default values will be used.


### Decoding (fsk-decode.py)

To decode a WAV file, run the script with the path to the WAV file and the encoding parameters used during encoding:

```bash
python fsk-decode.py output.wav --frequency 10000 --deviation 500
```

This command will:

* Decode the FSK signal from `output.wav`.
* Use a carrier frequency of 10000 Hz and a frequency deviation of 500 Hz (matching the encoding parameters).

The decoded binary string will be printed to the console.  Ensure the parameters used for decoding match those used for encoding.


## Example Workflow

1. **Encode:**  `python fsk-encode.py "1010101011" --frequency 12000 --deviation 750 > encoded.wav`
2. **Decode:** `python fsk-decode.py encoded.wav --frequency 12000 --deviation 750`


## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.


## License

[Specify your license here, e.g., MIT License]