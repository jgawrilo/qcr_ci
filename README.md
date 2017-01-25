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

# this will run a simple causal impact test and display the output returned
```
