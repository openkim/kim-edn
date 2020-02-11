from tests.test_kim_edn import PyTest


DOCS = r'''
[[[[[[[[[[[[[[[[[[["Not too deep"]]]]]]]]]]]]]]]]]]]
'''


class TestPass2:
    def test_parse(self):
        # test in/out equivalence and parsing
        res = self.loads(DOCS)
        out = self.dumps(res)

        self.assertEqual(res, self.loads(out))


class TestPyPass2(TestPass2, PyTest):
    pass
