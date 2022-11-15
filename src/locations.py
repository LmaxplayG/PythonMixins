from .utils import disassemble

class Location:
    def __init__(self, arg=None, ordinal=None, offset=0):
        self.arg = arg
        self.ordinal = ordinal
        self.offset = offset

    def __or__(self, other):
        return LocationUnion(self, other)

    @classmethod
    def after(cls, *args, **kwargs):
        self = cls(*args, **kwargs)
        self.offset += 1
        return self

    def handle(self, target, inject):
        for idx in sorted(set(self.matches(target)), reverse=True):
            target[idx:idx] = inject

class LocationUnion(Location):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def handle(self, target, inject):
        yield from self.a.matches(target)
        yield from self.b.matches(target)

class Head(Location):
    def matches(self, target):
        yield 0 + self.offset

class Opcode(Location):
    def matches(self, target):
        idxs = sorted([
            idx + self.offset for idx, op in enumerate(target) if op.opname == self.arg
        ], reverse=True)
        if self.ordinal is not None:
            yield idxs[self.ordinal]
        else:
            yield from idxs

class Return(Opcode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arg = 'RETURN_VALUE'

class Call(Opcode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arg = 'CALL_FUNCTION'

class Match(Location):
    def __init__(self, *args, **kwargs):
        """
        Match certain instructions in a function.
        """
        super().__init__(*args, **kwargs)
        self.arg = disassemble(self.arg)[:-1]

    @classmethod
    def manual(cls, ops, **kwargs):
        self = cls(lambda:0, **kwargs)
        self.arg = ops
        return self

    @classmethod
    def after(cls, *args, **kwargs):
        """
        Match after the matches instead of before.
        """
        self = cls(*args, **kwargs)
        self.offset = len(self.arg)
        return self

    def matches(self, target):
        target_s = [[op.opcode, op.argval] for op in target]
        match_s = [[op.opcode, op.argval] for op in self.arg]
        idxs = []
        offset = 0
        while (offset + len(match_s)) <= len(target):
            if target_s[offset:offset + len(self.arg)] == match_s:
                idxs.append(offset + self.offset)
            offset += 1
        if self.ordinal is not None:
            yield idxs[self.ordinal]
        else:
            yield from idxs

