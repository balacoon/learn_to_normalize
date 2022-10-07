# Copyright 2022 Balacoon

FROM python:3.8-slim

ARG build_fe
ARG user_id
ARG group_id

ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Berlin"

# get ubuntu essentials to build packages
RUN apt-get update
RUN apt-get install -y openssh-client git vim autoconf automake libtool m4 gfortran autoconf-archive build-essential wget cmake

RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

RUN echo "alias python=python3" > /root/.bash_aliases
RUN echo "export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH" >> /root/.bashrc
    
# download dependencies
RUN --mount=type=ssh cd /opt/ && \
    git clone -b 1.8.0 git@github.com:balacoon/openfst.git && \
    git clone -b 1.3.5 https://github.com/balacoon/thrax.git
RUN wget -O /opt/pynini-2.1.3.tar.gz \
    http://www.opengrm.org/twiki/pub/GRM/PyniniDownload/pynini-2.1.3.tar.gz

# build dependencies
# build and install OpenFST
RUN cd /opt/openfst && \
    ./configure --enable-python --enable-mpdt --enable-far --enable-pdt \
        --enable-shared --enable-ngram-fsts --enable-grm && \
    make -j $(nproc) && \
    make install

# build and install thrax
RUN cd /opt/thrax && \
    ./configure && \
    make -j $(nproc) && \
    make install

# install balacoon_text_normalization package,
# which utilizes normalization addons
RUN --mount=type=ssh if [ "$build_fe" = "true" ]; then \
    echo "Building balacoon_frontend from sources" && \
    cd /opt/ && \
    git clone git@github.com:balacoon/balacoon_frontend && \
    pip install ./balacoon_frontend ; \
else \
    echo "Installing balacoon_frontend from pip" && \
    pip install -i https://pypi.fury.io/balacoon/ balacoon-frontend ; fi

# install package dependencies and package itself
COPY ./ /opt/learn_to_normalize
RUN pip install -r /opt/learn_to_normalize/requirements.txt
# install pynini (not in pip)
RUN cd /opt && tar -zxvf pynini-2.1.3.tar.gz && rm pynini-2.1.3.tar.gz && \
    pip install ./pynini-2.1.3
RUN pip install /opt/learn_to_normalize

# create non-root user
RUN addgroup --gid $group_id user
RUN adduser --disabled-password --gecos '' --uid $user_id --gid $group_id user
USER user

# set unsual library path
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib/"

WORKDIR /home/
