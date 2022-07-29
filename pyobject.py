from llvmlite import ir

from llvm_operations import create_execution_engine, compile_ir
from primitives import allocate, charstring


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


def define_pyobjects_system(module: ir.Module):

    pyobject = module.context.get_identified_type("PyObject")
    pyvarobject = module.context.get_identified_type("PyVarObject")
    pytypeobject = module.context.get_identified_type("PyTypeObject")
    pybuffer = module.context.get_identified_type("Py_buffer")

    pyobject_p = pyobject.as_pointer()
    pytypeobject_p = pytypeobject.as_pointer()
    pybuffer_p = pybuffer.as_pointer()

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
        void_p,      # buf;
        pyobject_p,  # obj;        /* owned reference */
        ssize_t,     # len;
        ssize_t,     # itemsize;  /* This is Py_ssize_t so it can be
                     #              pointed to by strides in simple case.*/
        int8,        # readonly;
        int8,        # ndim;
        char_p,      # format;
        ssize_t_p,   # shape;
        ssize_t_p,   # strides;
        ssize_t_p,   # suboffsets;
        void_p,      # internal;
    )

    unaryfunc = ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()
    binaryfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()
    ternaryfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()
    ssizeargfunc = ir.FunctionType(pyobject_p, [pyobject_p, ssize_t]).as_pointer()
    ssizeobjargproc = ir.FunctionType(int64, [pyobject_p, ssize_t]).as_pointer()
    objobjproc = ir.FunctionType(int64, [pyobject_p, pyobject_p]).as_pointer()
    objobjargproc = ir.FunctionType(int64, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()
    pyobj_function = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()
    sendfunc_result = int8  # one of 0 (Return), -1 (Error), 1 (Next)
    sendfunc = ir.FunctionType(sendfunc_result, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()
    inqury_result = int8
    inquiry = ir.FunctionType(inqury_result, [pyobject_p]).as_pointer()
    destructor = ir.FunctionType(void, [pyobject_p]).as_pointer()
    reprfunc = ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()
    hashfunc = ir.FunctionType(ssize_t, [pyobject_p]).as_pointer()
    getattrfunc = ir.FunctionType(pyobject_p, [pyobject_p, char_p]).as_pointer()
    getattrofunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()
    setattrfunc = ir.FunctionType(int8, [pyobject_p, char_p, pyobject_p]).as_pointer()
    setattrofunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p]).as_pointer()
    getter = ir.FunctionType(pyobject_p, [pyobject_p, void_p]).as_pointer()
    setter = ir.FunctionType(int8, [pyobject_p, pyobject_p, void_p]).as_pointer()
    visitproc = ir.FunctionType(int64, [pyobject_p, void_p]).as_pointer()
    traverseproc = ir.FunctionType(int64, [pyobject_p, visitproc, void_p]).as_pointer()
    richcmpfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, int8]).as_pointer()
    getiterfunc = ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()
    iternextfunc = ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()
    lenfunc = ir.FunctionType(ssize_t, [pyobject_p]).as_pointer()
    descrgetfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()
    descrsetfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()
    initproc = ir.FunctionType(int8, [pyobject_p, pyobject_p, pyobject_p]).as_pointer()  # return 0 if ok -1 if exception
    allocfunc = ir.FunctionType(pyobject_p, [pytypeobject_p, ssize_t]).as_pointer()
    newfunc = ir.FunctionType(pyobject_p, [pytypeobject_p, pyobject_p, pyobject_p]).as_pointer()
    freefunc = ir.FunctionType(void, [void_p]).as_pointer()

    pyobject_p_arr_p = pyobject_p.as_pointer()
    vectorcallfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p_arr_p, ssize_t, pyobject_p]).as_pointer()

    getbufferproc = ir.FunctionType(int8, [pyobject_p, pybuffer_p, int8]).as_pointer()
    releasebufferproc = ir.FunctionType(void, [pyobject_p, pybuffer_p]).as_pointer()

    pyasyncmethods = module.context.get_identified_type("PyAsyncMethods")
    pyasyncmethods.set_body(
        unaryfunc,  # am_await;
        unaryfunc,  # am_aiter;
        unaryfunc,  # am_anext;
        sendfunc,   # am_send;
    )
    pyasyncmethods_p = pyasyncmethods.as_pointer()

    pynumbermethods = module.context.get_identified_type("PyNumberMethods")
    pynumbermethods.set_body(
        binaryfunc,   # nb_add;
        binaryfunc,   # nb_subtract;
        binaryfunc,   # nb_multiply;
        binaryfunc,   # nb_remainder;
        binaryfunc,   # nb_divmod;
        ternaryfunc,  # nb_power;
        unaryfunc,    # nb_negative;
        unaryfunc,    # nb_positive;
        unaryfunc,    # nb_absolute;
        inquiry,      # nb_bool;
        unaryfunc,    # nb_invert;
        binaryfunc,   # nb_lshift;
        binaryfunc,   # nb_rshift;
        binaryfunc,   # nb_and;
        binaryfunc,   # nb_xor;
        binaryfunc,   # nb_or;
        unaryfunc,    # nb_int;
        
        void_p,       # nb_reserved;  /* the slot formerly known as nb_long */
        unaryfunc,    # nb_float;

        binaryfunc,   # nb_inplace_add;
        binaryfunc,   # nb_inplace_subtract;
        binaryfunc,   # nb_inplace_multiply;
        binaryfunc,   # nb_inplace_remainder;
        ternaryfunc,  # nb_inplace_power;
        binaryfunc,   # nb_inplace_lshift;
        binaryfunc,   # nb_inplace_rshift;
        binaryfunc,   # nb_inplace_and;
        binaryfunc,   # nb_inplace_xor;
        binaryfunc,   # nb_inplace_or;

        binaryfunc,   # nb_floor_divide;
        binaryfunc,   # nb_true_divide;
        binaryfunc,   # nb_inplace_floor_divide;
        binaryfunc,   # nb_inplace_true_divide;

        unaryfunc,    # nb_index;

        binaryfunc,   # nb_matrix_multiply;
        binaryfunc,   # nb_inplace_matrix_multiply;
    )
    pynumbermethods_p = pynumbermethods.as_pointer()

    pysequencemethods = module.context.get_identified_type("PySequenceMethods")
    pysequencemethods.set_body(
        lenfunc,          # sq_length;
        binaryfunc,       # sq_concat;
        ssizeargfunc,     # sq_repeat;
        ssizeargfunc,     # sq_item;
        void_p,           # was_sq_slice;
        ssizeobjargproc,  # sq_ass_item;
        void_p,           # was_sq_ass_slice;
        objobjproc,       # sq_contains;

        binaryfunc,       # sq_inplace_concat;
        ssizeargfunc,     # sq_inplace_repeat;
    )
    pysequencemethods_p = pysequencemethods.as_pointer()

    pymappingmethods = module.context.get_identified_type("PyMappingMethods")
    pymappingmethods.set_body(
        lenfunc,        # mp_length;
        binaryfunc,     # mp_subscript;
        objobjargproc,  # mp_ass_subscript;
    )
    pymappingmethods_p = pymappingmethods.as_pointer()

    pybufferprocs = module.context.get_identified_type("PyBufferProcs")
    pybufferprocs.set_body(
        getbufferproc,      # bf_getbuffer;
        releasebufferproc,  # bf_releasebuffer;
    )
    pybufferprocs_p = pybufferprocs.as_pointer()

    pymethoddef = module.context.get_identified_type("PyMethodDef")
    pymethoddef.set_body(
        char_p,          # ml_name;   /* The name of the built-in function/method */
        pyobj_function,  # ml_meth;    /* The C function that implements it */
        int8,            # ml_flags;   /* Combination of METH_xxx flags, which mostly
                         #          describe the args expected by the C func */
        char_p           # ml_doc;    /* The __doc__ attribute, or NULL */
    )
    pymethoddef_p = pymethoddef.as_pointer()

    pymemberdef = module.context.get_identified_type("PyMemberDef")
    pymemberdef.set_body(
        char_p,  # name
        int8,    # type
        ssize_t,  # offset
        int8,    # flags
        char_p,  # doc
    )
    pymemberdef_p = pymemberdef.as_pointer()

    pygetsetdef = module.context.get_identified_type("PyGetSetDef")
    pygetsetdef.set_body(
        char_p,  # name
        getter,  # get
        setter,  # set
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
        destructor,           # tp_dealloc
        ssize_t,              # tp_vectorcall_offset
        getattrfunc,          # tp_getattr
        setattrfunc,          # tp_setattr
        pyasyncmethods_p,     # tp_as_async
        reprfunc,             # tp_repr

        # Method suites for standard classes
        pynumbermethods_p,    # tp_as_number
        pysequencemethods_p,  # tp_as_sequence
        pymappingmethods_p,   # tp_as_mapping

        # More standard operations (here for binary compatibility)
        hashfunc,             # tp_hash
        ternaryfunc,          # tp_call
        reprfunc,             # tp_str
        getattrofunc,         # tp_getattro 
        setattrofunc,         # tp_setattro

        # Functions to access object as input/output buffer
        pybufferprocs_p,      # tp_as_buffer

        int32,                # tp_flags
        char_p,               # tp_doc
        traverseproc,         # tp_traverse
        inquiry,              # tp_clear
        richcmpfunc,          # tp_richcompare
        ssize_t,              # tp_weaklistoffset

        getiterfunc,          # tp_iter
        iternextfunc,         # tp_iternext

        pymethoddef_p,       # tp_methods
        pymemberdef_p,       # tp_members
        pygetsetdef_p,        # tp_getset
        pytypeobject_p,       # tp_base
        pyobject_p,           # tp_dict
        descrgetfunc,         # tp_descrget
        descrsetfunc,         # tp_descrset
        ssize_t,              # tp_dictoffset
        initproc,             # tp_init
        allocfunc,            # tp_alloc
        newfunc,              # tp_new
        freefunc,             # tp_free; /* Low-level free-memory routine */
        inquiry,              # tp_is_gc; /* For PyObject_IS_GC */
        pyobject_p,           # tp_bases;
        pyobject_p,           # tp_mro; /* method resolution order */
        pyobject_p,           # tp_cache;
        pyobject_p,           # tp_subclasses;
        pyobject_p,           # tp_weaklist;
        destructor,           # tp_del;

        # /* Type attribute cache version tag. Added in version 2.6 */
        int64,                # tp_version_tag;

        destructor,           # tp_finalize;
        vectorcallfunc,       # tp_vectorcall;
    )


def define_PyTypeObject_new(module: ir.Module):
    pyobject = module.context.get_identified_type("PyObject")
    pytypeobject = module.context.get_identified_type("PyTypeObject")
    pyasyncmethods = module.context.get_identified_type("PyAsyncMethods")
    pyobject_p = pyobject.as_pointer()
    pytypeobject_p = pytypeobject.as_pointer()
    pyasyncmethods_p = pyasyncmethods.as_pointer()
    pytypeobject_new_fnty = ir.FunctionType(
        pytypeobject_p, (
            size_t, pytypeobject_p,
            size_t, char_p,
            ssize_t, ssize_t,
            ir.FunctionType(void, [pyobject_p]).as_pointer(),
            ssize_t,
            ir.FunctionType(pyobject_p, [pyobject_p, char_p]).as_pointer(),
            ir.FunctionType(int8, [pyobject_p, char_p, pyobject_p]).as_pointer(),
            pyasyncmethods_p,
            ir.FunctionType(pyobject_p, [pyobject_p]).as_pointer()
        ))
    pytypeobject_new_fn = ir.Function(module, pytypeobject_new_fnty, name="PyTypeObject_new")
    block = pytypeobject_new_fn.append_basic_block('entry')
    builder = ir.IRBuilder(block)
    type = allocate(pytypeobject, builder, name='newTypeObject')
    tp_refcount_ptr = builder.gep(type, [int32_0, int32_0], name='tp_refcount_ptr')
    tp_type_ptr = builder.gep(type, [int32_0, int32(1)], name='tp_type_ptr')
    tp_size_ptr = builder.gep(type, [int32_0, int32(2)], name='tp_size_ptr')
    tp_name_ptr = builder.gep(type, [int32_0, int32(3)], name='tp_name_ptr')
    tp_dealloc_ptr = builder.gep(type, [int32_0, int32(6)], name='tp_dealloc_ptr')
    tp_vectorcall_offset_ptr = builder.gep(type, [int32_0, int32(7)], name='tp_vectorcall_offset_ptr')
    tp_getattr_ptr = builder.gep(type, [int32_0, int32(8)], name='tp_getattr_ptr')
    tp_setattr = builder.gep(type, [int32_0, int32(9)], name='tp_setattr_ptr')
    tp_as_async = builder.gep(type, [int32_0, int32(10)], name='tp_as_async_ptr')
    tp_repr = builder.gep(type, [int32_0, int32(11)], name='tp_repr_ptr')
    # builder.store(pytypeobject_new_fn.args[], )
    builder.store(pytypeobject_new_fn.args[0], tp_refcount_ptr)
    builder.store(pytypeobject_new_fn.args[1], tp_type_ptr)
    builder.store(pytypeobject_new_fn.args[2], tp_size_ptr)
    builder.store(pytypeobject_new_fn.args[3], tp_name_ptr)
    builder.store(pytypeobject_new_fn.args[6], tp_dealloc_ptr)
    builder.store(pytypeobject_new_fn.args[7], tp_vectorcall_offset_ptr)
    builder.store(pytypeobject_new_fn.args[8], tp_getattr_ptr)
    builder.store(pytypeobject_new_fn.args[9], tp_setattr)
    builder.store(pytypeobject_new_fn.args[10], tp_as_async)
    builder.store(pytypeobject_new_fn.args[11], tp_repr)
    builder.ret(type)
    return pytypeobject_new_fn
