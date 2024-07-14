# FSK Signal Generator

This Python program generates an FSK (Frequency Shift Keying) signal using the square wave modulation method. The signal is then saved to a CSV file which can be imported into a signal generator or another program for analysis.

## Getting Started

To use this script, you will need to have Python installed on your computer. You also need to install the scipy and numpy libraries if you haven't already. You can do this using pip:

```
pip install scipy numpy
```

Once you have installed the required libraries, you can run the script by navigating to its directory in the terminal/command prompt and typing:

```
python fsk_signal_generator.py
```

## Input Data File

The input data file ("data.txt") should contain one character per line, where each character is either a '0' or a '1'. For example:

```
101010
111000
001100
110011
```

These are the binary representations of the numbers 2, 3, 6 and 7 respectively. You can use any text editor to create this file, save it with the name "data.txt", and then run the script as described above.

## Output CSV File

The resulting FSK signal is saved to a CSV file named "output.csv". This file contains one column of numbers representing the amplitude of the signal at each time sample. You can open this file in any spreadsheet program to view it.

## Settings

You can change the settings for the FSK signal generator by editing the `center_freq` and `deviation` variables in the script. These variables are defined in the `generate_fsk` function, which takes these values as arguments when generating the signal. You can also change the sampling frequency (`fs`) if you need a different value.

## License

This project is licensed under the MIT license. See the LICENSE file for more information.
