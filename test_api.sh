#!/bin/bash

# Will always be good right now
# curl -XGET http://localhost:5001/api/health

# Will return JSON output to expect
curl -XPOST -H "Content-Type:application/json" http://localhost:5001/api/impact -d '{
  "pre_start_date_time":"2016-09-05T00:00:00.000Z",
  "pre_end_date_time":"2016-10-15T00:00:00.000Z",
  "post_start_date_time":"2016-10-16T00:00:00.000Z",
  "post_end_date_time":"2016-11-03T00:00:00.000Z",
  "interval": "daily",
  "series": [
    {
      "date": 1468281600,
      "control": 4035,
      "treatment": 141
    },
    {
      "date": 1468368000,
      "control": 2860,
      "treatment": 52
    },
    {
      "date": 1468454400,
      "control": 4560,
      "treatment": 79
    },
    {
      "date": 1468540800,
      "control": 16617,
      "treatment": 62
    },
    {
      "date": 1468627200,
      "control": 4038,
      "treatment": 47
    },
    {
      "date": 1468713600,
      "control": 3601,
      "treatment": 77
    },
    {
      "date": 1468800000,
      "control": 4454,
      "treatment": 109
    },
    {
      "date": 1468886400,
      "control": 5570,
      "treatment": 123
    },
    {
      "date": 1468972800,
      "control": 5589,
      "treatment": 239
    },
    {
      "date": 1469059200,
      "control": 42529,
      "treatment": 2167
    },
    {
      "date": 1469145600,
      "control": 46487,
      "treatment": 1852
    },
    {
      "date": 1469232000,
      "control": 90441,
      "treatment": 2378
    },
    {
      "date": 1469318400,
      "control": 73224,
      "treatment": 2713
    },
    {
      "date": 1469404800,
      "control": 98374,
      "treatment": 2313
    },
    {
      "date": 1469491200,
      "control": 31425,
      "treatment": 849
    },
    {
      "date": 1469577600,
      "control": 17009,
      "treatment": 444
    },
    {
      "date": 1469664000,
      "control": 9771,
      "treatment": 452
    },
    {
      "date": 1469750400,
      "control": 8236,
      "treatment": 371
    },
    {
      "date": 1469836800,
      "control": 15349,
      "treatment": 411
    },
    {
      "date": 1469923200,
      "control": 26446,
      "treatment": 501
    },
    {
      "date": 1470009600,
      "control": 11506,
      "treatment": 392
    },
    {
      "date": 1470096000,
      "control": 7399,
      "treatment": 445
    },
    {
      "date": 1470182400,
      "control": 9356,
      "treatment": 617
    },
    {
      "date": 1470268800,
      "control": 7181,
      "treatment": 512
    },
    {
      "date": 1470355200,
      "control": 9101,
      "treatment": 570
    },
    {
      "date": 1470441600,
      "control": 15350,
      "treatment": 832
    },
    {
      "date": 1470528000,
      "control": 11761,
      "treatment": 986
    },
    {
      "date": 1470614400,
      "control": 10494,
      "treatment": 600
    },
    {
      "date": 1470700800,
      "control": 15091,
      "treatment": 702
    },
    {
      "date": 1470787200,
      "control": 14900,
      "treatment": 1023
    },
    {
      "date": 1470873600,
      "control": 6868,
      "treatment": 466
    },
    {
      "date": 1470960000,
      "control": 3125,
      "treatment": 324
    },
    {
      "date": 1471046400,
      "control": 2352,
      "treatment": 271
    },
    {
      "date": 1471132800,
      "control": 841,
      "treatment": 73
    },
    {
      "date": 1471219200,
      "control": 608,
      "treatment": 30
    },
    {
      "date": 1471305600,
      "control": 922,
      "treatment": 38
    },
    {
      "date": 1471392000,
      "control": 4279,
      "treatment": 139
    },
    {
      "date": 1471478400,
      "control": 4173,
      "treatment": 224
    }
  ]
}'
