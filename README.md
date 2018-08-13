# CSAOpt Worker
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker?ref=badge_shield)
[![Maintainability](https://api.codeclimate.com/v1/badges/e97f8c54e6e35787041f/maintainability)](https://codeclimate.com/github/d53dave/csaopt-worker/maintainability)

This project provides the code for CSAOpt worker nodes. This is deployed on the
target instances via Docker images. Workers pull work from Kafka, compile the
models, run optimizations on GPU hardware and and post results back to Kafka.
Initially based on C++11 (for CUDA) this project now uses
[numba](http://numba.pydata.org), which provides JIT compilation of a subset
of python (called nopython) into CUDA kernels (directly via PTX assembly).

## Host Requirements

Machine hosting the worker containers need to run docker (duh!) and are
subject to following requirements
(mainly dictated by [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)):

- GNU/Linux x86_64 with kernel version > 3.10
- Docker >= 1.9 (official docker-engine, docker-ce or docker-ee only)
- NVIDIA GPU with Architecture > Fermi (2.1)
- NVIDIA drivers >= 340.29 with binary nvidia-modprobe

## Compilation of Optimization Models

The models (i.e. model specific implementation of the Simulated Annealing
routines) are serialized on the application master and transmitted to the
workers. Workers use rudimentary templates to generate the actual optimization
code at runtime. This code is then loaded and JIT-ed by numba, which then runs
the optimization kernels on the GPU hardware.

## CUDA

The workers run on hardware that has Nvidia GPUs available and uses CUDA
to run the parallelized optimization algorithm. To minimize the platform
dependency, the host machines need not provide any CUDA specific packages,
since the Docker image already provides all CUDA requirements. Only the GPU
driver is required on the host.

## Development

This is not intended to be built by hand as it will be deployed
automatically to the target machines using docker. That being said, manual
building should still be relatively straightforward. Dependencies are managed by
`conda` and are listed in the `environment.yml`. To create an environemnt with
all required dependencies, from the project root execute:

```bash
conda env create # this will use the environment.yml

# after downloading all deps (might take a while)
source activate csaopt-worker

# Then, in the virtualenv
./worker --kafka <kafka_host1:port,...> --topics <topic1,> --group <group> [--multi-gpu]
```

Kernels can be executed by hand, even without GPU hardware, using the debugging
infrastructure of `numba`. This works by setting the `NUMBA_ENABLE_CUDASIM` env
variable to 1. This switches numba to the cuda simulator mode, which is run on
the CPU and can be inspected for debugging. Refer to
[the documentation](https://numba.pydata.org/doc.html) for further details.

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker?ref=badge_large)
