from operator import mod
from llvmlite import ir


void = ir.VoidType()
void_p = void.as_pointer()
int8 = ir.IntType(8)
int32 = ir.IntType(32)
int64 = ir.IntType(64)
char = ir.IntType(8)
char_p = char.as_pointer()
size_t = ir.IntType(64)


def define_pyobjects_system(module: ir.Module):

    pyobject = module.context.get_identified_type("PyObject")
    pyvarobject = module.context.get_identified_type("PyVarObject")
    pytypeobject = module.context.get_identified_type("PyTypeObject")

    pyobject_p = pyobject.as_pointer()
    pytypeobject_p = pytypeobject.as_pointer()

    ob_refcount = int64
    ob_type = pytypeobject.as_pointer()
    pyobject.set_body(
        ob_refcount,
        ob_type
    )
    ob_size = size_t
    ob_base = pyobject
    pyvarobject.set_body(
        ob_base,
        ob_size
    )

    unaryfunc = ir.FunctionType(pyobject_p, [pyobject_p])
    binaryfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p])
    ternaryfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p])
    ssizeargfunc = ir.FunctionType(pyobject_p, [pyobject_p, int64])
    ssizeobjargproc = ir.FunctionType(int64, [pyobject_p, int64])
    objobjproc = ir.FunctionType(int64, [pyobject_p, pyobject_p])
    objobjargproc = ir.FunctionType(int64, [pyobject_p, pyobject_p, pyobject_p])
    sendfunc_result = int8  # one of 0 (Return), -1 (Error), 1 (Next)
    sendfunc = ir.FunctionType(sendfunc_result, [pyobject_p, pyobject_p, pyobject_p])
    inqury_result = int8
    inquiry = ir.FunctionType(inqury_result, [pyobject_p])
    destructor = ir.FunctionType(ir.VoidType(), [pyobject_p])
    printfunc = ir.FunctionType()
    reprfunc = ir.FunctionType(pyobject_p, [pyobject_p])
    getattrfunc = ir.FunctionType(pyobject_p, [pyobject_p, char_p])
    getattrofunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p])
    setattrfunc = ir.FunctionType(int8, [pyobject_p, char_p, pyobject_p])
    setattrofunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p])
    visitproc = ir.FunctionType(int64, [pyobject_p, void_p])  # 
    traverseproc = ir.FunctionType(int64, [pyobject_p, visitproc, void_p])
    richcmpfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, int8])
    getiterfunc = ir.FunctionType(pyobject_p, [pyobject_p])
    iternextfunc = ir.FunctionType(pyobject_p, [pyobject_p])
    lenfunc = ir.FunctionType(int64, [pyobject_p])
    descrgetfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p])
    descrsetfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p, pyobject_p])
    initproc = ir.FunctionType(int8, [pyobject_p, pyobject_p, pyobject_p])  # return 0 if ok -1 if exception
    allocfunc = ir.FunctionType(pyobject_p, [pytypeobject_p, int64])
    newfunc = ir.FunctionType(pyobject_p, [pytypeobject_p, pyobject_p, pyobject_p])
    freefunc = ir.FunctionType(void, [void_p])

    pyobject_p_arr_p = pyobject_p.as_pointer()
    vectorcallfunc = ir.FunctionType(pyobject_p, [pyobject_p, pyobject_p_arr_p, int64, pyobject_p])


    pyasyncmethods = module.context.get_identified_type("PyAsyncMethods")
    pyasyncmethods.set_body(
        unaryfunc,  # am_await;
        unaryfunc,  # am_aiter;
        unaryfunc,  # am_anext;
        sendfunc,   # am_send;
    )
    pyasyncmethods_p = pyasyncmethods.as_pointer()

    pynumbermethods = module.context.get_identified_type("PyNumberMethods")
    pyasyncmethods.set_body(
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
    pymethoddef_p = pymethoddef.as_pointer()

    pymemberdef = module.context.get_identified_type("PyMemberDef")
    pymemberdef_p = pymemberdef.as_pointer()

    pygetsetdef = module.context.get_identified_type("PyGetSetDef")
    pygetsetdef_p = pygetsetdef.as_pointer()

    pytypeobject.set_body(
        ob_base,
        char_p,               # tp_name
        int64,                # tp_basicsize
        int64,                # tp_itemsize

        # Methods to implement standard operations
        destructor,           # tp_dealloc
        printfunc,            # tp_print
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
        int64,                # tp_weaklistoffset

        getiterfunc,          # tp_iter
        iternextfunc,         # tp_iternext

        pymethoddef_p,       # tp_methods
        pymemberdef_p,       # tp_members
        pygetsetdef_p,        # tp_getset
        pytypeobject_p,       # tp_base
        pyobject_p,           # tp_dict
        descrgetfunc,         # tp_descrget
        descrsetfunc,         # tp_descrset
        int64,                # tp_dictoffset
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
