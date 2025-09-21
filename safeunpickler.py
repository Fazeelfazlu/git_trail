import pickle
import builtins
import io
safe_builtins = {
}

class SafeUnpickler(pickle.Unpickler):

    def find_class(self, module, name):        
        print(self, module, name)
        if module == "builtins" and name in safe_builtins:        
            return getattr(builtins, name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))

def safeunpickle(s):
    return SafeUnpickler(io.BytesIO(s)).load()