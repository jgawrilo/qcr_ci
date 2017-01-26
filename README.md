# qcr_ci
Casual Impact Integration
```bash
git clone https://github.com/jgawrilo/qcr_ci.git
cd qcr_ci

# You must edit the config.json file.  You must have access to an ES which this container can pull data from.

docker build -t qcr-causal-impact .
docker run -p 5001:5001 qcr-causal-impact

# Can test with...
./test_api.sh

# this uses a target pouplation as tweets with benghazi hashtag and the full campaign as the control
# the desired metric is emotion - specifically with the sadness band, so output is the casual impact of some event
# on the sadness in bengnazi tagged tweets.

# this will run a simple causal impact test and display the output returned..see test_output.txt for details.

# 
```
