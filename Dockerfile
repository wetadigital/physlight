# Copyright © 2020, Weta Digital, Ltd.
# SPDX-License-Identifier: Apache-2.0
FROM python:3.7

WORKDIR /tmp
COPY ./requirements.txt /tmp
RUN pip install -r requirements.txt \
    && rm /tmp/requirements.txt \
    && python -c "import imageio;imageio.plugins.freeimage.download()"

RUN mkdir -p /home/weta-digital/physlight
WORKDIR /home/weta-digital/physlight

CMD sh -c 'cd /home/weta-digital/physlight && jupyter notebook --allow-root --ip=0.0.0.0 --port=8888'
