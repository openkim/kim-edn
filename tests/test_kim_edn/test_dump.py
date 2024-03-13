from io import StringIO
import os
from tests.test_kim_edn import PyTest


class TestDump:
    def test_dump(self):
        sio = StringIO()

        self.kim_edn.dump({}, sio)
        self.assertEqual(sio.getvalue(), '{}\n')   # NOTE

        d = {1337: "true.ed"}
        self.addCleanup(os.remove, d[1337])

        self.kim_edn.dump(d, d[1337])

        self.assertEqual(self.kim_edn.load('{"1337" "true.ed"}'),
                         self.kim_edn.load(d[1337]))

    def test_dumps(self):
        self.assertEqual(self.dumps({}), '{}')

    def test_encode_truefalse(self):
        self.assertEqual(self.dumps(
            {True: False, False: True}, sort_keys=True),
            '{"false" true "true" false}')

        self.assertEqual(self.dumps(
            {2: 3.0, 4.0: 5, False: 1, 6: True}, sort_keys=True),
            '{"false" 1 "2" 3.0 "4.0" 5 "6" true}')

    def test_encode_evil_dict(self):
        class D(dict):
            def keys(self):
                return L

        class X:
            def __hash__(self):
                del L[0]
                return 1337

            def __lt__(self, o):
                return 0

        L = [X() for i in range(1122)]
        d = D()
        d[hash(d.keys()[0])] = "true.edn"

        self.assertEqual(self.dumps(d, sort_keys=(not L[0] < L[1])),
                         '{"1337" "true.edn"}')


class TestPyDump(TestDump, PyTest):
    pass
