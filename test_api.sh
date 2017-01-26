#!/bin/bash

# Will always be good right now
# curl -XGET http://localhost:5001/api/health

# Will return JSON output to expect
curl -XPOST -H "Content-Type:application/json" http://localhost:5001/api/impact -d '{
    "campaign_id":"3d266bc5-7669-4389-b187-4efa931e0d8d",
    "pre_start_date_time":"2016-09-05T00:00:00.000Z",
    "pre_end_date_time":"2016-10-15T00:00:00.000Z",
    "post_start_date_time":"2016-10-16T00:00:00.000Z",
    "post_end_date_time":"2016-11-03T00:00:00.000Z",
    "metrics":"emotion",
    "granularity":"day",
    "control_filters":"",
    "treatment_filters":"{\"hashtags\": \"benghazi\"}"
}'