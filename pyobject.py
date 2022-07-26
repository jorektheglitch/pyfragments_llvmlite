from llvmlite import ir

from llvm_operations import create_execution_engine, compile_ir
from primitives import allocate, charstring
from typedefs import TypeTable


int8 = ir.IntType(8)
int32 = ir.IntType(32)
int64 = ir.IntType(64)
char = ir.IntType(8)
char_p = char.as_pointer()
size = ir.IntType(1)
size_t = size.as_pointer()
ssize_t = size.as_pointer()
ssize_t_p = ssize_t.as_pointer()

void = ir.VoidType()
void_p = int8.as_pointer()

int32_0 = ir.Constant(int32, 0)

T_SHORT = int8(0)
T_INT = int8(1)
T_LONG = int8(2)
T_FLOAT = int8(3)
T_DOUBLE = int8(4)
T_STRING = int8(5)
T_OBJECT = int8(6)
# XXX the ordering here is weird for binary compatibility
T_CHAR = int8(7)   # 1-character string
T_BYTE = int8(8)   # 8-bit signed int
# unsigned variants:
T_UBYTE = int8(9)
T_USHORT = int8(10)
T_UINT = int8(11)
T_ULONG = int8(12)

# Added by Jack: strings contained in the structure
T_STRING_INPLACE = int8(13)

# Added by Lillo: bools contained in the structure (assumed char)
T_BOOL = int8(14)

T_OBJECT_EX = int8(16)  # Like T_OBJECT, but raises AttributeError when the value is NULL, instead of converting to None.
T_LONGLONG = int8(17)
T_ULONGLONG = int8(18)

T_PYSSIZET = int8(19)   # Py_ssize_t
T_NONE = int8(20)       # Value is always None


READONLY = int8(1)
READ_RESTRICTED = int8(2)
PY_WRITE_RESTRICTED = int8(4)
RESTRICTED = READ_RESTRICTED.or_(PY_WRITE_RESTRICTED)


PYTYPEOBJECT_FIELD_NAMES = (
    "ob_refcount",
    "ob_type",
    "ob_size",
    "tp_name",
    "tp_basicsize",
    "tp_itemsize",

    # Methods to implement standard operations
    "tp_dealloc",
    "tp_vectorcall_offset",
    "tp_getattr",
    "tp_setattr",
    "tp_as_async",
    "tp_repr",

    # Method suites for standard classes
    "tp_as_number",
    "tp_as_sequence",
    "tp_as_mapping",

    # More standard operations (here for binary compatibility)
    "tp_hash",
    "tp_call",
    "tp_str",
    "tp_getattro",
    "tp_setattro",

    # Functions to access object as input/output buffer
    "tp_as_buffer",

    "tp_flags",
    "tp_doc",
    "tp_traverse",
    "tp_clear",
    "tp_richcompare",
    "tp_weaklistoffset",

    "tp_iter",
    "tp_iternext",

    "tp_methods",
    "tp_members",
    "tp_getset",
    "tp_base",
    "tp_dict",
    "tp_descrget",
    "tp_descrset",
    "tp_dictoffset",
    "tp_init",
    "tp_alloc",
    "tp_new",
    "tp_free",  # /* Low-level free-memory routine */
    "tp_is_gc",  # /* For PyObject_IS_GC */
    "tp_bases",
    "tp_mro",  # /* method resolution order */
    "tp_cache",
    "tp_subclasses",
    "tp_weaklist",
    "tp_del",

    # /* Type attribute cache version tag. Added in version 2.6 */
    "tp_version_tag",

    "tp_finalize",
    "tp_vectorcall",
)


def define_pyobjects_system(module: ir.Module):

    pyobject = module.context.get_identified_type("PyObject")
    pyvarobject = module.context.get_identified_type("PyVarObject")
    pytypeobject = module.context.get_identified_type("PyTypeObject")
    pybuffer = module.context.get_identified_type("Py_buffer")

    pyobject_p = pyobject.as_pointer()
    pytypeobject_p = pytypeobject.as_pointer()

    types = TypeTable(pyobject, pytypeobject, pybuffer)

    ob_refcount = ssize_t
    ob_type = pytypeobject.as_pointer()
    pyobject.set_body(
        ob_refcount,
        ob_type
    )
    ob_size = size_t
    pyvarobject.set_body(
        ob_refcount,
        ob_type,
        ob_size
    )
    pybuffer.set_body(
        void_p,      # buf
        pyobject_p,  # obj       owned reference
        ssize_t,     # len
        ssize_t,     # itemsize  This is Py_ssize_t so it can be
                     #              pointed to by strides in simple case.
        int8,        # readonly
        int8,        # ndim
        char_p,      # format
        ssize_t_p,   # shape
        ssize_t_p,   # strides
        ssize_t_p,   # suboffsets
        void_p,      # internal
    )

    pyasyncmethods = module.context.get_identified_type("PyAsyncMethods")
    pyasyncmethods.set_body(
        types.unaryfunc_p,  # am_await
        types.unaryfunc_p,  # am_aiter
        types.unaryfunc_p,  # am_anext
        types.sendfunc_p,   # am_send
    )
    pyasyncmethods_p = pyasyncmethods.as_pointer()

    pynumbermethods = module.context.get_identified_type("PyNumberMethods")
    pynumbermethods.set_body(
        types.binaryfunc_p,   # nb_add
        types.binaryfunc_p,   # nb_subtract
        types.binaryfunc_p,   # nb_multiply
        types.binaryfunc_p,   # nb_remainder
        types.binaryfunc_p,   # nb_divmod
        types.ternaryfunc_p,  # nb_power
        types.unaryfunc_p,    # nb_negative
        types.unaryfunc_p,    # nb_positive
        types.unaryfunc_p,    # nb_absolute
        types.inquiry_p,      # nb_bool
        types.unaryfunc_p,    # nb_invert
        types.binaryfunc_p,   # nb_lshift
        types.binaryfunc_p,   # nb_rshift
        types.binaryfunc_p,   # nb_and
        types.binaryfunc_p,   # nb_xor
        types.binaryfunc_p,   # nb_or
        types.unaryfunc_p,    # nb_int

        void_p,       # nb_reserved  the slot formerly known as nb_long
        types.unaryfunc_p,    # nb_float

        types.binaryfunc_p,   # nb_inplace_add
        types.binaryfunc_p,   # nb_inplace_subtract
        types.binaryfunc_p,   # nb_inplace_multiply
        types.binaryfunc_p,   # nb_inplace_remainder
        types.ternaryfunc_p,  # nb_inplace_power
        types.binaryfunc_p,   # nb_inplace_lshift
        types.binaryfunc_p,   # nb_inplace_rshift
        types.binaryfunc_p,   # nb_inplace_and
        types.binaryfunc_p,   # nb_inplace_xor
        types.binaryfunc_p,   # nb_inplace_or

        types.binaryfunc_p,   # nb_floor_divide
        types.binaryfunc_p,   # nb_true_divide
        types.binaryfunc_p,   # nb_inplace_floor_divide
        types.binaryfunc_p,   # nb_inplace_true_divide

        types.unaryfunc_p,    # nb_index

        types.binaryfunc_p,   # nb_matrix_multiply
        types.binaryfunc_p,   # nb_inplace_matrix_multiply
    )
    pynumbermethods_p = pynumbermethods.as_pointer()

    pysequencemethods = module.context.get_identified_type("PySequenceMethods")
    pysequencemethods.set_body(
        types.lenfunc_p,          # sq_length
        types.binaryfunc_p,       # sq_concat
        types.ssizeargfunc_p,     # sq_repeat
        types.ssizeargfunc_p,     # sq_item
        void_p,           # was_sq_slice
        types.ssizeobjargproc_p,  # sq_ass_item
        void_p,           # was_sq_ass_slice
        types.objobjproc_p,       # sq_contains

        types.binaryfunc_p,       # sq_inplace_concat
        types.ssizeargfunc_p,     # sq_inplace_repeat
    )
    pysequencemethods_p = pysequencemethods.as_pointer()

    pymappingmethods = module.context.get_identified_type("PyMappingMethods")
    pymappingmethods.set_body(
        types.lenfunc_p,        # mp_length
        types.binaryfunc_p,     # mp_subscript
        types.objobjargproc_p,  # mp_ass_subscript
    )
    pymappingmethods_p = pymappingmethods.as_pointer()

    pybufferprocs = module.context.get_identified_type("PyBufferProcs")
    pybufferprocs.set_body(
        types.getbufferproc_p,      # bf_getbuffer
        types.releasebufferproc_p,  # bf_releasebuffer
    )
    pybufferprocs_p = pybufferprocs.as_pointer()

    pymethoddef = module.context.get_identified_type("PyMethodDef")
    pymethoddef.set_body(
        char_p,          # ml_name   The name of the built-in function/method
        types.pyobj_function_p,  # ml_meth   The C function that implements it
        int8,            # ml_flags  Combination of METH_xxx flags, which
                         #             mostly describe the args expected by
                         #             the C func
        char_p           # ml_doc    The __doc__ attribute, or NULL
    )
    pymethoddef_p = pymethoddef.as_pointer()

    pymemberdef = module.context.get_identified_type("PyMemberDef")
    pymemberdef.set_body(
        char_p,   # name
        int8,     # type
        ssize_t,  # offset
        int8,     # flags
        char_p,   # doc
    )
    pymemberdef_p = pymemberdef.as_pointer()

    pygetsetdef = module.context.get_identified_type("PyGetSetDef")
    pygetsetdef.set_body(
        char_p,  # name
        types.getter_p,  # get
        types.setter_p,  # set
        char_p,  # doc
        void_p,  # closure - optional function pointer
    )
    pygetsetdef_p = pygetsetdef.as_pointer()

    pytypeobject.set_body(
        ob_refcount,
        ob_type,
        ob_size,
        char_p,               # tp_name
        ssize_t,              # tp_basicsize
        ssize_t,              # tp_itemsize

        # Methods to implement standard operations
        types.destructor_p,           # tp_dealloc
        ssize_t,              # tp_vectorcall_offset
        types.getattrfunc_p,          # tp_getattr
        types.setattrfunc_p,          # tp_setattr
        pyasyncmethods_p,     # tp_as_async
        types.reprfunc_p,             # tp_repr

        # Method suites for standard classes
        pynumbermethods_p,    # tp_as_number
        pysequencemethods_p,  # tp_as_sequence
        pymappingmethods_p,   # tp_as_mapping

        # More standard operations (here for binary compatibility)
        types.hashfunc_p,             # tp_hash
        types.ternaryfunc_p,          # tp_call
        types.reprfunc_p,             # tp_str
        types.getattrofunc_p,         # tp_getattro
        types.setattrofunc_p,         # tp_setattro

        # Functions to access object as input/output buffer
        pybufferprocs_p,      # tp_as_buffer

        int32,                # tp_flags
        char_p,               # tp_doc
        types.traverseproc_p,         # tp_traverse
        types.inquiry_p,              # tp_clear
        types.richcmpfunc_p,          # tp_richcompare
        ssize_t,              # tp_weaklistoffset

        types.getiterfunc_p,          # tp_iter
        types.iternextfunc_p,         # tp_iternext

        pymethoddef_p,        # tp_methods
        pymemberdef_p,        # tp_members
        pygetsetdef_p,        # tp_getset
        pytypeobject_p,       # tp_base
        pyobject_p,           # tp_dict
        types.descrgetfunc_p,         # tp_descrget
        types.descrsetfunc_p,         # tp_descrset
        ssize_t,              # tp_dictoffset
        types.initproc_p,             # tp_init
        types.allocfunc_p,            # tp_alloc
        types.newfunc_p,              # tp_new
        types.freefunc_p,             # tp_free  Low-level free-memory routine
        types.inquiry_p,              # tp_is_gc  For PyObject_IS_GC
        pyobject_p,           # tp_bases
        pyobject_p,           # tp_mro  method resolution order
        pyobject_p,           # tp_cache
        pyobject_p,           # tp_subclasses
        pyobject_p,           # tp_weaklist
        types.destructor_p,           # tp_del

        # Type attribute cache version tag. Added in version 2.6
        int64,                # tp_version_tag

        types.destructor_p,           # tp_finalize
        types.vectorcallfunc_p,       # tp_vectorcall
    )


def sizeof(type: ir.Type, builder: ir.IRBuilder):
    """
        `%Size = getelementptr %T* null, i32 1`

        This code is effectively pretending that there is an array of `T`
        elements, starting at the `null` pointer. This gets a pointer to the
        2nd `T` element (element #1) in the array and treats it as an integer.
        This computes the size of one `T` element.
    """
    return builder.gep(type.as_pointer()("null"), [int32(1)])


def offsetof(type: ir.Aggregate, index: int, ptrtype=ssize_t):
    element_ty = type.gep(int32(index))
    element_ty_repr = element_ty._to_string()
    return f"bitcast ({element_ty_repr}* getelementptr ({type._to_string()}, {type.as_pointer()('null')}, i32 0, i32 {index}) to {ptrtype})"


def global_constant_string(module: ir.Module, name: str, value: str):
    encoded = value.encode()
    array_ty = ir.ArrayType(int8, len(encoded)+1)
    global_variable = ir.GlobalVariable(module, array_ty, name)
    elements = [int8(n) for n in encoded]
    elements.append(int8(0))
    initializer = array_ty(elements)
    global_variable.initializer = initializer
    global_variable.global_constant = True
    return global_variable


def define_PyType_Type(module: ir.Module, builder: ir.IRBuilder = None):
    pyobject = module.context.get_identified_type("PyObject")
    pytypeobject = module.context.get_identified_type("PyTypeObject")
    pymemberdef = module.context.get_identified_type("PyMemberDef")
    members_ty = ir.ArrayType(pymemberdef, 8)
    members = ir.GlobalVariable(module, members_ty, "PyType_Type__members")
    members_descr = [
        ("__basicsize__", T_PYSSIZET, "tp_basicsize", READONLY, None),
        ("__itemsize__", T_PYSSIZET, "tp_itemsize", READONLY, None),
        ("__flags__", T_ULONG, "tp_flags", READONLY, None),
        ("__weakrefoffset__", T_PYSSIZET, "tp_weaklistoffset", READONLY, None),
        ("__base__", T_OBJECT, "tp_base", READONLY, None),
        ("__dictoffset__", T_PYSSIZET, "tp_dictoffset", READONLY, None),
        ("__mro__", T_OBJECT, "tp_mro", READONLY, None)
    ]
    members_initializer = []
    for i, (name, m_type, field_name, flags, doc) in enumerate(members_descr):
        name_var = global_constant_string(module, f"PyType_Type__members.{i}", name)
        name_ptr = name_var.gep([int32(0), int32(0)])
        field_index = PYTYPEOBJECT_FIELD_NAMES.index(field_name)
        field_offset = offsetof(pytypeobject, field_index)
        doc_ptr = doc or char_p("null")
        member = pymemberdef([name_ptr, m_type, field_offset, flags, doc_ptr])
        members_initializer.append(member)
    members_initializer.append(None)
    members.initializer = members_ty(members_initializer)
    pyobject_p = pyobject.as_pointer()
    pytypeobject_p = pytypeobject.as_pointer()
    type_name = global_constant_string(module, "PyType_Type__name", "type")
    type = ir.GlobalVariable(module, pytypeobject, "PyType_Type")
    type.initializer = pytypeobject([
        ssize_t("null"),
        type.get_reference(),
        ssize_t("null"),
        type_name.gep([int32(0), int32(0)]),
        ssize_t("null"),
        ssize_t("null"),
        ir.FunctionType(void, [pyobject_p]).as_pointer()("null"),
        ssize_t("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, char_p]).as_pointer()("null"),
        ir.FunctionType(int8, [pyobject_p, char_p, pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyAsyncMethods").as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyNumberMethods").as_pointer()("null"),
        module.context.get_identified_type("PySequenceMethods").as_pointer()("null"),
        module.context.get_identified_type("PyMappingMethods").as_pointer()("null"),
        ir.FunctionType(ssize_t, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyBufferProcs").as_pointer()("null"),
        int32(0),                # tp_flags
        char_p("null"),               # tp_doc
        ir.FunctionType(int64, [pyobject_p, ir.FunctionType(int64, [pyobject_p, void_p]).as_pointer(), void_p]).as_pointer()("null"),         # tp_traverse
        ir.FunctionType(int8, [pyobject_p]).as_pointer()("null"),              # tp_clear
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, int8]).as_pointer()("null"),          # tp_richcompare
        ssize_t("null"),              # tp_weaklistoffset
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyMethodDef").as_pointer()("null"),
        members.gep([int32(0), int32(0)]),
        module.context.get_identified_type("PyGetSetDef").as_pointer()("null"),
        pytypeobject_p("null"),       # tp_base
        pyobject_p("null"),           # tp_dict
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),
        ssize_t("null"),              # tp_dictoffset
        ir.FunctionType(int8, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),             # tp_init
        ir.FunctionType(pyobject_p, [pytypeobject_p, ssize_t]).as_pointer()("null"),            # tp_alloc
        ir.FunctionType(pyobject_p, [pytypeobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),              # tp_new
        ir.FunctionType(void, [void_p]).as_pointer()("null"),
        ir.FunctionType(int8, [pyobject_p]).as_pointer()("null"),
        pyobject_p("null"),           # tp_bases;
        pyobject_p("null"),           # tp_mro; /* method resolution order */
        pyobject_p("null"),           # tp_cache;
        pyobject_p("null"),           # tp_subclasses;
        pyobject_p("null"),           # tp_weaklist;
        ir.FunctionType(void, [pyobject_p]).as_pointer()("null"),
        int64(1),                # tp_version_tag;
        ir.FunctionType(void, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p.as_pointer(), ssize_t, pyobject_p]).as_pointer()("null"),       # tp_vectorcall;
    ])
    return type


def define_PyBaseObject_Type(module: ir.Module):
    pyobject = module.context.get_identified_type("PyObject")
    pytypeobject = module.context.get_identified_type("PyTypeObject")
    typetype = module.get_global("PyType_Type")
    pyobject_p = pyobject.as_pointer()
    pytypeobject_p = pytypeobject.as_pointer()
    objecttype_name = global_constant_string(module, "PyBaseObject_Type__name", "object")
    objecttype = ir.GlobalVariable(module, pytypeobject, "PyBaseObject_Type")
    objecttype.initializer = pytypeobject([
        ssize_t("null"),
        typetype.get_reference(),
        ssize_t("null"),
        objecttype_name.gep([int32(0), int32(0)]),
        ssize_t("null"),
        ssize_t("null"),
        ir.FunctionType(void, [pyobject_p]).as_pointer()("null"),
        ssize_t("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, char_p]).as_pointer()("null"),
        ir.FunctionType(int8, [pyobject_p, char_p, pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyAsyncMethods").as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyNumberMethods").as_pointer()("null"),
        module.context.get_identified_type("PySequenceMethods").as_pointer()("null"),
        module.context.get_identified_type("PyMappingMethods").as_pointer()("null"),
        ir.FunctionType(ssize_t, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyBufferProcs").as_pointer()("null"),
        int32(0),                # tp_flags
        char_p("null"),               # tp_doc
        ir.FunctionType(int64, [pyobject_p, ir.FunctionType(int64, [pyobject_p, void_p]).as_pointer(), void_p]).as_pointer()("null"),         # tp_traverse
        ir.FunctionType(int8, [pyobject_p]).as_pointer()("null"),              # tp_clear
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, int8]).as_pointer()("null"),          # tp_richcompare
        ssize_t("null"),              # tp_weaklistoffset
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()("null"),
        module.context.get_identified_type("PyMethodDef").as_pointer()("null"),
        module.context.get_identified_type("PyMemberDef").as_pointer()("null"),
        module.context.get_identified_type("PyGetSetDef").as_pointer()("null"),
        pytypeobject_p("null"),       # tp_base
        pyobject_p("null"),           # tp_dict
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),
        ssize_t("null"),              # tp_dictoffset
        ir.FunctionType(int8, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),             # tp_init
        ir.FunctionType(pyobject_p, [pytypeobject_p, ssize_t]).as_pointer()("null"),            # tp_alloc
        ir.FunctionType(pyobject_p, [pytypeobject_p, pyobject_p, pyobject_p]).as_pointer()("null"),              # tp_new
        ir.FunctionType(void, [void_p]).as_pointer()("null"),
        ir.FunctionType(int8, [pyobject_p]).as_pointer()("null"),
        pyobject_p("null"),           # tp_bases;
        pyobject_p("null"),           # tp_mro; /* method resolution order */
        pyobject_p("null"),           # tp_cache;
        pyobject_p("null"),           # tp_subclasses;
        pyobject_p("null"),           # tp_weaklist;
        ir.FunctionType(void, [pyobject_p]).as_pointer()("null"),
        int64(1),                # tp_version_tag;
        ir.FunctionType(void, [pyobject_p]).as_pointer()("null"),
        ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p.as_pointer(), ssize_t, pyobject_p]).as_pointer()("null"),       # tp_vectorcall;
    ])
    return objecttype


if __name__ == "__main__":
    module = ir.Module(__name__)
    define_pyobjects_system(module)
    define_PyType_Type(module)
    define_PyBaseObject_Type(module)
    llvm_ir = str(module)
    print(f"Generated LLVM IR:\n\n{llvm_ir}\n")
    engine = create_execution_engine()
    mod = compile_ir(engine, llvm_ir)
    print()
