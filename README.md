# CSAOpt Worker
[![Build Status](https://travis-ci.org/d53dave/csaopt-worker.svg?branch=master)](https://travis-ci.org/d53dave/csaopt-worker)
[![Coverage Status](https://coveralls.io/repos/github/d53dave/csaopt-worker/badge.svg?branch=master)](https://coveralls.io/github/d53dave/csaopt-worker?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/e97f8c54e6e35787041f/maintainability)](https://codeclimate.com/github/d53dave/csaopt-worker/maintainability)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker?ref=badge_shield)

This project provides the code for CSAOpt worker nodes. This is deployed on
target instances via Docker images. Workers pull work from the broker, compile
models, run optimizations on GPU hardware and and post results back to the broker.
Initially written in C++11 (for CUDA) this project now uses
[numba](http://numba.pydata.org), which provides JIT compilation of a subset
of python (called nopython) into CUDA kernels directly via PTX assembly.

## Host Requirements

Machine hosting the worker containers need to run docker (duh!) and are
subject to following requirements
(mainly dictated by [nvidia-docker2](https://github.com/NVIDIA/nvidia-docker)):

- GNU/Linux x86_64 with kernel version > 3.10
- Docker >= 1.12
- NVIDIA GPU with Architecture > Fermi (2.1)
- NVIDIA drivers ~= 361.93 (untested on older versions)

However, if you are looking at this repository, chances are you might be interested
in debugging worker code or your own models. If that is the case, you will be glad
to hear that the debug-enabled version (via the usual optimization config, refer to
the CSAOpt documentation) will run without `nvidia-docker`, as the worker will use
Numba's GPU simulator, running the worker code solely on CPU (and thusly, much much
slower).

## Compilation of Optimization Models

The models (i.e. model specific implementation of the Simulated Annealing
routines) are serialized on the application master and transmitted to the
workers. Workers use a rudimentary file template to generate the actual optimization
code at runtime. This code is then loaded and JIT-ed by numba, which then runs
the optimization kernels on the GPU hardware.

## CUDA

The workers run on hardware that has Nvidia GPUs available and uses CUDA
to run the parallelized optimization algorithm. To minimize the platform
dependency, the host machines need not provide any CUDA specific packages,
since the worker Docker image already provides all CUDA requirements.
Only the GPU driver is required on the host.

## Development

This is not intended to be built by hand as it will be deployed
automatically to the target machines using docker. That being said, manual
building should still be relatively straightforward. Dependencies are managed by
`conda` and are listed in the `environment.yml`. To create an environemnt with
all required dependencies, from the project root execute:

```bash
# Create environement and resolve/install all dependencies listed in environment.yml
conda env create

# after downloading all deps (might take a while)
source activate csaopt-worker

# Then, in the activated environment
dramatiq --processes 1 --threads 3 broker:broker worker.tasks.actors
```

This will start the broker client that accepts model deployments and optimization jobs.
Note that running this without `docker` and `nvidia-docker` requires an installed CUDA
toolkit in addition to the required Nvidia graphics drivers.

Kernels can even be executed manually, even without GPU hardware, using the debugging
infrastructure of `Numba`. This works by setting the `NUMBA_ENABLE_CUDASIM` env
variable to 1. This switches numba to the CUDA simulator mode, which is run on
the CPU and can be inspected for debugging. Refer to
[the documentation](https://numba.pydata.org/doc.html) for further details.

You can also have a look at the [test suite](tests/).

## License

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker?ref=badge_large)
