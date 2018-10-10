FROM frolvlad/alpine-miniconda3
LABEL maintainer="David Sere <dave@d53dev.net>"

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

ENV csaopt_dir /opt/csaopt-worker

# Numba will be unable to pick up the cuda library
# as it only check /usr/lib. Setting this helps.
ENV LD_LIBRARY_PATH /usr/lib64/

WORKDIR ${csaopt_dir}

ADD . ${csaopt_dir}

RUN conda env create -q && rm -rf /opt/conda/pkgs/*

ENV PATH /opt/conda/envs/csaopt-worker/bin:$PATH

CMD dramatiq --processes 1 --threads 3 broker:broker worker.tasks.actors