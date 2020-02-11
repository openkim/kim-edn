from tests.test_kim_edn import PyTest

class TestDefault:
    def test_default(self):
        self.assertEqual(
            self.dumps(type, default=repr),
            self.dumps(repr(type)))


class TestPyDefault(TestDefault, PyTest):
    pass
