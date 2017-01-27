# qcr_ci
Casual Impact Integration
```bash
# Get the repo...
git clone https://github.com/jgawrilo/qcr_ci.git

# Go into the dir...
cd qcr_ci

# You must edit the config.json file to change the ES instance  You must have access to an ES which this container can pull data from.
# Default uses the dev ES instance, index and, service port

# Build the container
docker build -t qcr-causal-impact .

# Run the container.  Service will be running on http://localhost:5001/api/impact
docker run -p 5001:5001 qcr-causal-impact

# Can test with the following.
# this uses a target pouplation as tweets with benghazi hashtag and the full campaign as the control
# the desired metric is emotion - specifically with the sadness band, so output is the casual impact of some event
# on the sadness in bengnazi tagged tweets.

./test_api.sh

# this will run a simple causal impact test and display the output returned..see test_output.txt for details.

# 
```
```
Output will be

{"total_impact": "302.919285529977", # cumulative impact at the end of the post period
"ts_results": {"2016-10-03": # time period for results
{"response": "2", # Actual response - solid line in original
"point.effect.lower": -21.6999,  # Point-wise impact  - lower bound - lower blue line in pointwise
"cum.response": 114.0, # Can ignore
"cum.pred.lower": 114.0, # Can ignore
"cum.effect": 0.0, # Cumulative Point-wise impact  - dotted line in cumulative
"point.pred": 7.749572, # Predicted response - dotted line in original
"cum.pred": 114.0, # Can ignore
"cum.effect.upper": 0.0, # Cumulative Point-wise impact  - upper bound - upper blue line in cumulative
"cum.effect.lower": 0.0, # Cumulative Point-wise impact  - lower bound - lower blue line in cumulative
"point.pred.lower": -9.305632, # Predicted reponse - upper bound - blue upper region in original
"point.pred.upper": 23.6999, # Predicted reponse - lower bound - lower upper region in original
"point.effect.upper": 11.305632, # Point-wise impact  - upper bound - upper blue line in pointwise
"point.effect": -5.74957167, # Point-wise impact  - dotted line in pointwise
"cum.pred.upper": 114.0},# Can ignore
{"2016-10-04":{...
```

![alt text](https://github.com/jgawrilo/qcr_ci/blob/master/image_outputs/sadness.png "Sadness plotted with CI")
