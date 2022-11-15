from .utils import *
from .locations import *

class Mixin:
    def __init__(self, target, at: Location, force_ret=False, globals={}):
        self.target = target
        self.at = at
        self.force_ret=force_ret
        for key, value in globals.items():
            self.target.__globals__[key] = value

    def __call__(self, inject):
        instructions = disassemble(inject)
        should_ret = instructions[-2].argval is not None or self.force_ret
        if not should_ret:
            instructions = instructions[:-2]

        target_instructions = disassemble(self.target)
        self.at.handle(target_instructions, instructions)
        reassemble(self.target, target_instructions)
        return inject
