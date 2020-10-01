## Evaluator for the Social Distancing in Brazil during COVID-19 outbreak

This presents a project that uses the Google Mobility Report to analyze how
different mobility activities changed during the COVID-19 pandemic in Brazil.
It also shows statistics of other countries, but they are not highlighted or
focused, and they're present in the graphics for extra insight.

This project is written in Python, and it uses the Matplotlib, Numpy, and Pandas
libraries.

## About

Subjects:
* Retail
* Grocery
* Parks
* Transit
* Workplaces
* Residential

Countries:
* Brazil
* France
* Germany
* Greece
* India
* Italy
* Japan
* Netherlands
* Spain
* Sweden
* United Kingdom
* United States

Highlighted:
* Brazil's statistics.
* The mean of the values of the selected countries for each day.
* The comparison of the lowest point to the latest point of the report
(growth percentage).

## Output

![output](https://github.com/murilobnt/bc19ev/blob/master/data/brazil_covid19_evaluation.png?raw=true)

## How to run

Initial requirements:
* Python 3
* Pip

```sh
pip install -r requirements.txt
python3 evaluator.py
```

### License

BC19Ev is licensed under the [MIT License](https://github.com/murilobnt/bc19ev/blob/master/LICENSE).
