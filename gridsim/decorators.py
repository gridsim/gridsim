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

    if __debug__:
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
    else:
        def check_accepts(func):
            return func

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
    if __debug__:
        def check_returns(func):

            @wraps(func)
            def new_f(*args, **keywords):

                result = func(*args, **keywords)
                if not isinstance(result, rtype):
                    raise TypeError(
                        "return value %r does not match %s" % (result, rtype))
                return result

            return new_f
    else:
        def check_returns(func):
            return func

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


if __debug__:

    import time
    import inspect

    PROF_DATA = {}

    def timed(func):
        """
        This is a decorator which can be used to register the execution time of
        functions.

        To display the result use :func:`print_time_registered`

        *Example:*
        ::

            @timed
            def func(arg1, arg2):
                return arg1 * arg2

            [...]

            print_time_registered()

        .. warning:: only reachable in debug mode (if `__debug__` is `True`).
        """
        @wraps(func)
        def with_profiling(*args, **kwargs):
            start_time = time.time()

            ret = func(*args, **kwargs)

            elapsed_time = time.time() - start_time

            cls_id = ""
            for cls in inspect.getmro(func.im_class):
                if func.__name__ in cls.__dict__:
                    cls_id = str(cls)


            func_id = cls_id+'.'+func.__name__

            if func_id not in PROF_DATA:
                PROF_DATA[func_id] = [0, []]
            PROF_DATA[func_id][0] += 1
            PROF_DATA[func_id][1].append(elapsed_time)

            return ret

        return with_profiling

    def print_time_registered():
        """
        Display registered time of function with :func:`timed` decorator.

        .. warning:: only reachable in debug mode (if `__debug__` is `True`).
        """
        for func_name, data in PROF_DATA.items():
            max_time = max(data[1])
            avg_time = sum(data[1]) / len(data[1])
            print "Function %s called %d times. " % (func_name, data[0]),
            print 'Execution time max: %.7f, average: %.7f' % (max_time, avg_time)

    import atexit
    atexit.register(print_time_registered)
