FROM frolvlad/alpine-miniconda3
LABEL maintainer="David Sere <dave@d53dev.net>"

ENV csaopt_dir /opt/csaopt-worker

WORKDIR ${csaopt_dir}

ADD . ${csaopt_dir}

RUN conda env create -q && rm -rf /opt/conda/pkgs/*

ENV PATH /opt/conda/envs/csaopt-worker/bin:$PATH

CMD dramatiq --processes 1 --threads 3 broker:broker worker.tasks.actors