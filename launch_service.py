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


        self.es = Elasticsearch([kwargs["esAddress"]])
        self.es_index = kwargs["esIndex"]

        self.metric_map = {
            "emotion":"emotion.display.value",
            "sentiment":"sentiment.display.value",
            "radicalization":"radicalization.display.value",
            "religiosity":"religiosity.display.value",
        }

        super(ImpactPredictorAPI, self).__init__()

    def runR_CausalImpact(self,data_location,pre_period_start,pre_period_end,post_period_start,post_period_end):
        r_output = subprocess.check_output(["Rscript", "causal.R", 
            data_location,
            pre_period_start,
            pre_period_end,
            post_period_start,
            post_period_end], 
            universal_newlines=True)

        returned_data = StringIO(r_output)

        cumulative_impact = returned_data.readline().strip()

        time_series_data = pd.read_csv(returned_data,sep='\s+')

        return cumulative_impact, time_series_data

    def post(self):
        '''
            1) Slice control and target metrics for pre_start - post-end
            2) Write data to disk - DONE
            3) Call Causal Impact - DONE
            4) Wrangle and return results - DONE
        '''
        index_doc_type = "msg"

        args = self.reqparse.parse_args()
        campaign_id = args["campaign_id"]
        metrics = args["metrics"]

        logger.info('Request for campaign: ' + campaign_id)
        
        try:
            query = {
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

            for metric in metrics.split("|"):
                metric = metric.strip()
                if metric in self.metric_map:
                    query["aggs"]["metrics_over_time"]["aggregations"][metric] = \
                    {"terms":{"field":self.metric_map[metric]}}
            

            res = self.es.search(index=self.es_index, doc_type=index_doc_type, body=query)

            def flatten(top_bucket,metrics):
                data = {}
                for metric in metrics.split("|"):
                    metric = metric.strip()
                    for b in top_bucket[metric]["buckets"]:
                        data[metric + "." + b["key"]] = b["doc_count"]
                return data

            flattened_data = {top_bucket["key_as_string"].split("T")[0]:flatten(top_bucket,metrics) 
                for top_bucket in res["aggregations"]["metrics_over_time"]["buckets"]}
            logger.info(flattened_data)
            logger.info("Got %d Hits:" % res['hits']['total'])
            pd_data = pd.read_json(json.dumps(flattened_data),orient="index")
            pd_data.to_csv("./tmp/tmp.txt",sep=",",index_label="date")

            #for line in open("./tmp/tmp.txt"):
            #    logger.info(line)
            
            impact, data = self.runR_CausalImpact("./tmp/tmp.txt",
            args["pre_start_date_time"],
            args["pre_end_date_time"],
            args["post_start_date_time"],
            args["post_end_date_time"])
            ts_results = data.to_json(orient='index')
            results = {"ts_results":json.loads(ts_results),"total_impact":impact}
            #results = {"data":flattened_data,"impact":impact}
            logger.info(results)
            return results
        except Exception as e:
            logger.info(e)
            return {}

class HealthCheck(Resource):
    def get(self):
        return make_response(jsonify({"status": "ok"}), 200)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    logger.info('Starting Causal Impact Service.')
    config = json.load(open('./config.json'))
    port = config["impactServicePort"]

    api.add_resource(ImpactPredictorAPI, '/api/impact', resource_class_kwargs=config)

    api.add_resource(HealthCheck, '/api/health')

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    IOLoop.instance().start()

