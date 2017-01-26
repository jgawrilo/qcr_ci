#!/usr/bin/env python

import argparse
import logging
from flask import Flask, make_response, jsonify
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.restful.representations.json import output_json
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from elasticsearch import Elasticsearch
import simplejson as json
import subprocess
import pandas as pd
from io import StringIO
from datetime import datetime
import os

app = Flask(__name__)
api = Api(app)

logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ImpactPredictorAPI(Resource):
    def __init__(self, **kwargs):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('campaign_id', type=str, location='json')

        self.reqparse.add_argument('pre_start_date_time', type=str, location='json')
        self.reqparse.add_argument('pre_end_date_time', type=str, location='json')
        self.reqparse.add_argument('post_start_date_time', type=str, location='json')
        self.reqparse.add_argument('post_end_date_time', type=str, location='json')

        self.reqparse.add_argument('granularity', type=str, location='json')
        self.reqparse.add_argument('metrics', type=str, location='json')

        # Should be of the form "{\"hashtags\": \"benghazi\"}" for now
        self.reqparse.add_argument('treatment_filters', type=str, location='json')


        self.es = Elasticsearch([kwargs["esAddress"]])
        self.es_index = kwargs["esIndex"]

        # Which metrics are available.  Need to test combinations.
        self.metric_map = {
            "emotion":"emotion.display.value",
            "sentiment":"sentiment.display.value",
            "radicalization":"radicalization.display.value",
            "religiosity":"religiosity.display.value",
        }

        super(ImpactPredictorAPI, self).__init__()

    def runR_CausalImpact(self,data_location,pre_period_start,pre_period_end,post_period_start,post_period_end):
        # Run R process and captured printed output
        r_output = subprocess.check_output(["Rscript", "causal.R", 
            data_location,
            pre_period_start,
            pre_period_end,
            post_period_start,
            post_period_end], 
            universal_newlines=True)

        returned_data = StringIO(r_output)

        # First line is cumulative impact number
        cumulative_impact = returned_data.readline().strip()

        # Remainder is the timeseries prediction data
        time_series_data = pd.read_csv(returned_data,sep='\s+')

        return cumulative_impact, time_series_data

    # Function to flatten a metric for casual impact processessing
    def flatten(self,top_bucket,metrics):
        data = {}
        # For each metric, for each day, add the metric -> doc_count
        for metric in metrics.split("|"):
            metric = metric.strip()
            for b in top_bucket[metric]["buckets"]:
                data[metric + "." + b["key"]] = b["doc_count"]
        # return dict for time window
        return data

    def post(self):
        '''
            1) Slice control and target metrics for pre_start - post-end
            2) Write data to disk - DONE
            3) Call Causal Impact - DONE
            4) Wrangle and return results - DONE
        '''

        # Will this ever not be msg?
        index_doc_type = "msg"

        args = self.reqparse.parse_args()
        campaign_id = args["campaign_id"]

        # One of the keys in metric_map.  Can be multiple (e.g., emotion|sentiment)
        metrics = args["metrics"]

        # Need extensive testing here.
        treatment_filters = json.loads(args["treatment_filters"])

        logger.info('Request for campaign: ' + campaign_id)
        
        try:
            # Control query uses time range, campaign_id match, and sets up
            # aggregation inverval.  aggregations are added based on
            # metrics.
            control_query = {
                "query": {
                  "bool": {
                     "must": [
                        {
                           "constant_score": {
                              "filter": {
                                 "range": {
                                    "timestamp": {
                                       "gte": args["pre_start_date_time"],
                                       "lte": args["post_end_date_time"]
                                    }
                                 }
                              }
                           }
                        },
                        {
                           "match": {
                              "tags.campaignID": campaign_id
                           }
                        }
                     ]
                  }
               },
               "size": 0,
               "aggs": {
                  "metrics_over_time": {
                     "date_histogram": {
                        "field": "timestamp",
                        "interval": args["granularity"]
                     },
                     "aggregations": {
                     }
                  }
               }
            }

            # for each metric (separated by |), add the aggregation
            for metric in metrics.split("|"):
                metric = metric.strip()
                if metric in self.metric_map:
                    control_query["aggs"]["metrics_over_time"]["aggregations"][metric] = \
                    {"terms":{"field":self.metric_map[metric]}}
            

            # Run control query
            control_result = self.es.search(index=self.es_index, doc_type=index_doc_type, body=control_query)
            logger.info("Got %d Control Hits:" % control_result['hits']['total'])

            # Treatment query is control query + treatment_filters
            # This will eventually need work
            treatment_query = control_query
            treatment_query["query"]["bool"]["must"].append({"match":treatment_filters})

            # Run treatment query
            treatment_result = self.es.search(index=self.es_index, doc_type=index_doc_type, body=treatment_query)
            
            # Control Dict of days -> {metric1->count, metric2->count...}
            flattened_control_data = {top_bucket["key_as_string"].split("T")[0]:self.flatten(top_bucket,metrics) 
                for top_bucket in control_result["aggregations"]["metrics_over_time"]["buckets"]}

            # Create dataframe from control
            control_pd_data = pd.read_json(json.dumps(flattened_control_data),orient="index")

            # Treatment Dict of days -> {metric1->count, metric2->count...}
            treatment_flattened_data = {top_bucket["key_as_string"].split("T")[0]:self.flatten(top_bucket,metrics) 
                for top_bucket in treatment_result["aggregations"]["metrics_over_time"]["buckets"]}

            # Create dataframe from treatment
            treatment_pd_data = pd.read_json(json.dumps(treatment_flattened_data),orient="index")

            # For the Treatment prepend columns with "target."
            target_columns = ["target." + name for name in treatment_pd_data.columns]
            treatment_pd_data.columns = target_columns

            # Join Treatment and Control data based on time bin
            treament_control_data = pd.concat([control_pd_data, treatment_pd_data], axis=1)

            # Create filename for tmp file.  Will this work ok?
            tmp_filename = "./tmp/" + datetime.now().isoformat().replace(":","_") + ".txt"

            # Save file to disk
            treament_control_data.to_csv(tmp_filename ,sep=",",index_label="date",na_rep="0")

            # Finally run R Causal Impact
            
            impact, casual_impact_data = self.runR_CausalImpact(tmp_filename,
                args["pre_start_date_time"],
                args["pre_end_date_time"],
                args["post_start_date_time"],
                args["post_end_date_time"])
            
            # Remove tmp file.  Comment out if debugging
            os.remove(tmp_filename)

            # Turn into json
            ts_results = casual_impact_data.to_json(orient='index')
            ret_results = {"ts_results":json.loads(ts_results),"total_impact":impact}
            #logger.info(results)
            return ret_results
        except Exception as e:
            logger.info(e)
            if tmp_filename:
                os.remove(tmp_filename)
            return {}

'''
Deal with these later
'''
class HealthCheck(Resource):
    def get(self):
        return make_response(jsonify({"status": "ok"}), 200)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# Start

if __name__ == '__main__':
    logger.info('Starting Causal Impact Service.')

    # Read in config, set port
    config = json.load(open('./config.json'))
    port = config["impactServicePort"]

    api.add_resource(ImpactPredictorAPI, '/api/impact', resource_class_kwargs=config)

    api.add_resource(HealthCheck, '/api/health')

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    IOLoop.instance().start()

