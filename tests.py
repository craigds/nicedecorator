from nicedecorator import NiceDecorator

import unittest

called = []


def a_function(arg1):
    called.append(('func', arg1))
    return 'returned'


def get_decorated_class_with_classmethod(decorator):
    class AClass(object):
        # note this only works if @classmethod is outside @decorator
        @classmethod
        @decorator
        def a_classmethod(cls, arg1):
            called.append(('classmethod', cls, arg1))
            return 'returned'

    return AClass


def get_decorated_class_with_instancemethod(decorator):
    class AClass(object):
        @decorator
        def a_instancemethod(self, arg1):
            called.append(('instancemethod', self, arg1))
            return 'returned'
        a_instancemethod.somekey = 'value'

    return AClass


def get_decorated_class_with_instancemethod2(decorator, decorator2):
    class AClass(object):
        @decorator
        @decorator2
        def a_instancemethod(self, arg1):
            called.append(('instancemethod', self, arg1))
            return 'returned'
        a_instancemethod.somekey = 'value'

    return AClass


class TestNiceDecorator(unittest.TestCase):
    def setUp(self):
        self.pop_called()

        self.count = 0

        class dec(NiceDecorator):
            def __init__(dec_self, func, *args, **kwargs):
                called.append(('__init__', (func,) + args, kwargs))
                dec_self.idx = self.count
                self.count += 1
                print("dec-init", dec_self.idx)
                super(dec, dec_self).__init__(func)

            def __call__(dec_self, *args, **kwargs):
                called.append(('__call__', args, kwargs))
                print("dec-call", dec_self.idx)
                return dec_self.func(*args, **kwargs)

        class dec2(NiceDecorator):
            def __init__(dec_self, func, *args, **kwargs):
                called.append(('dec2: __init__', (func,) + args, kwargs))
                dec_self.idx = self.count
                self.count += 1
                print("dec2-init", dec_self.idx)
                super(dec2, dec_self).__init__(func)

            def __call__(dec_self, *args, **kwargs):
                called.append(('dec2: __call__', args, kwargs))
                print("dec2-call", dec_self.idx)
                return dec_self.func(*args, **kwargs)

        self.dec = dec
        self.dec2 = dec2

    def pop_called(self):
        r = called[:]
        called[:] = []
        return r

    def test_decorator_function_unargumented(self):
        self.assertEqual(self.pop_called(), [])

        decorated = self.dec(a_function)
        self.assertEqual(self.pop_called(), [
            ('__init__', (a_function,), {}),
        ])

        self.assertEqual(decorated('an arg'), 'returned')
        self.assertEqual(self.pop_called(), [
            ('__call__', ('an arg',), {}),
            ('func', 'an arg'),
        ])

    def test_decorator_function_argumented(self):
        self.assertEqual(self.pop_called(), [])

        decorator = self.dec('arg1', kwarg1='kwarg1')
        self.assertEqual(self.pop_called(), [])

        decorated = decorator(a_function)
        self.assertEqual(self.pop_called(), [
            ('__init__', (a_function, 'arg1'), {'kwarg1': 'kwarg1'}),
        ])

        self.assertEqual(decorated('an arg'), 'returned')
        self.assertEqual(self.pop_called(), [
            ('__call__', ('an arg',), {}),
            ('func', 'an arg'),
        ])

    def test_decorator_function_stacked(self):
        """
        Testing stacking the decorators:

            @dec2('arg2')
            @dec
            def a_function(some_arg):
                return 'returned'
        """

        self.assertEqual(self.pop_called(), [])

        decorated1 = self.dec(a_function)
        self.assertEqual(self.pop_called(), [
            ('__init__', (a_function,), {}),
        ])

        decorated2 = self.dec2('arg2')(decorated1)
        self.assertEqual(self.pop_called(), [
            ('dec2: __init__', (decorated1, 'arg2'), {}),
        ])

        self.assertEqual(decorated2('an arg'), 'returned')
        r = self.pop_called()
        print(r)
        self.assertEqual(r, [
            ('dec2: __call__', ('an arg',), {}),
            ('__call__', ('an arg',), {}),
            ('func', 'an arg'),
        ])

    def test_decorator_function_stacked2(self):
        """
        Testing stacking the decorators:

            @dec
            @dec2
            def a_function(some_arg):
                return 'returned'
        """

        self.assertEqual(self.pop_called(), [])

        decorated2 = self.dec2(a_function)
        self.assertEqual(self.pop_called(), [
            ('dec2: __init__', (a_function,), {}),
        ])

        decorated1 = self.dec(decorated2)
        self.assertEqual(self.pop_called(), [
            ('__init__', (decorated2,), {}),
        ])

        self.assert_(decorated2.func is a_function, decorated2.func)
        self.assert_(decorated1.func is decorated2, decorated1.func)

        r = decorated1('an arg')
        called = self.pop_called()
        print(called)

        self.assertEqual(r, 'returned')
        self.assertEqual(decorated1.idx, 1)
        self.assertEqual(decorated2.idx, 0)

        self.assertEqual(called, [
            ('__call__', ('an arg',), {}),
            ('dec2: __call__', ('an arg',), {}),
            ('func', 'an arg'),
        ])

    def test_decorator_instancemethod_unargumented(self):
        klass = get_decorated_class_with_instancemethod(self.dec)

        klass_decoration_called = self.pop_called()
        self.assertEqual(len(klass_decoration_called), 1)

        instance = klass()
        self.assertEqual(self.pop_called(), [])

        self.assertEqual(instance.a_instancemethod('an arg'), 'returned')
        self.assertEqual(self.pop_called(), [
            ('__call__', (instance, 'an arg',), {}),
            ('instancemethod', instance, 'an arg'),
        ])

        # self.assertEqual(instance.a_instancemethod.somekey, 'value')

    def test_decorator_instancemethod_stacked(self):
        klass = get_decorated_class_with_instancemethod2(self.dec, self.dec2)

        klass_decoration_called = self.pop_called()
        print(klass_decoration_called)
        self.assertEqual(len(klass_decoration_called), 2)
        self.assertEqual(klass_decoration_called[0][0], 'dec2: __init__')
        self.assertEqual(klass_decoration_called[1][0], '__init__')

        instance = klass()
        self.assertEqual(self.pop_called(), [])

        self.assertEqual(instance.a_instancemethod('an arg'), 'returned')
        called = self.pop_called()
        print(called)
        self.assertEqual(called, [
            ('__call__', (instance, 'an arg',), {}),
            ('dec2: __call__', (instance, 'an arg',), {}),
            ('instancemethod', instance, 'an arg'),
        ])

    def test_decorator_instancemethod_argumented(self):
        decorator = self.dec('arg1', kwarg1='kwarg1')
        klass = get_decorated_class_with_instancemethod(decorator)

        klass_decoration_called = self.pop_called()
        self.assertEqual(len(klass_decoration_called), 1)

        instance = klass()
        self.assertEqual(self.pop_called(), [])

        self.assertEqual(instance.a_instancemethod('an arg'), 'returned')
        self.assertEqual(self.pop_called(), [
            ('__call__', (instance, 'an arg',), {}),
            ('instancemethod', instance, 'an arg'),
        ])

        # self.assertEqual(instance.a_instancemethod.somekey, 'value')

    def test_decorator_classmethod_unargumented(self):
        klass = get_decorated_class_with_classmethod(self.dec)

        klass_decoration_called = self.pop_called()
        self.assertEqual(len(klass_decoration_called), 1)

        self.assertEqual(klass.a_classmethod('an arg'), 'returned')
        self.assertEqual(self.pop_called(), [
            ('__call__', (klass, 'an arg',), {}),
            ('classmethod', klass, 'an arg'),
        ])

    def test_decorator_classmethod_argumented(self):
        decorator = self.dec('arg1', kwarg1='kwarg1')
        klass = get_decorated_class_with_classmethod(decorator)

        klass_decoration_called = self.pop_called()
        self.assertEqual(len(klass_decoration_called), 1)

        self.assertEqual(klass.a_classmethod('an arg'), 'returned')
        self.assertEqual(self.pop_called(), [
            ('__call__', (klass, 'an arg',), {}),
            ('classmethod', klass, 'an arg'),
        ])


if __name__ == '__main__':
    unittest.main()
