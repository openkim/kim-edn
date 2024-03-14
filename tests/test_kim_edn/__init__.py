import kim_edn
import unittest


class PyTest(unittest.TestCase):
    """Make a basic py test class.

    The basic py test class will be used by the other tests.

    """

    loads = staticmethod(kim_edn.loads)
    dumps = staticmethod(kim_edn.dumps)
    KIMEDNDecodeError = staticmethod(kim_edn.KIMEDNDecodeError)
    kim_edn = staticmethod(kim_edn)
