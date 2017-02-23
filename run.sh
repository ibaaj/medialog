#!/bin/bash

/usr/bin/python /home/admin/medialog/get-netflix.py >> /home/admin/medialog/log/log-netflix ;
/usr/bin/python /home/admin/medialog/get-allocine.py >> /home/admin/medialog/log/log-allocine ;
/usr/bin/python /home/admin/medialog/get-youtube.py >> /home/admin/medialog/log/log-youtube ;
/usr/bin/python /home/admin/medialog/get-review.py >> /home/admin/medialog/log/log-review ;
/usr/bin/python /home/admin/medialog/get-events.py >> /home/admin/medialog/log/log-events ;
/usr/bin/python /home/admin/medialog/get-series.py >> /home/admin/medialog/log/log-series ;

exit 0
