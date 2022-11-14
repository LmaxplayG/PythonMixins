"""
Mixit

A mixin library for Python

Authors:
Lmaxplay (Discord ID: 941433256010727484, GitHub: LmaxplayG)
chilaxan (Discord ID: 274715613115711488) # Add ur own github here (if u want)
"""
import dis
import opcode
import inspect


def disassemble(func: callable):
    """Disassembles a function into a list of opcodes"""
    instructions = list(dis.get_instructions(func))
    for idx, op in enumerate(instructions):
        if op.is_jump_target:
            for op2 in instructions:
                # use argval because it is absolute
                if (op2.opcode in dis.hasjrel or op2.opcode in dis.hasjabs) and op2.argval // 2 == idx:
                    op2.target = op
    return instructions


def compute_stack_effect(segment: list[dis.Instruction]):
    """Compute the stack effect of a function"""
    effects = []
    SE = 0 # Stack Effect
    idx = 0
    while idx < len(segment):
        op = segment[idx]
        isjump = op.opcode in dis.hasjrel or op.opcode in dis.hasjabs
        SE += dis.stack_effect(
            op.opcode,
            op.arg if op.opcode > dis.HAVE_ARGUMENT else None,
            jump = isjump
        )
        if isjump:
            idx = segment.index(op.target)
        else:
            idx += 1
        effects.append(SE)
    return SE, max(effects)
    

def reassemble(func: callable, segment: list[dis.Instruction]):
    """Reassembles a function from a list of opcodes"""
    consts = func.__code__.co_consts
    names = func.__code__.co_names
    varnames = func.__code__.co_varnames
    co_code = b""

    for idx, op in enumerate(segment):
        if op.opcode in dis.hasjrel:
            target = segment.index(op.target)
            arg = target - idx - 1 # -1 is needed here
            co_code += bytes([op.opcode, arg])
        elif op.opcode in dis.hasjabs:
            target = segment.index(op.target)
            co_code += bytes([op.opcode, target])
        elif op.opcode in dis.hasconst:
            const = op.argval
            if const in consts:
                arg = consts.index(const)
            else:
                arg = len(consts)
                consts += (const,)
            co_code += bytes([op.opcode, arg])
        elif op.opcode in dis.haslocal:
            varname = op.argval
            if varname in varnames:
                arg = varnames.index(varname)
            else:
                arg = len(varnames)
                varnames += (varname,)
            co_code += bytes([op.opcode, arg])
        elif op.opcode in dis.hasname:
            name = op.argval
            if name in names:
                arg = names.index(name)
            else:
                arg = len(names)
                names += (name,)
            co_code += bytes([op.opcode, arg])
        else:
            co_code += bytes([op.opcode, op.arg if op.arg else 0])
    func.__code__ = func.__code__.replace(
        co_code = co_code,
        co_consts = consts,
        co_names = names,
        co_varnames = varnames,
        co_nlocals = len(varnames),
        co_stacksize = compute_stack_effect(segment)[1]
    )
    return func

class At:
    """
    Represents a location in a function to inject code at. (e.g. At('return'))
    """
    def __init__(self, value, arg = None, op = None, offset = 0):
        self.value = value
        self.arg = arg
        self.op = op
        self.offset = offset

# After class, literally here to aid with highlighting
class After:
    pass

After = lambda value, arg = None, offset = 0: At(value, arg, offset + 1)

def inject_at_instruction(opname: str, at: At, target_instructions: list[dis.Instruction], instructions: list[dis.Instruction]):
    """Inject a mixin at a specific instruction"""
    idxs = sorted([
        idx for idx, op in enumerate(target_instructions) if op.opname == opname
    ])
    if at.arg is not None:
        i = idxs[at.arg] + at.offset
        target_instructions[i:i] = instructions
    else:
        for i in reversed(idxs):
            i += at.offset
            target_instructions[i:i] = instructions

def inject_at_match(at: At, match_instructions: list[dis.Instruction], target_instructions: list[dis.Instruction], instructions: list[dis.Instruction]):
    """Inject a mixin at a specific instruction"""
    match_seq = [[op.opname for op in match_instructions]]
    target_seq = [[op.opname for op in target_instructions]]

    idxs = []

    offset = 0
    while (offset + len(match_seq)) <= len(target_seq):
        if target_seq[offset:offset + len(match_seq)] == match_seq:
            idxs.append(offset)
        offset += 1
    if at.arg is not None:
        i = idxs[at.arg] + at.offset
        target_instructions[i:i] = instructions
    else:
        for i in reversed(idxs):
            i += at.offset
            target_instructions[i:i] = instructions


class Mixin:
    """
    Represents a mixin to be injected into a function at a specific location.

    Note:
    - Mixins use the local and global scope of the function they are injected into.
    - Variables can be added as arguments of the function (makes intellisense happy)
    """
    def __init__(self, target, at: At, force_ret = False):
        self.target = target
        self.at = at
        self.force_ret = force_ret
    
    def __call__(self, inject):
        instructions = disassemble(inject)
        should_ret = instructions[-2].argval is not None or self.force_ret
        if not should_ret:
            instructions = instructions[:-2]

        target_instructions = disassemble(self.target)
        if self.at.value == 'head':
            i = self.at.offset
            target_instructions[i:i] = instructions
        elif self.at.value == 'return':
            inject_at_instruction('RETURN_VALUE', self.at, target_instructions, instructions)
        elif self.at.value == 'opcode':
            inject_at_instruction(self.at.op, self.at, target_instructions, instructions)
        elif self.at.value == 'match':
            inject_at_match(self.at, disassemble(self.at.f)[:-2], target_instructions, instructions)
        
        reassemble(self.target, target_instructions)
        return inject