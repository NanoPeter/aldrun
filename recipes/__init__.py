from .recipe import REGISTRY

from importlib import import_module
import os
paths = [x for x in os.listdir('./recipes') if x.endswith('py') and x != '__init__.py' and x != 'recipe.py']

for path in paths:
    print('importing recipes.{}'.format(path[:-3]))
    import_module('recipes.{}'.format(path[:-3]))