from collections import defaultdict
from functools import wraps

# Maps hook name → list of hook functions
HOOKS = defaultdict(list)

def register_hook(name, func):
    """Register a hook function for the given namespace (e.g., 'users.get_user_score')"""
    HOOKS[name].append(func)

def get_hooks(name):
    """Get list of hook functions for the given name"""
    return HOOKS.get(name, [])

def hook_function(name):
    """
    Decorator for plugins to register a hook function for a given target function.
    The hook must accept: (next_func, original_func, *args, **kwargs)
    """
    def decorator(func):
        register_hook(name, func)
        return func
    return decorator

def call_hooks(name):
    """
    Decorator to wrap a core function and allow plugins to hook into it.

    Each hook is called like: hook(next_func, original_func, *args, **kwargs)
    Hooks can:
      - run logic and call next_func(...) to continue the chain
      - or call original_func(...) to bypass other hooks
    """
    def decorator(original_func):
        @wraps(original_func)
        def wrapper(*args, **kwargs):
            hooks = get_hooks(name)
            if not hooks:
                return original_func(*args, **kwargs)

            def call_next(index, *a, **kw):
                if index < len(hooks):
                    return hooks[index](
                        lambda *a2, **kw2: call_next(index + 1, *a2, **kw2),
                        original_func,
                        *a, **kw
                    )
                return original_func(*a, **kw)

            return call_next(0, *args, **kwargs)

        return wrapper
    return decorator
