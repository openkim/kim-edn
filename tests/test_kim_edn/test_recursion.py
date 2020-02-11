from tests.test_kim_edn import PyTest


class KIMEDNTestObject:
    pass


class TestRecursion:
    def test_listrecursion(self):
        x = []
        x.append(x)
        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on list recursion")

        x = []
        y = [x]
        x.append(y)

        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on alternating list recursion")

        y = []
        x = [y, y]
        # ensure that the marker is cleared
        self.dumps(x)

    def test_dictrecursion(self):
        x = {}
        x["test"] = x

        try:
            self.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on dict recursion")

        x = {}
        y = {"a": x, "b": x}
        # ensure that the marker is cleared
        self.dumps(x)

    def test_defaultrecursion(self):
        class RecursiveKIMEDNEncoder(self.kim_edn.KIMEDNEncoder):
            recurse = False

            def default(self, o):
                if o is KIMEDNTestObject:
                    if self.recurse:
                        return [KIMEDNTestObject]
                    else:
                        return 'KIMEDNTestObject'

                return kim_edn.KIMEDNEncoder.default(o)

        enc = RecursiveKIMEDNEncoder()

        self.assertEqual(enc.encode(KIMEDNTestObject), '"KIMEDNTestObject"')

        enc.recurse = True

        try:
            enc.encode(KIMEDNTestObject)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on default recursion")

    def test_highly_nested_objects_decoding(self):
        # test that loading highly-nested objects doesn't segfault
        with self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '1' + '}' * 100000)

        with self.assertRaises(RecursionError):
            self.loads('{"a":' * 100000 + '[1]' + '}' * 100000)

        with self.assertRaises(RecursionError):
            self.loads('[' * 100000 + '1' + ']' * 100000)

    def test_highly_nested_objects_encoding(self):
        l, d = [], {}

        for x in range(100000):
            l, d = [l], {'k': d}

        with self.assertRaises(RecursionError):
            self.dumps(l)

        with self.assertRaises(RecursionError):
            self.dumps(d)

    def test_endless_recursion(self):
        class EndlessKIMEDNEncoder(self.kim_edn.KIMEDNEncoder):
            def default(self, o):
                """Fail ValueError after detecting the circular reference."""
                return [o]

        with self.assertRaises(ValueError):
            EndlessKIMEDNEncoder().encode(5j)


class TestPyRecursion(TestRecursion, PyTest):
    pass
