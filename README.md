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

![alt text](https://github.com/jgawrilo/qcr_ci/blob/master/image_outputs/sadness.png "Sadness plotted with CI")
