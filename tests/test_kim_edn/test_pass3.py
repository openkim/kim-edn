from tests.test_kim_edn import PyTest


DOCS = r'''
{
    "Test Pattern pass3": {
        "The outermost value": "must be an object or array.",
        "In this test": "It is an object."
    }
}
'''


class TestPass3:
    def test_parse(self):
        # test in/out equivalence and parsing
        res = self.loads(DOCS)
        out = self.dumps(res)

        self.assertEqual(res, self.loads(out))


class TestPyPass3(TestPass3, PyTest):
    pass
