=============
nicedecorator
=============

.. image:: https://travis-ci.org/craigds/nicedecorator.png?branch=master
   :target: https://travis-ci.org/craigds/nicedecorator

Intro
=====

``nicedecorator`` provides a *nice* way of doing decorators in Python.

Where you might normally do something horribly confusing like this::

    def debug_function(output_to=None):
        def dec(func):
            from django.db import transaction

            @wraps(func)
            def wrapper(*args, **kwargs):
                output_to.write(
                    "%s called. args=%r, kwargs=%r" % (func.__name__, args, kwargs)
                )

                return func(*args, **kwargs)
            return wrapper

        if callable(output_to):
            # decorator called without parentheses.
            # i.e. @debug_function
            func, output_to = output_to, sys.stderr
            return dec(func)
        else:
            # decorator called with parentheses.
            # i.e. @debug_function()
            output_to = sys.stderr
            return dec

    @debug_function(output_to=sys.stdout)
    def myfunc():
        pass

    @debug_function
    def myotherfunc():
        pass

You can now do something much *nicer*::

    class debug_function(NiceDecorator):
        def __init__(self, func, output_to=sys.stderr):
            super(debug_function, self).__init__(func)
            self.output_to = output_to

        def __call__(self, *args, **kwargs):
            self.output_to.write(
                "%s called. args=%r, kwargs=%r" % (func.__name__, args, kwargs)
            )
            return self.func(*args, **kwargs)

    @debug_function(output_to=sys.stdout)
    def myfunc():
        pass

    @debug_function
    def myotherfunc():
        pass


Licensed under the New BSD License.


Features
========

* Handles either `@decorator` or `@decorator(args..)` syntax *nicely*
* Rather a *nice* use case for demonstrating how metaclasses are *nice*.


Requirements
============

* Python 2.6, 2.7, or 3.3+
