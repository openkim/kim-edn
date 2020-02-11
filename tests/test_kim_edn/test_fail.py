
from tests.test_kim_edn import PyTest


FAILDOCS = [
    # fail1
    '"A JSON payload should be an object or array, not a string."',
    # fail2
    '["Unclosed array"',
    # fail3
    '{unquoted_key: "keys must be quoted"}',
    # fail4
    '["extra comma",]',
    # fail5
    '["double extra comma",,]',
    # fail6
    '[   , "<-- missing value"]',
    # fail7
    '["Comma after the close"],',
    # fail8
    '["Extra close"]]',
    # fail9
    '{"Extra comma": true,}',
    # fail10
    '{"Extra value after close": true} "misplaced quoted value"',
    # fail11
    '{"Illegal expression": 1 + 2}',
    # fail12
    '{"Illegal invocation": alert()}',
    # fail13
    '{"Numbers cannot have leading zeroes": 013}',
    # fail14
    '{"Numbers cannot be hex": 0x14}',
    # fail15
    '["Illegal backslash escape: \\x15"]',
    # fail16
    '[\\naked]',
    # fail17
    '["Illegal backslash escape: \\017"]',
    # fail18
    '[[[[[[[[[[[[[[[[[[[["Too deep"]]]]]]]]]]]]]]]]]]]]',
    # fail19
    '{"Missing colon" null}',
    # fail20
    '{"Double colon":: null}',
    # fail21
    '{"Comma instead of colon", null}',
    # fail22
    '["Colon instead of comma": false]',
    # fail23
    '["Bad value", truth]',
    # fail24
    "['single quote']",
    # fail25
    '["\ttab\tcharacter\tin\tstring\t"]',
    # fail26
    '["tab\\   character\\   in\\  string\\  "]',
    # fail27
    '["line\nbreak"]',
    # fail28
    '["line\\\nbreak"]',
    # fail29
    '[0e]',
    # fail30
    '[0e+]',
    # fail31
    '[0e+-1]',
    # fail32
    '{"Comma instead if closing brace": true,',
    # fail33
    '["mismatch"}',
    # fail34
    '["A\u001FZ control characters in string"]',
    # fail35
    '["line\rreturn"]',
]

# None of these are the failure in EDN
SKIPS = {
    1: "why not have a string payload?",
    4: '["extra comma",]',
    5: '["double extra comma",,]',
    6: '[   , "<-- missing value"]',
    7: '["Comma after the close"],',
    9: '{"Extra comma": true,}',
    18: "spec doesn't specify any nesting limitations",
    25: "\t tab character in string is accepted in EDN",
    27: "\n newline character in string is accepted in EDN",
    35: "\r return character in string is accepted in EDN",
}


class TestFail:
    def test_failures(self):
        print("")
        for idx, doc in enumerate(FAILDOCS):
            idx += 1
            if idx in SKIPS:
                self.loads(doc)
                continue

            try:
                self.loads(doc)
            except self.KIMEDNDecodeError:
                pass
            else:
                self.fail(
                    "Expected failure for fail{0}: {1!r}".format(idx, doc))

    def test_non_string_keys_dict(self):
        data = {'a': 1, (1, 2): 2}
        msg = f'keys must be str, int, float, or bool, '
        msg += f'not {(1, 2).__class__.__name__}'
        with self.assertRaisesRegex(TypeError, msg):
            self.dumps(data)

    def test_not_serializable(self):
        import sys
        msg = f'Object of type {sys.__class__.__name__} '
        msg += f'is not KIM-EDN serializable'
        with self.assertRaisesRegex(TypeError, msg):
            self.dumps(sys)

    def test_truncated_input(self):
        test_cases = [
            ('', 'Expecting value', 0),
            ('[', 'Expecting value', 1),
            ('[42', "Expecting value", 3),
            ('[42,', 'Expecting value', 4),
            ('["', 'Unterminated string starting at', 1),
            ('["spam', 'Unterminated string starting at', 1),
            ('["spam"', "Expecting value", 7),
            ('["spam",', 'Expecting value', 8),
            ('{', 'Expecting property name enclosed in double quotes', 1),
            ('{"', 'Unterminated string starting at', 1),
            ('{"spam', 'Unterminated string starting at', 1),
            ('{"spam"', "Expecting value", 7),
            ('{"spam":', 'Expecting value', 8),
            ('{"spam":42', "Expecting property name enclosed in double quotes", 10),
            ('{"spam":42,', 'Expecting property name enclosed in double quotes', 11),
        ]

        test_cases += [
            ('"', 'Unterminated string starting at', 0),
            ('"spam', 'Unterminated string starting at', 0),
        ]

        for data, msg, idx in test_cases:
            with self.assertRaises(self.KIMEDNDecodeError) as cm:
                self.loads(data)

            err = cm.exception

            self.assertEqual(err.msg, msg)
            self.assertEqual(err.pos, idx)
            self.assertEqual(err.lineno, 1)
            self.assertEqual(err.colno, idx + 1)
            self.assertEqual(str(err), '%s: line 1 column %d (char %d)' %
                             (msg, idx + 1, idx))

    def test_unexpected_data(self):
        test_cases = [
            ('[,', 'Expecting value', 2),
            ('{"spam":[}', 'Expecting value', 9),
            ('[42:', "Expecting value", 3),
            ('[42 "spam"', "Expecting value", 10),
            ('{"spam":[42}', "Expecting value", 11),
            ('["]', 'Unterminated string starting at', 1),
            ('["spam":', "Expecting value", 7),
            ('{:', 'Expecting property name enclosed in double quotes', 1),
            ('{,', 'Expecting property name enclosed in double quotes', 2),
            ('{42', 'Expecting property name enclosed in double quotes', 1),
            ('[{]', 'Expecting property name enclosed in double quotes', 2),
            ('{"spam",', "Expecting value", 8),
            ('{"spam"}', "Expecting value", 8),
            ('[{"spam"]', "Expecting value", 9),
            ('{"spam":}', 'Expecting value', 8),
            ('[{"spam":]', 'Expecting value', 9),
            ('{"spam":42 "ham"', "Expecting value", 16),
            ('[{"spam":42]', "Expecting property name enclosed in double quotes", 11),
        ]

        for data, msg, idx in test_cases:
            with self.assertRaises(self.KIMEDNDecodeError) as cm:
                self.loads(data)

            err = cm.exception

            self.assertEqual(err.msg, msg)
            self.assertEqual(err.pos, idx)
            self.assertEqual(err.lineno, 1)
            self.assertEqual(err.colno, idx + 1)
            self.assertEqual(str(err), '%s: line 1 column %d (char %d)' %
                             (msg, idx + 1, idx))

    def test_extra_data(self):
        test_cases = [
            ('[]]', 'Extra data', 2),
            ('{}}', 'Extra data', 2),
            ('[],[]', 'Extra data', 3),
            ('{},{}', 'Extra data', 3),
        ]

        test_cases += [
            ('42,"spam"', 'Extra data', 3),
            ('"spam",42', 'Extra data', 7),
        ]

        for data, msg, idx in test_cases:
            with self.assertRaises(self.KIMEDNDecodeError) as cm:
                self.loads(data)

            err = cm.exception

            self.assertEqual(err.msg, msg)
            self.assertEqual(err.pos, idx)
            self.assertEqual(err.lineno, 1)
            self.assertEqual(err.colno, idx + 1)
            self.assertEqual(str(err), '%s: line 1 column %d (char %d)' %
                             (msg, idx + 1, idx))

    def test_linecol(self):
        test_cases = [
            ('!', 1, 1, 0),
            (' !', 1, 2, 1),
            ('\n!', 2, 1, 1),
            ('\n  \n\n     !', 4, 6, 10),
        ]

        for data, line, col, idx in test_cases:
            with self.assertRaises(self.KIMEDNDecodeError) as cm:
                self.loads(data)

            err = cm.exception

            self.assertEqual(err.msg, 'Expecting value')
            self.assertEqual(err.pos, idx)
            self.assertEqual(err.lineno, line)
            self.assertEqual(err.colno, col)
            self.assertEqual(str(err), 'Expecting value: line %s column %d (char %d)' %
                             (line, col, idx))


class TestPyFail(TestFail, PyTest):
    pass
