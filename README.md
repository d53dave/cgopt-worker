# CSAOpt Worker

This project provides the worker code for CSAOpt.
This is deployed on the target instances via Docker images, pull work
from the message queue, run optimizations on the GPU hardware and
and posts results back to the queue.

## Host Requirements

Machine hosting the worker containers need to run docker (duh!) and are subject to following requirements (mainly dictated by [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)):
- GNU/Linux x86_64 with kernel version > 3.10
- Docker >= 1.9 (official docker-engine, docker-ce or docker-ee only)
- NVIDIA GPU with Architecture > Fermi (2.1)
- NVIDIA drivers >= 340.29 with binary nvidia-modprobe

## CUDA

The workers run on hardware that has Nvidia GPUs available and uses CUDA
to run the parallelized optimization algorithms. To minimize the platform
dependency, the host machines need not provide any CUDA specific packages, since the Docker images already provide all CUDA requirements.
Only an NVidia driver is required on the host.

## Building

This is not intended to be built by hand as it will be deployed
automatically to the target machines. That being said, manual building
should still be relatively straightforward. Dependencies are:

- CMake >= 3.2
- GCC >= 4.9
- ZMQ and ZMQPP >=4
- CUDA Toolkit >= 6.0 with appropriate NVidia driver.

The libzmqpp-dev package in ubuntu 16.04 is still v3, which will not work.
The docker image actually built zmq-pp from source.

After fulfilling the dependencies, the build should be a simple
`cmake . && make`

Note that building the `csaopt-tidings` target (see [csaopt-tidings](https://github.com/d53dave/csaopt-tidings)) generates required headers for the actual build. CMake makes sure this is run beforehand, but it might be handy for development (i.e. let the IDE resolve the capnp generated headers).
