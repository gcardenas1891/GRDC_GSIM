# grdc_gsim

grdc_gsim is a Python script to combine monthly river discharges from two open source databases: the GRDC centre and the GSIM project.
The processing is based on a statistical evaluation carried out that compared the suitability to merge both datasets.
grdc_gsim allows you to specify the minimum Kling-Gupta Efficiency, the period od analysis and to make a visual assessment of the time-serial data per station.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install grdc_gsim.

```bash
pip install grdc_gsim
```

## Dependencies

python 3.9.12
pandas 1.4.2
numpy 1.21.6

## Usage

Access the script at './scr/code.py' and modify the variables within the module 'Input'.
The variables that can be adjusted are:
 - kge_limit : Minimum Kling-Gupta Efficiency value accepted for a station to be considered for merging [float]
 - period    : Period of analysis [list[int: initial_year, int: final_year]]
 - plot      : To specify if plottings should be displayed: [bool: True, False]
 - export    : To specify if plottings should be exported: [bool: True/False]

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
