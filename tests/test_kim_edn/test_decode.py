import decimal
from io import StringIO
from collections import OrderedDict

from tests.test_kim_edn import PyTest


class TestDecode:
    def test_float(self):
        rval = self.loads('1.1')

        self.assertTrue(isinstance(rval, float))
        self.assertEqual(rval, 1.1)

    def test_empty_objects(self):
        self.assertEqual(self.loads('{}'), {})
        self.assertEqual(self.loads('[]'), [])
        self.assertEqual(self.loads('""'), "")

    def test_object_pairs_hook(self):
        s = '{"xkd":1, "kcw":2, "art":3, "hxm":4, "qrt":5, "pad":6, "hoy":7}'
        p = [("xkd", 1), ("kcw", 2), ("art", 3), ("hxm", 4),
             ("qrt", 5), ("pad", 6), ("hoy", 7)]

        self.assertEqual(self.loads(s), eval(s))
        self.assertEqual(self.loads(s, object_pairs_hook=lambda x: x), p)
        self.assertEqual(self.kim_edn.load(StringIO(s),
                                           object_pairs_hook=lambda x: x), p)

        od = self.loads(s, object_pairs_hook=OrderedDict)

        self.assertEqual(od, OrderedDict(p))
        self.assertEqual(type(od), OrderedDict)

        # the object_pairs_hook takes priority over the object_hook
        self.assertEqual(self.loads(s, object_pairs_hook=OrderedDict,
                                    object_hook=lambda x: None),
                         OrderedDict(p))

        # check that empty object literals work (see #17368)
        self.assertEqual(self.loads('{}', object_pairs_hook=OrderedDict),
                         OrderedDict())

        self.assertEqual(self.loads('{"empty": {}}',
                                    object_pairs_hook=OrderedDict),
                         OrderedDict([('empty', OrderedDict())]))

    def test_decoder_optimizations(self):
        # Several optimizations were made that skip over calls to
        # the whitespace regex, so this test is designed to try and
        # exercise the uncommon cases. The array cases are already covered.
        rval = self.loads('{   "key"    :    "value"    ,  "k":"v"    }')

        self.assertEqual(rval, {"key": "value", "k": "v"})

    def check_keys_reuse(self, source, loads):
        rval = loads(source)
        (a, b), (c, d) = sorted(rval[0]), sorted(rval[1])

        self.assertIs(a, c)
        self.assertIs(b, d)

    def test_keys_reuse(self):
        s = '[{"a_key": 1, "b_\xe9": 2}, {"a_key": 3, "b_\xe9": 4}]'
        self.check_keys_reuse(s, self.loads)

        decoder = self.kim_edn.decoder.KIMEDNDecoder()

        self.check_keys_reuse(s, decoder.decode)

        self.assertFalse(decoder.memo)

    def test_extra_data(self):
        s = '[1, 2, 3]5'
        msg = 'Extra data'
        self.assertRaisesRegex(self.KIMEDNDecodeError, msg, self.loads, s)

    def test_invalid_escape(self):
        s = '["abc\\y"]'
        msg = 'escape'
        self.assertRaisesRegex(self.KIMEDNDecodeError, msg, self.loads, s)

    def test_invalid_input_type(self):
        msg_ = 'the EDN object must be str, bytes or bytearray, '
        for value in [1, 3.14, [], {}, None, float('nan'), float('inf'), float('-inf')]:

            # Like assertRaises() but also tests that regex matches on the
            # string representation of the raised exception.
            msg = msg_ + 'not {}'.format(value.__class__.__name__)
            self.assertRaisesRegex(TypeError, msg, self.loads, value)

    def test_string_with_utf8_bom(self):
        bom_kim_edn = "[1,2,3]".encode('utf-8-sig').decode('utf-8')

        with self.assertRaises(self.KIMEDNDecodeError) as cm:
            self.loads(bom_kim_edn)

        self.assertIn('BOM', str(cm.exception))

        with self.assertRaises(self.KIMEDNDecodeError) as cm:
            self.kim_edn.load(StringIO(bom_kim_edn))

        self.assertIn('BOM', str(cm.exception))

        # make sure that the BOM is not detected in the middle of a string
        bom_in_str = '"{}"'.format(''.encode('utf-8-sig').decode('utf-8'))

        self.assertEqual(self.loads(bom_in_str), '\ufeff')

        self.assertEqual(self.kim_edn.load(StringIO(bom_in_str)), '\ufeff')

    def test_negative_index(self):
        d = self.kim_edn.KIMEDNDecoder()

        self.assertRaises(ValueError, d.raw_decode, 'a' * 42, -50000)


class TestPyDecode(TestDecode, PyTest):
    pass
