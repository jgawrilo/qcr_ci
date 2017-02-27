#!/usr/bin/env python

from rpy2.robjects import r
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from rpy2.rinterface import RRuntimeError

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

pandas2ri.activate()

ci = importr('CausalImpact')
base = importr('base')
devtools = importr('devtools')
dollar = base.__dict__['$']
at = base.__dict__['@']

logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ImpactPredictorAPI(Resource):
    def __init__(self, **kwargs):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('data', type=dict, location='json')

        super(ImpactPredictorAPI, self).__init__()

    def post(self):
        
        try:

            args = self.reqparse.parse_args()

            treatment_control_data = pd.DataFrame.from_dict(args["data"]["series"])

            time_df = treatment_control_data[["date"]]

            time_df.index = range(1,len(time_df)+1)

            logger.info("PRE-START:" +str(args["data"]["pre_start"]))
            logger.info("PRE-END:" +str(args["data"]["pre_end"]))
            logger.info("POST-START:" +str(args["data"]["post_start"]))
            logger.info("POST-END:" +str(args["data"]["post_end"]))
            logger.info("DATA:"+json.dumps(args["data"]["series"]))

            treatment_control_data = treatment_control_data[["target","control"]]

            treatment_control_data.index = range(1,len(treatment_control_data)+1)

            pre_start = time_df[time_df.date == args["data"]["pre_start"]].index[0]
            pre_end = time_df[time_df.date == args["data"]["pre_end"]].index[0]
            post_start = time_df[time_df.date == args["data"]["post_start"]].index[0]
            post_end = time_df[time_df.date == args["data"]["post_end"]].index[0]

            columns = [
                "response",
                "cum.response",
                "point.pred",
                "point.pred.lower",
                "point.pred.upper",
                "cum.pred",
                "cum.pred.lower",
                "cum.pred.upper",
                "point.effect",
                "point.effect.lower",
                "point.effect.upper",
                "cum.effect",
                "cum.effect.lower",
                "cum.effect.upper"
                ]

            r_data = pandas2ri.py2ri(treatment_control_data)
            pre = robjects.IntVector((pre_start,pre_end))
            post = robjects.IntVector((post_start,post_end))

            results = ci.CausalImpact(r_data,pre,post)

            py_out = pandas2ri.ri2py(results)

            dout = pandas2ri.ri2py_dataframe(dollar(py_out,"series"))

            dout.columns = columns

            dout.index = range(1,len(dout)+1)

            final = pd.concat([time_df,dout],axis=1)
            final.drop('cum.response', axis=1, inplace=True)
            final.drop('cum.pred.lower', axis=1, inplace=True)
            final.drop('cum.pred.upper', axis=1, inplace=True)
            final.drop('cum.pred', axis=1, inplace=True)

            impact = dollar(dollar(py_out,"summary"),"AbsEffect")[1]

            # Turn into json
            ts_results = final.to_json(orient='records')
            ret_results = {"ts_results":json.loads(ts_results),"total_impact":impact}
            with open('data/' + datetime.datetime.now().isoformat().replace(':','_'),'w') as out:
                out.write(json.dumps(ret_results,indent=2))
            return ret_results
        
        except RRuntimeError as e:
            return {"message":str(e)}

        except Exception as e:
            logger.error(e)
            raise e

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

