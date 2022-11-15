import dis

def disassemble(code: list[dis.Instruction]):
    instructions = list(dis.get_instructions(code))
    for idx, op in enumerate(instructions):
        if op.is_jump_target:
            for op2 in instructions:
                # use argval because it is absolute
                if (op2.opcode in dis.hasjrel or op2.opcode in dis.hasjabs) and op2.argval // 2 == idx:
                    op2.target = op
    return instructions

def compute_stack_effect(segment: list[dis.Instruction], retmax=False): # returns stack_effect and max stack value
    SE = 0
    idx = 0
    effects = []
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
    if retmax:
        return max(effects)
    return SE

def reassemble(func, segment: list[dis.Instruction]):
    consts = func.__code__.co_consts
    names = func.__code__.co_names
    varnames = func.__code__.co_varnames
    co_code = b''
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
        co_code=co_code,
        co_consts=consts,
        co_names=names,
        co_varnames=varnames,
        co_nlocals=len(varnames),
        co_stacksize=compute_stack_effect(segment, retmax=True),
    )
    return func
