//
// Created by dotdi on 20.11.16.
//

#include "OptRunner.h"


void CSAOpt::OptRunner::simulated_annealing(size_t rounds, size_t nThreads, Target *results, curandState *states,
                                            Optimization::RandomDistr distribution) {
    int id = threadIdx.x;

    OptimizationImpl opt;

    printf("Thread %d started.\n", id);

    double (*rand_func)(curandStateXORWOW_t *state);

    switch(distribution){
        case Optimization::normal:
            rand_func = &curand_normal_double;
            break;
        case Optimization::uniform:
        default:
            rand_func = &curand_uniform_double;
            break;
    }

    printf("Rand_func initialized\n");

    double rands[RAND_SIZE];
    for (int i = 0; i < RAND_SIZE; ++i) {
        rands[i] = rand_func(&states[id]);
    }

    printf("%d rands generated\n", RAND_SIZE);

    //Target &state, double *rands
    auto target = results[id];
    auto cur_state = opt.initialize(target, rands);

    printf("Cur state calculated\n");
    auto state_best = cur_state;
    auto energy_old = opt.evaluate(cur_state);
    auto energy_best = energy_old;
    double temp = opt.cool(rounds); // TODO: return type should be configurable here

    printf("Initial state initialized e=%f\n", energy_best);

    for(size_t round = rounds; temp >= 0.0 && --round >= 0;){

        for (int k = 0; k < RAND_SIZE; ++k) {
            rands[k] = rand_func(&states[id]);
        }

        auto state_new = opt.generateNext(cur_state, rands);
        auto energy_new = opt.evaluate(state_new);

        if(energy_new < energy_best){
            state_best =   state_new ;
            energy_best =  energy_new ;
            state_best.energy = energy_new;
        }

        temp = opt.temp_func(round);

        if( energy_new < energy_old || exp( (energy_old - energy_new) / temp ) > curand_uniform(&states[id]) ){
            printf("New step to state with e=%f at temp %f\n", energy_new, temp);
            cur_state = state_new;
            energy_old = energy_new;
        }
    }
    results[id] = state_best;
}

__global__
void CSAOpt::OptRunner::setup_kernel(curandState *state, unsigned long seed) {
    int id = threadIdx.x;
    curand_init( seed, id, 0, &state[id]);
}

void CSAOpt::OptRunner::run_simulated_annealing() {
    size_t nThreads = 10;

    Target* targets;
    checkCudaErrors(cudaMallocManaged(&targets, sizeof(Target)*nThreads));

    for(size_t i=0; i<nThreads; ++i){
        Target t;
        for(size_t k=0; k<RAND_SIZE; ++k){
            t.coords[k] = 0.1*k;
        }
        targets[i] = t;
    }

    curandState* devStates;
    checkCudaErrors(cudaMallocManaged(&devStates, sizeof(curandState)*nThreads));

    printf("Running cuRand setup_kernel... ");

    setup_kernel<<<1, nThreads>>>(devStates, time(NULL));

    printf("\t\tdone.\n");
    printf("Running simulated annealing... \n");
    //Optimization *opt, size_t rounds, size_t nThreads, Target *result, Optimization::RandomDistr distr

    simulated_annealing<<<1, nThreads>>>(10000, nThreads, targets, devStates, Optimization::uniform);


    cudaDeviceSynchronize();
    print_arr(targets, nThreads, "results");

    checkCudaErrors(cudaFree(devStates));
    return (0);
}