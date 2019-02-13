FROM rpy2/rpy2:2.8.x

MAINTAINER Justin Gawrilow 

USER root

RUN apt-get update && apt-get install -y libssl-dev libcurl4-openssl-dev

RUN R -e 'install.packages("devtools", repos="http://cran.cnr.Berkeley.edu")'
RUN R -e 'install.packages("Boom", repos="http://cran.cnr.Berkeley.edu")'
RUN R -e 'install.packages("BoomSpikeSlab", repos="http://cran.cnr.Berkeley.edu")'
RUN R -e 'devtools::install_github("google/CausalImpact")'

RUN apt-get install python3-pandas -y

RUN pip3 install --upgrade pip

ADD . /src

RUN pip3 install -r /src/requirements.txt

WORKDIR /src

EXPOSE 5001

RUN chmod -x /src/launch.sh

CMD sh /src/launch.sh


