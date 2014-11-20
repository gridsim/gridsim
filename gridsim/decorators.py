"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>

Gridsim decorators module. Defines all decorators used in the Gridsim simulator.

"""

import warnings
from functools import wraps


def accepts(*atypes):
    """
    Type Enforcement. Verifies types of parameters given to the function.
    
    *Example:*
    ::

        @accepts((0,int), (1,(int,float)))
        def func(arg1, arg2):
            return arg1 * arg2

    .. warning::
        In a class function, the current class cannot be used (e.g.: ``self``
        type cannot be defined with ``accepts``)
    """

    def check_accepts(func):

        @wraps(func)
        def new_func(*args, **keywords):

            if len(atypes) != 0 and type(atypes[0]) is not tuple:
                raise AttributeError("Missing brackets in accepts of function "
                                     + func.__name__)

            for atype in atypes:

                if type(atype[0]) is tuple:
                    for apos in atype[0]:

                        default_param = False
                        try:
                            args[apos]
                        except IndexError:
                            default_param = True

                        if not default_param \
                                and not isinstance(args[apos], atype[1]):
                            raise TypeError(
                                "In"+func.__name__+", "
                                "params value %r does not "
                                "match %s" % (args[apos], atype[1]))
                else:

                    default_param = False
                    try:
                        args[atype[0]]
                    except IndexError:
                        default_param = True

                    if not default_param \
                            and not isinstance(args[atype[0]], atype[1]):
                        raise TypeError(
                            "In"+func.__name__+", "
                            "params value %r does not "
                            "match %s" % (args[atype[0]], atype[1]))

            return func(*args, **keywords)

        return new_func

    return check_accepts


def returns(rtype=type(None)):
    """
    Type Enforcement. Verifies return type of the function.
    
    *Example:*
    ::

        @returns((int,float))
        def func(arg1, arg2):
            return arg1 * arg2

    """

    def check_returns(f):

        @wraps(f)
        def new_f(*args, **keywords):

            result = f(*args, **keywords)
            if not isinstance(result, rtype):
                raise TypeError(
                    "return value %r does not match %s" % (result, rtype))
            return result

        return new_f

    return check_returns


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    *Example:*
    ::

        @deprecated
        def func(arg1, arg2):
            return arg1 * arg2

    """

    @wraps(func)
    def new_func(*args, **keywords):

        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **keywords)

    return new_func


def singleton(cls):
    """
    This is a decorator which can be used to mark classes
    as singleton.

    *Example:*
    ::

        @singleton
        class MyClass:

        MyClass.get_instance()

    """

    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance


