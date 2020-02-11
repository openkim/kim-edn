from enum import Enum, IntEnum
from math import isnan
from tests.test_kim_edn import PyTest


SMALL = 1
BIG = 1 << 32
HUGE = 1 << 64
REALLY_HUGE = 1 << 96


class BigNum(IntEnum):
    small = SMALL
    big = BIG
    huge = HUGE
    really_huge = REALLY_HUGE


E = 2.718281
PI = 3.141593
TAU = 2 * PI


class FloatNum(float, Enum):
    e = E
    pi = PI
    tau = TAU


INF = float('inf')
NEG_INF = float('-inf')
NAN = float('nan')


class WierdNum(float, Enum):
    inf = INF
    neg_inf = NEG_INF
    nan = NAN


class TestEnum:

    def test_floats(self):
        for enum in FloatNum:
            self.assertEqual(self.dumps(enum), repr(enum.value))
            self.assertEqual(float(self.dumps(enum)), enum)
            self.assertEqual(self.loads(self.dumps(enum)), enum)

    def test_weird_floats(self):

        for enum in WierdNum:
            self.assertRaises(ValueError, self.dumps, enum)

    def test_ints(self):
        for enum in BigNum:
            self.assertEqual(self.dumps(enum), str(enum.value))
            self.assertEqual(int(self.dumps(enum)), enum)
            self.assertEqual(self.loads(self.dumps(enum)), enum)

    def test_list(self):
        self.assertEqual(self.dumps(list(BigNum)),
                         str([SMALL, BIG, HUGE, REALLY_HUGE]).replace(',', ''))
        self.assertEqual(self.loads(self.dumps(list(BigNum))),
                         list(BigNum))
        self.assertEqual(self.dumps(list(FloatNum)),
                         str([E, PI, TAU]).replace(',', ''))
        self.assertEqual(self.loads(self.dumps(list(FloatNum))),
                         list(FloatNum))
        self.assertRaises(ValueError, self.dumps, list(WierdNum))

    def test_dict_keys(self):
        s, b, h, r = BigNum
        e, p, t = FloatNum
        d = {s: 'tiny', b: 'large', h: 'larger', r: 'largest',
             e: "Euler's number", p: 'pi', t: 'tau'}

        nd = self.loads(self.dumps(d))

        self.assertEqual(nd[str(SMALL)], 'tiny')
        self.assertEqual(nd[str(BIG)], 'large')
        self.assertEqual(nd[str(HUGE)], 'larger')
        self.assertEqual(nd[str(REALLY_HUGE)], 'largest')
        self.assertEqual(nd[repr(E)], "Euler's number")
        self.assertEqual(nd[repr(PI)], 'pi')
        self.assertEqual(nd[repr(TAU)], 'tau')

    def test_dict_values(self):
        d = dict(tiny=BigNum.small,
                 large=BigNum.big,
                 larger=BigNum.huge,
                 largest=BigNum.really_huge,
                 e=FloatNum.e,
                 pi=FloatNum.pi,
                 tau=FloatNum.tau)

        nd = self.loads(self.dumps(d))

        self.assertEqual(nd['tiny'], SMALL)
        self.assertEqual(nd['large'], BIG)
        self.assertEqual(nd['larger'], HUGE)
        self.assertEqual(nd['largest'], REALLY_HUGE)
        self.assertEqual(nd['e'], E)
        self.assertEqual(nd['pi'], PI)
        self.assertEqual(nd['tau'], TAU)


class TestPyEnum(TestEnum, PyTest):
    pass
