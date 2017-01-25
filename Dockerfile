FROM sd2k/rpy2-causalimpact-test

RUN apt-get install python3-pandas -y

RUN pip3 install --upgrade pip

ADD . /src

RUN pip3 install -r /src/requirements.txt

WORKDIR /src

EXPOSE 5001

RUN chmod -x /src/launch.sh

CMD sh /src/launch.sh


