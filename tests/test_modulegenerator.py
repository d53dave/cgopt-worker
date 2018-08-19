import sys

from context import ModuleGenerator, test_model_dict
from pyhocon import ConfigFactory


internal_config = ConfigFactory.parse_file('worker/internal/internal.conf')


def test_compile():
    gen = ModuleGenerator(internal_config['cuda'])

    module_conf = ModuleGenerator.extract_opt_configuration(test_model_dict)
    module = gen.cuda_module(module_conf)

    assert hasattr(module, 'initialize')
    assert hasattr(module, 'cool')
    assert hasattr(module, 'evaluate')
    assert hasattr(module, 'acceptance_func')
    assert hasattr(module, 'empty_state')

    # pylint: disable=E1101
    assert module.empty_state() == (0.0, 0.0)  # type: ignore
    assert module.m == 5
    assert module.c == (1, 2, 5, 2, 3)
    assert module.A == ((3, 5), (5, 2), (2, 1), (1, 4), (7, 9))

    assert 'csaopt_cuda_opt' in sys.modules
