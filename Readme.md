# Mixit

A mixin library for python

## Usage

```python
from mixit import Mixin, At

from somewhere import somefunc

@Mixin(target=somefunc, at=At('head'))
def somefunc_mixin():
    print('mixin')

# From now on, when somefunc is called, it will print 'mixin' first
```

## Compatibility

Mixit is tested with python 3.10, python 3.11 is not supported yet.
Please use python 3.10 for now.
