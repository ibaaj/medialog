# Medialog

process of generating & updating this [spreadsheet](https://docs.google.com/spreadsheets/d/1Jg4Ejtahmq1o1CoEHvWhf5_hgSXamm4PRhuNdRfGXnA/) every day.

- new movies release
- new netflix US dvd release
- new Arte+7 video available
- new video on multiple Youtube channels
- new "night" events in Paris
- new music reviews from various source
- series schedule


## Requirements
You need a Google Sheets key and a Youtube API key - use [http://console.developers.google.com](console.developers.google.com)
The [Pygsheets](pygsheets.readthedocs.io)  python package available with pip to easily work with Google APIs.

## Launch

I run it with a cron at 6:00am every day.
```
0 6 * * * /bin/bash -c /home/admin/medialog/run.sh >> /home/admin/medialog/log/log-run
```

***

wtfpl license
