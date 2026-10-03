# My SIT225 4P PIR Desk Motion Project

## Why I made this repository

I made this private repository to keep the supporting files for my SIT225 Assessment 4P PIR desk-motion project in one place. My PIR sensor detects motion near my desk. It does not measure study time, attendance, focus, or productivity.

## Privacy

I will keep this repository private because my raw data contains timestamps from my personal desk experiment. I will share access only with my unit assessor for marking.

## Project files

- I stored my Arduino sketch and Python scripts in `code/`.
- I stored my raw CSV, test CSV, completed collection log, and processed CSV in `data/`.
- I stored my descriptive statistics, analysis results, and plots in `analysis/`.
- I stored my hardware photos and Arduino/Python screenshots in `evidence/`.

## Hardware and collection method

I used an Arduino Nano 33 IoT and a PIR sensor. My Arduino read the PIR input on D2 every five seconds. It sent 0 or 1 to my computer using USB serial at 9600 baud. My Python script saved the received readings with timestamps in a raw CSV file.

## Main results

- I collected 1,499 valid readings over 124 minutes and 50 seconds.
- I found support for H1: all five normal desk-work windows showed motion detected, with p = 0.0312.
- I did not find support for H2: all five empty-desk windows still showed motion detected, with p = 1.0000.
- I reduced stored records by 98.33% when I changed five-second raw data into five-minute summaries.

The H2 result is an important limitation in my project. My PIR sensor was too sensitive or detected environmental movement during empty-desk windows. I report this result honestly.

## Run the programs on Windows

I installed the required packages with:

```text
py -m pip install -r code/requirements.txt
```

I found my Arduino port with:

```text
py code/find_arduino_port.py
```

I collected data by replacing COM3 with my real port:

```text
py code/collect_pir_data.py --port COM3 --minutes 125 --output data/raw_pir_data.csv
```

I ran my analysis with:

```text
py code/analyse_pir_data.py --raw data/raw_pir_data.csv --log data/collection_log.csv --output-folder analysis
```

## Additional assessment evidence

I included my hardware photos, my Arduino serial screenshot, my Python collector screenshot, and my online soldering-module screenshot in `evidence/`. My online soldering screenshot shows that I completed the module and received 81% in the quiz. I also completed the in-person physical soldering induction. I could not see the physical certificate on my profile when I prepared my report, so I booked an appointment at the university on Tuesday to collect it. I will append the physical certificate to my final combined PDF when I receive it.

I will also append my Week 8.2C activity report to my final combined PDF submitted through the LMS.
