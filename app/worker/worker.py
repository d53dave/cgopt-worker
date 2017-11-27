


# TODO: add this to the model documentation
# Numba(like cuRAND) uses the Box - Muller transform 
# <https://en.wikipedia.org/wiki/Box%E2%80%93Muller_transform> to generate 
# normally distributed random numbers from a uniform generator. However, 
# Box - Muller generates pairs of random numbers, and the current implementation
# only returns one of them. As a result, generating normally distributed values
# is half the speed of uniformly distributed values.

class Worker():
    def __init__():
        pass