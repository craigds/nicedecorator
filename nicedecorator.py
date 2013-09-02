import functools
import sys


__all__ = ('NiceDecorator',)


def available_attrs(fn):
    """
    Return the list of functools-wrappable attributes on a callable.
    This is required as a workaround for http://bugs.python.org/issue3445
    under Python 2.
    """
    if sys.version > '3.':
        return functools.WRAPPER_ASSIGNMENTS
    else:
        return tuple(a for a in functools.WRAPPER_ASSIGNMENTS if hasattr(fn, a))


def wraps(fn, **kwargs):
    """
    Wraps plain functools.wraps to workaround http://bugs.python.org/issue3445 which
    means __call__ methods make it explode.
    """
    return functools.wraps(fn, assigned=available_attrs(fn), **kwargs)


def with_metaclass(meta, base=object):
    """
    Create a base class with a metaclass.
    Required to support both the Python 2 and 3 ways of doing metaclasses.
    """
    return meta("NewBase", (base,), {})


class NiceDecoratorMeta(type):
    def __call__(self, *args, **kwargs):
        # yeah, this is confusing...
        #   `self`: a NiceDecoratorMeta *instance*, ie NiceDecorator or a subclass
        #   `args`, `kwargs`: arguments that we're going to pass to
        #        NiceDecorator.__init__ eventually (i.e. decorator arguments)
        args = list(args)

        def decorate(func):
            decorated = super(NiceDecoratorMeta, self).__call__(func, *args, **kwargs)
            return wraps(func, updated=())(decorated)

        is_decorator_factory = self.is_decorator_factory
        if is_decorator_factory is None:
            # auto-detect whether this is a decorator factory.
            is_decorator_factory = not (len(args) == 1 and callable(args[0]) and not kwargs)

        if is_decorator_factory:
            # decorator factory, like @dec()
            return decorate
        else:
            # plain decorator, like @dec
            func = args.pop(0)
            return decorate(func)


class NiceDecorator(with_metaclass(NiceDecoratorMeta, base=object)):
    """
    Base class for class-based decorators.

    Subclasses should define a `__call__` method which takes the same args
    as the function. It may call `self.func` which is the original function.

    If the decorator takes arguments, you should also override __init__()
    to accept them.

    Example:
        class debug_call(NiceDecorator):
            def __init__(self, func, a_decorator_kwarg=None):
                super(debug_call, self).__init__(func)
                self.a_decorator_kwarg = a_decorator_kwarg

            def __call__(self, *args, **kwargs):
                print "decorated with a_decorator_kwarg=%s" % self.a_decorator_kwarg
                print "calling func", args, kwargs
                self.func(*args, **kwargs)
                print "returning"

    Notes:
      * Works with functions, no worries.
      * When used with instance methods, the instance is passed as the
        second argument to the decorator's __call__ method.
        That's fine if you're just dumbly passing (*args, **kwargs) to the decorated
        function, but otherwise you should use something like
        django.utils.decorators.method_decorator to prevent this from happening.
      * Works with classmethods, but same caveat as instance methods, and also this
        decorator must be inside the @classmethod decorator. i.e.:

            @classmethod
            @mydecorator
            def foo(cls):
                pass
    """
    __metaclass__ = NiceDecoratorMeta

    # if this is set to None, the decorator will try to detect
    # whether it has been called as @decorator or @decorator().
    # Set this to True if your decorator-factory needs to accept a
    # single callable argument, since that will muck up the detection.
    is_decorator_factory = None

    def __init__(self, func):
        if isinstance(func, classmethod):
            raise TypeError(
                "@classmethod must be outside %s decorator" %
                self.__class__.__name__
            )
        self.func = func

    def __get__(self, instance, klass):
        """Support instance methods."""
        func = functools.partial(self.__call__, instance)
        return wraps(self.func)(func)
