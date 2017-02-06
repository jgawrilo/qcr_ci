# qcr_ci
Casual Impact Integration

This project essentially wraps the Google Causal Imnpact package (https://google.github.io/CausalImpact/CausalImpact.html).

```bash
# Get the repo...
git clone https://github.com/jgawrilo/qcr_ci.git

# Go into the dir...
cd qcr_ci

# You must edit the config.json file to change the docker service port

# Build the container
docker build -t qcr-causal-impact .

# Run the container.  Service will be running on http://localhost:5001/api/impact
docker run -p 5001:5001 qcr-causal-impact

# Can test with the following.
# this uses the test_input.json as input

python test_service.py

# this will run a simple causal impact test and display the output returned..see test_output.json for details.

# 
```
So input is...

![alt text](https://github.com/jgawrilo/qcr_ci/blob/master/imgs/Sadness_Time_Series.png "Sadness inputs")

Output is...
```
{
  "total_impact": 3700.23134190327, 
  "ts_results": [
    {
      "cum.effect.upper": 0.0, 
      "control": 4035, 
      "point.effect": -3.908289, 
      "point.effect.upper": 867.586, 
      "target": 141, 
      "cum.pred.upper": 141.0, 
      "point.effect.lower": -904.61133, 
      "point.pred.lower": -726.58602, 
      "date": 1468281600, 
      "cum.effect.lower": 0.0, 
      "cum.pred": 141.0, 
      "point.pred.upper": 1045.6113, 
      "cum.response": 141, 
      "cum.effect": 0.0, 
      "point.pred": 144.90829, 
      "response": 141, 
      "cum.pred.lower": 141.0
    }, 
    {
      "cum.effect.upper": 0.0, 
      "control": 2860, 
      "point.effect": -58.197883, 
      "point.effect.upper": 926.1226, 
      "target": 52, 
      "cum.pred.upper": 193.0, 
      "point.effect.lower": -985.821982, 
      "point.pred.lower": -874.12263, 
      "date": 1468368000, 
      "cum.effect.lower": 0.0, 
      "cum.pred": 193.0, 
      "point.pred.upper": 1037.822, 
      "cum.response": 193, 
      "cum.effect": 0.0, 
      "point.pred": 110.19788, 
      "response": 52, 
      "cum.pred.lower": 193.0
    }, 
    ....
    ....
    ....
```

![alt text](https://github.com/jgawrilo/qcr_ci/blob/master/image_outputs/sadness.png "Sadness plotted with CI")
