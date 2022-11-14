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
