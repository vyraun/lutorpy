import os
import ctypes
lualib = ctypes.CDLL(os.path.expanduser("~") + "/torch/install/lib/libluajit.so", mode=ctypes.RTLD_GLOBAL)

import inspect
# We need to enable global symbol visibility for lupa in order to
# support binary module loading in Lua.  If we can enable it here, we
# do it temporarily.

def _try_import_with_global_library_symbols():
    try:
        import DLFCN
        dlopen_flags = DLFCN.RTLD_NOW | DLFCN.RTLD_GLOBAL
    except ImportError:
        import ctypes
        dlopen_flags = ctypes.RTLD_GLOBAL

    import sys
    old_flags = sys.getdlopenflags()
    try:
        sys.setdlopenflags(dlopen_flags)
        import lutorpy._lupa
    finally:
        sys.setdlopenflags(old_flags)

try:
    _try_import_with_global_library_symbols()
except:
    pass

del _try_import_with_global_library_symbols

# the following is all that should stay in the namespace:

from lutorpy._lupa import *

try:
    from lutorpy.version import __version__
except ImportError:
    pass

import lutorpy
lua = lutorpy.LuaRuntime()
lutorpy.lua = lua

globals_ = None
def update_globals(enable_warning=False):
    if globals_ is None:
        return
    lg = lua.globals()
    for k in lg:
        ks = str(k)
        if globals_.has_key(ks):
            if inspect.ismodule(globals_[ks]):
                if enable_warning:
                    print("WARNING: variable "+ ks + ' is already exist in python globals, use ' + ks + '_ to refer to the lua version')
                globals_[ks + '_'] = lg[ks]
                continue
        globals_[ks] = lg[ks]

def set_globals(g):
    global globals_
    globals_ = g
    update_globals(True)
    
def eval(cmd):
    ret = lua.eval(cmd)
    update_globals()
    return ret

def execute(cmd):
    ret = lua.execute(cmd)
    update_globals()
    return ret

def require(module_name):
    ret = lua.require(module_name)
    update_globals()
    return ret

def boostrap_self(obj,func_name):
    '''
        bootstrap a function to add self as the first argument
    '''
    if obj[func_name+'_']:
        return
    func = obj[func_name]
    def func_self(*opt):
        func(obj,*opt)
    obj[func_name+'_'] = func
    obj[func_name] = func_self

bs = boostrap_self