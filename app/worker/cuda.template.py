import numpy
import array
import math

from numba import cuda, $precision
from numba.cuda.random import $random_gen_type$precision

@cuda.jit(device=True)
$initialize

@cuda.jit(device=True)
$cool

@cuda.jit(device=True)
$generate_next

@cuda.jit(device=True)
$evaluate

@cuda.jit(device=True)
$acceptance_func

@cuda.jit
def simulated_annealing(max_steps, initial_temp, dimensionality, rands, states):
    thread_id = cuda.grid(1)
    step = 0
    rand_gen_idx = 0
    random_values = cuda.local.array($dim, dtype=$precision)
    while(rand_gen_idx < $dim):
        random_values[rand_gen_idx] = $random_gen_type$precision(rands, thread_id)
        rand_gen_idx += 1
    rand_gen_idx = 0

    state = initialize(states[thread_id], random_values)
    energy = evaluate(state)
    temperature = initial_temp
    while(step < max_steps):
        # Generate Rands
        while(rand_gen_idx < $dim):
            random_values[rand_gen_idx] = $random_gen_type$precision(rands, thread_id)
            rand_gen_idx += 1
        rand_gen_idx = 0

        temperature = cool(temperature)
        new_state = generate_next(state, random_values)
        new_energy = evaluate(new_state)
        if acceptance_func(energy, new_energy, temperature):
            state = new_state
            energy = new_energy
        step += 1

    states[thread_id] = state
