# FSK Signal Generator

This Python script generates an FSK signal from a binary data file and saves it to a CSV file with a "-fsk-<center-frequency>".csv extension appended to its name.

## Installation

To use this script, you will need to have Python installed on your computer. You can download Python from the official website: https://www.python.org/downloads/

Once you have Python installed, you can install the required dependencies by running the following command in your terminal or command prompt:

```
pip install numpy scipy
```

## Usage

To generate an FSK signal from a binary data file and save it to a CSV file, use the following command syntax in your terminal or command prompt:

```
python main.py <input-file> [--frequency] [--deviation] [--output]
```

Here are the details for each argument:

- `<input-file>` is the path to the input binary data file that you want to generate an FSK signal from.

- `[--frequency]` (optional) specifies the center frequency in Hz that you want the FSK signal to have (default: 50kHz). You can set this argument to any other value using the `--deviation` argument.

- `[--deviation]` (optional) specifies the deviation from the center frequency in Hz that you want the FSK signal to have (default: +-700Hz). You can set this argument to any other value using the `--frequency` argument.

- `[--output]` (optional) specifies the output file name. By default, the output file name will be based on the input file name, but with "-fsk-<center-frequency>".csv appended to it. For example, if your input file is named "data.txt", then the default output file name would be "data-fsk-50kHz.csv". If you want a different output file name, you can use this argument to set it.

To run your updated Python script from the command line and see its help message, simply type:

```
python main.py --help
```

This will display the usage information for your script. The `--help` option is used to indicate that the user wants to know more about how to use your script, so it is automatically executed by Python when you run your script from the command line.

## License

This project is licensed under the Apache-2.0 license. See the  Apache-2.0 LICENSE for more information.
