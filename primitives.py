from llvmlite import ir

char = ir.IntType(8)
char_p = char.as_pointer()
null = char(0)


def charstring(string: str, builder: ir.IRBuilder):
    string_p = builder.alloca(char_p)
    string_t = ir.ArrayType(char, len(string)+1)
    memory_p = builder.alloca(string_t)
    chars = string_t([*map(char, string.encode()), null])
    builder.store(chars, memory_p)
    memory_p = builder.bitcast(memory_p, char_p)
    builder.store(memory_p, string_p)
    return builder.load(string_p)


def allocate(pointee: ir.Type, builder: ir.IRBuilder, name=''):
    # shitty trick with pointers for avoid llvmlite's GEP strange behaviour
    pointer = builder.alloca(pointee)
    pointer_p = builder.alloca(pointee.as_pointer())
    builder.store(pointer, pointer_p)
    pointer = builder.load(pointer_p, name=name)
    return pointer


def nullptr(type: ir.Type, builder: ir.IRBuilder):
    return builder.bitcast(null, type.as_pointer())
