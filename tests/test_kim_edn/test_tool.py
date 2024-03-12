import os
import subprocess
import sys
from tests.test_kim_edn import PyTest
import textwrap
import unittest

if sys.version_info.minor >= 10:
    from test.support import os_helper


class TestTool:
    data = """

        [["blorpie"],[ "whoops" ] , [
                                 ],\t"d-shtaeou",\r"d-nthiouh",
        "i-vhbjkhnth", {"nifty":87}, {"morefield" :\tfalse,"field"
            :"yes"}  ]
           """

    expect = textwrap.dedent("""\
    [
        [
            "blorpie"
        ] 
        [
            "whoops"
        ] 
        [] 
        "d-shtaeou" 
        "d-nthiouh" 
        "i-vhbjkhnth" 
        {
            "nifty" 87
        } 
        {
            "morefield" false 
            "field" "yes"
        }
    ]

    """)  # noqa

    ednlines_raw = textwrap.dedent("""\
    {"ingredients":["frog","water","chocolate","glucose"]}
    {"ingredients":["chocolate","steel bolts"]}
    """)

    ednlines_expect = textwrap.dedent("""\
    {
        "ingredients" [
            "frog" 
            "water" 
            "chocolate" 
            "glucose"
        ]
    }
 
    {
        "ingredients" [
            "chocolate" 
            "steel bolts"
        ]
    }

    """)  # noqa

    expect_without_sort_keys = textwrap.dedent("""\
    [
        [
            "blorpie"
        ] 
        [
            "whoops"
        ] 
        [] 
        "d-shtaeou" 
        "d-nthiouh" 
        "i-vhbjkhnth" 
        {
            "nifty" 87
        } 
        {
            "field" "yes" 
            "morefield" false
        }
    ]

    """)  # noqa

    def test_stdin_stdout(self):
        args = sys.executable, '-m', 'kim_edn.tool'
        process = subprocess.run(args, input=self.data, capture_output=True, text=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, self.expect)
        self.assertEqual(process.stderr, '')

    @unittest.skipIf(sys.version_info.minor < 10, "not supported in this Python version")
    def _create_infile(self, data=None):
        infile = os_helper.TESTFN
        with open(infile, "w", encoding="utf-8") as fp:
            self.addCleanup(os.remove, infile)
            fp.write(data or self.data)

        return infile

    def test_infile_stdout(self):
        infile = self._create_infile()
        args = sys.executable, '-m', 'kim_edn.tool', infile
        process = subprocess.run(args, capture_output=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout.splitlines(), self.expect.encode().splitlines())
        self.assertEqual(process.stderr, b'')

    def test_non_ascii_infile(self):
        data = '{"msg": "\u3053\u3093\u306b\u3061\u306f"}'
        expect = textwrap.dedent('''\
        {
            "msg" "\\u3053\\u3093\\u306b\\u3061\\u306f"
        }

        ''').encode()

        infile = self._create_infile(data)
        args = sys.executable, '-m', 'kim_edn.tool', infile
        process = subprocess.run(args, capture_output=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout.splitlines(), expect.splitlines())
        self.assertEqual(process.stderr, b'')

    @unittest.skipIf(sys.version_info.minor < 10, "not supported in this Python version")
    def test_infile_outfile(self):
        infile = self._create_infile()
        outfile = os_helper.TESTFN + '.out'
        args = sys.executable, '-m', 'kim_edn.tool', infile, outfile
        process = subprocess.run(args, capture_output=True, check=True)

        self.addCleanup(os.remove, outfile)

        with open(outfile, "r", encoding="utf-8") as fp:
            self.assertEqual(fp.read(), self.expect)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, b'')
        self.assertEqual(process.stderr, b'')

    def test_writing_in_place(self):
        infile = self._create_infile()
        args = sys.executable, '-m', 'kim_edn.tool', infile, infile
        process = subprocess.run(args, capture_output=True, check=True)

        with open(infile, "r", encoding="utf-8") as fp:
            self.assertEqual(fp.read(), self.expect)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, b'')
        self.assertEqual(process.stderr, b'')

    def test_edn_lines(self):
        args = sys.executable, '-m', 'kim_edn.tool', '--edn-lines'
        process = subprocess.run(args, input=self.ednlines_raw, capture_output=True, text=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, self.ednlines_expect)
        self.assertEqual(process.stderr, '')

    def test_help_flag(self):
        args = sys.executable, '-m', 'kim_edn.tool', '-h'
        process = subprocess.run(args, capture_output=True, text=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertTrue(process.stdout.startswith('usage: '))
        self.assertEqual(process.stderr, '')

    def test_sort_keys_flag(self):
        infile = self._create_infile()
        args = sys.executable, '-m', 'kim_edn.tool', '--sort-keys', infile
        process = subprocess.run(args, capture_output=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout.splitlines(),
                         self.expect_without_sort_keys.encode().splitlines())
        self.assertEqual(process.stderr, b'')

    def test_indent(self):
        input_ = '[1, 2]'
        expect = textwrap.dedent('''\
        [
          1 
          2
        ]

        ''')  # noqa
        args = sys.executable, '-m', 'kim_edn.tool', '--indent', '2'
        process = subprocess.run(args, input=input_, capture_output=True, text=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')

    def test_no_indent(self):
        input_ = '[1,\n2]'
        expect = '[1 2]\n\n'
        args = sys.executable, '-m', 'kim_edn.tool', '--no-indent'
        process = subprocess.run(args, input=input_, capture_output=True, text=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')

    def test_tab(self):
        input_ = '[1, 2]'
        expect = '[\n\t1 \n\t2\n]\n\n'
        args = sys.executable, '-m', 'kim_edn.tool', '--tab'
        process = subprocess.run(args, input=input_, capture_output=True, text=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')

    def test_compact(self):
        input_ = '[ 1 ,\n 2]'
        expect = '[1 2]\n\n'
        args = sys.executable, '-m', 'kim_edn.tool', '--compact'
        process = subprocess.run(args, input=input_, capture_output=True, text=True, check=True)

        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')


class TestPyTestTool(TestTool, PyTest):
    pass
