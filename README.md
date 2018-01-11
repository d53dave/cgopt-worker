# CSAOpt Worker
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker?ref=badge_shield)


This project provides the worker code for CSAOpt.
This is deployed on the target instances via Docker images.
Workers pull work from the message queue, run optimizations
on the GPU hardware and and posts results back to the queue.

## Host Requirements

Machine hosting the worker containers need to run docker (duh!) and are
subject to following requirements
(mainly dictated by [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)):
- GNU/Linux x86_64 with kernel version > 3.10
- Docker >= 1.9 (official docker-engine, docker-ce or docker-ee only)
- NVIDIA GPU with Architecture > Fermi (2.1)
- NVIDIA drivers >= 340.29 with binary nvidia-modprobe

## CUDA

The workers run on hardware that has Nvidia GPUs available and uses CUDA
to run the parallelized optimization algorithms. To minimize the platform
dependency, the host machines need not provide any CUDA specific packages, 
since the Docker image already provides all CUDA requirements.
Only an NVidia driver is required on the host.

## Development

This is not intended to be built by hand as it will be deployed
automatically to the target machines using docker. That being said, manual building
should still be relatively straightforward. Dependencies are managed by `conda`
and are listed in the `environment.yml`.


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fd53dave%2Fcsaopt-worker?ref=badge_large)