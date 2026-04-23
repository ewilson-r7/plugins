FROM rapid7/insightconnect-python-3-slim-plugin:6

ADD ./plugin.spec.yaml /plugin.spec.yaml
ADD . /python/src
WORKDIR /python/src

RUN python -m pip install --upgrade pip setuptools wheel
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
RUN python setup.py build && python setup.py install