"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>

Gridsim decorators module. Defines all decorators used in the Gridsim simulator.


.. method:: timed

This decorator can be used to register the execution time of
class methods.

*Example*::

    class MyClass(object):
        @timed
        def my_short_func(arg1, arg2):
            return arg1 * arg2

        @timed
        def my_long_func(arg1, arg2):
            # long section of code
            ...

.. warning:: This decorator only works with class methods and not
             with functions.

At the end of the execution, the console prompt the time for each function::

    Function MyClass.my_short_func 1 times.  Execution time max: 0.0000119, average: 0.0000119 Total time: 0.0000119
    Function MyClass.my_long_func called 13 times.  Execution time max: 0.0001291, average: 0.0001177 Total time: 0.0015298


"""

import time
import warnings
from functools import wraps


def accepts(*atypes):
    """
    accepts()

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
                                    "In '"+func.__name__+"', "
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
    returns()

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
    deprecated()

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


class _Timed(object):

    def __init__(self):
        """
        Also commented in top of file for website.

        This is a decorator which can be used to register the execution
        time of class methods.

        *Example:*
        ::
            class MyClass(object):
                @timed
                def func(arg1, arg2):
                    return arg1 * arg2

            [...]

        .. warning:: This decorator only works with class methods and not
                     with functions.

        """
        self._data = {}

    def __call__(self, func):

        @wraps(func)
        def store_time(inst, *args, **kwargs):

            start_time = time.time()

            ret = func(inst, *args, **kwargs)

            elapsed_time = time.time() - start_time

            func_id = inst.__class__.__name__+'.'+func.__name__
            if func_id not in self._data:
                self._data[func_id] = [0, []]
            self._data[func_id][0] += 1
            self._data[func_id][1].append(elapsed_time)

            return ret

        return store_time

    def print_time_registered(self):
        """
        Display registered time of function with :func:`timed` decorator.

        Automatically called at exit.
        """
        for func_name, data in self._data.items():
            max_time = max(data[1])
            sum_time = sum(data[1])
            avg_time = sum_time / len(data[1])
            print("Function %s called %d times. " % (func_name, data[0]),)
            print('Execution time max: %.7f, average: %.7f' % (max_time, avg_time),)
            print("Total time: %.7f" % sum_time)
timed = _Timed()

import atexit
atexit.register(timed.print_time_registered)
