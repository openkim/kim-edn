from collections import OrderedDict
from test.support import bigaddrspacetest
from tests.test_kim_edn import PyTest


CASES = [
    ('/\\"\ucafe\ubabe\uab98\ufcde\ubcda\uef4a\x08\x0c\n\r\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?',
     '"/\\\\\\"\\ucafe\\ubabe\\uab98\\ufcde\\ubcda\\uef4a\\b\\f\\n\\r\\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?"'),
    ('\u0123\u4567\u89ab\ucdef\uabcd\uef4a',
     '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
    ('controls', '"controls"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    ('{"object with 1 member":["array with 1 element"]}',
     '"{\\"object with 1 member\\":[\\"array with 1 element\\"]}"'),
    (' s p a c e d ', '" s p a c e d "'),
    ('\U0001d120', '"\\ud834\\udd20"'),
    ('\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    ("`1~!@#$%^&*()_+-={':[,]}|;.</>?", '"`1~!@#$%^&*()_+-={\':[,]}|;.</>?"'),
    ('\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    ('\u0123\u4567\u89ab\ucdef\uabcd\uef4a',
     '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
]


class TestEncodeBasestringAscii:
    def test_encode_basestring_ascii(self):
        fname = self.kim_edn.encoder.encode_basestring_ascii.__name__

        for input_string, expect in CASES:
            result = self.kim_edn.encoder.encode_basestring_ascii(input_string)

            self.assertEqual(result, expect,
                             '{0!r} != {1!r} for {2}({3!r})'.format(
                                 result, expect, fname, input_string))

    def test_ordered_dict(self):
        # See issue 6105
        items = [('one', 1), ('two', 2), ('three', 3),
                 ('four', 4), ('five', 5)]

        s = self.dumps(OrderedDict(items))

        self.assertEqual(
            s, '{"one" 1 "two" 2 "three" 3 "four" 4 "five" 5}')

    def test_sorted_dict(self):
        items = [('one', 1), ('two', 2), ('three', 3),
                 ('four', 4), ('five', 5)]

        s = self.dumps(dict(items), sort_keys=True)

        self.assertEqual(
            s, '{"five" 5 "four" 4 "one" 1 "three" 3 "two" 2}')


CASES2 = [
    (["short-name", {"source-value": ["hcp"]}],
     '["short-name" {"source-value" ["hcp"]}]'),
    ("\"P6_3/mmc", '"\\"P6_3/mmc"'),
    ('\\', '"\\\\"'),
    ({"domain": "openkim.org", "data-method": "computation", "author": "John Doe"},
     '{"domain" "openkim.org" "data-method" "computation" "author" "John Doe"}'),
    (['openkim.org'], '["openkim.org"]')
]


class TestEncodeBase:
    def test_encode_bases(self):
        for input_, expect_ in CASES2:
            result_ = self.kim_edn.dumps(input_)

            self.assertEqual(result_, expect_,
                             '{!r} != {!r} for ({!r})'.format(
                                 result_, expect_, input_))

        def encode_complex(obj):
            if isinstance(obj, complex):
                return [obj.real, obj.imag]
            msg = 'Object of type {} '.format(obj.__class__.__name__)
            msg += 'is not KIM-EDN serializable'
            raise TypeError(msg)

        result_ = self.kim_edn.dumps(2 + 1j, default=encode_complex)

        self.assertEqual(result_, '[2.0 1.0]',
                         '{!r} != {!r} for ({!r})'.format(
                             result_, '[2.0 1.0]', 2 + 1j))


class TestPyEncodeBasestringAscii(TestEncodeBasestringAscii, PyTest):
    pass


class TestPyTestEncodeBase(TestEncodeBase, PyTest):
    pass
