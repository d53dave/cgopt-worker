//
// Created by dotdi on 20.11.16.
//

#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <cmath>
#include <math.h>
#include <random>
#include <utility>
#include <algorithm>
#include <curand_kernel.h>
#include <string>
#include "Optimization_impl.h"
#include "Target.h"

#define checkCudaErrors(val) check( (val), #val, __FILE__, __LINE__)

template<typename T>
void check(T err, const char* const func, const char* const file, const int line) {
  if (err != cudaSuccess) {
    std::cerr << "CUDA error at: " << file << ":" << line << " => ";
    std::cerr << cudaGetErrorString(err) << " " << func;
    std::cerr << std::endl; //fixes eclipse complaining
    exit(1);
  }
};



namespace CSAOpt {
    class OptRunner {
    public:
        void run_simulated_annealing();
    private:
        __global__ void simulated_annealing(size_t rounds,
            size_t nThreads,
            Target *results,
            curandState* states,
            Optimization::RandomDistr distribution);

        __global__ void setup_kernel( curandState * state, unsigned long seed );
    };
}

