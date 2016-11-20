# CSAOpt Worker

This project provides the worker code for CSAOpt.
This is deployed on the target instances, pull work from the message queue
and posts results to it.

## CUDA
The workers run on hardware that has NVIDIA GPUs available and uses CUDA
to run parallelized optimization algorithms.

## Building
This is not intended to be built by hand as it will be deployed
automatically to the target machines. That being said, manual building
should still be relatively straightforward. Dependencies are:
- CMake >= 3.2
- GCC >= 4.9
- CUDA >= 7.5
- ZMQ and ZMQPP >=4

The libzmqpp-dev package in ubuntu 16.04 is still v3, which will not work.
The ansible deployment actually gets the zmqpp source from GitHub, builds
and installs it.

After fulfilling the dependencies, the build should be a simple
`cmake . && make csaopt-tidings csaopt_worker`

Note that building csaopt-tidings generates required headers for the actual build.


