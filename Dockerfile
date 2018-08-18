FROM frolvlad/alpine-miniconda3
LABEL maintainer="David Sere <dave@d53dev.net>"

ENV csaopt_dir /opt/csaopt-worker


RUN apk update && apk add git


RUN git clone https://github.com/d53dave/csaopt-worker.git $csaopt_dir
RUN apk del git

WORKDIR ${csaopt_dir}

RUN conda env create -q && rm -rf /opt/conda/pkgs/*
# RUN echo "source activate csaopt-worker" > ~/.bashrc
# SHELL ["/bin/bash", "-c"]
ENV PATH /opt/conda/envs/csaopt-worker/bin:$PATH


# ENTRYPOINT ["/bin/bash -c dramatiq --processes 1 --threads 3 broker:broker worker.tasks.actors"]
CMD dramatiq --processes 1 --threads 3 broker:broker worker.tasks.actors