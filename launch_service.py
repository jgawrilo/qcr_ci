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
import datetime
import os

app = Flask(__name__)
api = Api(app)

logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ImpactPredictorAPI(Resource):
    def __init__(self, **kwargs):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('data', type=dict, location='json')

        super(ImpactPredictorAPI, self).__init__()

    def runR_CausalImpact(self,treatment_control_data,
        data_location,pre_period_start,pre_period_end,post_period_start,post_period_end):
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

        time_series_data.index.name = "string_date"

        orig = pd.concat([time_series_data,treatment_control_data],axis=1)

        orig = orig.set_index("date")

        orig.index = orig.index.map(int)

        orig["date"] = orig.index

        return float(cumulative_impact), orig

    def post(self):
        
        # Create filename for tmp file.  Will this work ok?

        args = self.reqparse.parse_args()

        treatment_control_data = pd.DataFrame.from_dict(args["data"]["series"])
        treatment_control_data["string_date"] = treatment_control_data.apply(
            lambda x: datetime.datetime.fromtimestamp(x['date']).isoformat().split("T")[0], axis=1)
        treatment_control_data = treatment_control_data.set_index("string_date")

        tmp_filename = "./tmp/" + datetime.datetime.now().isoformat().replace(":","_") + ".txt"

        # Save file to disk
        treatment_control_data.to_csv(tmp_filename ,sep=",",index_label="string_date",na_rep="0")

        # Finally run R Causal Impact
        
        impact, casual_impact_data = self.runR_CausalImpact(treatment_control_data,tmp_filename,
            datetime.datetime.fromtimestamp(args["data"]["pre_start"]).isoformat(),
            datetime.datetime.fromtimestamp(args["data"]["pre_end"]).isoformat(),
            datetime.datetime.fromtimestamp(args["data"]["post_start"]).isoformat(),
            datetime.datetime.fromtimestamp(args["data"]["post_end"]).isoformat()
        )
        
        # Remove tmp file.  Comment out if debugging
        #os.remove(tmp_filename)

        # Turn into json
        ts_results = casual_impact_data.to_json(orient='records')
        ret_results = {"ts_results":json.loads(ts_results),"total_impact":impact}
        return ret_results

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

