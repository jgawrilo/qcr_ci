#!/bin/bash

curl -XGET http://localhost:5001/api/health

curl -XPOST -H "Content-Type:application/json" http://localhost:5001/api/impact -d '{
    "campaign_id":"3d266bc5-7669-4389-b187-4efa931e0d8d",
    "pre_start_date_time":"2016-09-05T00:00:00.000Z",
    "pre_end_date_time":"2016-10-01T00:00:00.000Z",
    "post_start_date_time":"2016-10-02T00:00:00.000Z",
    "post_end_date_time":"2016-11-04T00:00:00.000Z",
    "metrics":"emotion",
    "granularity":"day"
}'






<<COMMENT

'{
    "esAddress":"http://10.1.92.76:9200",
    "esIndex":"qcr_app_pc_3d266bc5-7669-4389-b187-4efa931e0d8d",
    "campaignID":"3d266bc5-7669-4389-b187-4efa931e0d8d",
    "pre":{"start_date_time":"2016-01-01T00:00:00.000Z", "end_date_time":"2016-05-01T00:00:00.000Z"},
    "post":{"start_date_time":"2016-05-01T00:00:00.000Z", "end_date_time":"2017-01-01T00:00:00.000Z"},
    "granularity":"day"
}'

"2015-06-01", "2016-01-01", "2016-03-29", "2016-08-01"]

ES Address (e.g. http://10.1.92.76:9200)
ES Index (e.g. qcr_app_pc_3d266bc5-7669-4389-b187-4efa931e0d8d)
ES Type (optional - should be 'msg')
Pre-intervention start and end dates RFC3339 / ISO 8601 format
During intervention start and end dates, RFC3339 / ISO 8601 format
Post-intervention start and end dates, RFC3339 / ISO 8601 format
Granularity of output time series buckets (perhaps in seconds)
ES filters for:
pre-intervention period and control population
pre-intervention period and treatment population
pre-intervention period and all population
***Repeat the above 3 for "during intervention period" and "post-intervention period" as well
***TBD: Uncharted should do sampling to figure out which users to use and put them into the filters? Or we just give you the filters and you can sample?
COMMENT