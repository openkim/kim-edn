import os
import subprocess
import sys
import textwrap
import unittest

from test import support

if sys.version_info.minor >= 10:
    from test.support import os_helper

if sys.version_info.minor >= 9:
    from test.support.script_helper import assert_python_ok


@support.requires_subprocess()
class TestTool(unittest.TestCase):
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
        self.assertEqual(process.stdout, self.expect)
        self.assertEqual(process.stderr, '')

    @unittest.skipIf(sys.version_info.minor < 10, "not supported in this Python version")
    def _create_infile(self, data=None):
        infile = os_helper.TESTFN
        with open(infile, "w", encoding="utf-8") as fp:
            self.addCleanup(os.remove, infile)
            fp.write(data or self.data)
        return infile

    @unittest.skipIf(sys.version_info.minor < 9, "not supported in this Python version")
    def test_infile_stdout(self):
        infile = self._create_infile()
        rc, out, err = assert_python_ok('-m', 'kim_edn.tool', infile)
        self.assertEqual(rc, 0)
        self.assertEqual(out.splitlines(), self.expect.encode().splitlines())
        self.assertEqual(err, b'')

    @unittest.skipIf(sys.version_info.minor < 9, "not supported in this Python version")
    def test_non_ascii_infile(self):
        data = '{"msg": "\u3053\u3093\u306b\u3061\u306f"}'
        expect = textwrap.dedent('''\
        {
            "msg" "\\u3053\\u3093\\u306b\\u3061\\u306f"
        }

        ''').encode()

        infile = self._create_infile(data)
        rc, out, err = assert_python_ok('-m', 'kim_edn.tool', infile)

        self.assertEqual(rc, 0)
        self.assertEqual(out.splitlines(), expect.splitlines())
        self.assertEqual(err, b'')

    @unittest.skipIf(sys.version_info.minor < 10, "not supported in this Python version")
    def test_infile_outfile(self):
        infile = self._create_infile()
        outfile = os_helper.TESTFN + '.out'
        rc, out, err = assert_python_ok('-m', 'kim_edn.tool', infile, outfile)
        self.addCleanup(os.remove, outfile)
        with open(outfile, "r", encoding="utf-8") as fp:
            self.assertEqual(fp.read(), self.expect)
        self.assertEqual(rc, 0)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

    @unittest.skipIf(sys.version_info.minor < 9, "not supported in this Python version")
    def test_writing_in_place(self):
        infile = self._create_infile()
        rc, out, err = assert_python_ok('-m', 'kim_edn.tool', infile, infile)
        with open(infile, "r", encoding="utf-8") as fp:
            self.assertEqual(fp.read(), self.expect)
        self.assertEqual(rc, 0)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

    def test_edn_lines(self):
        args = sys.executable, '-m', 'kim_edn.tool', '--edn-lines'
        process = subprocess.run(args, input=self.ednlines_raw, capture_output=True, text=True, check=True)
        self.assertEqual(process.stdout, self.ednlines_expect)
        self.assertEqual(process.stderr, '')

    @unittest.skipIf(sys.version_info.minor < 9, "not supported in this Python version")
    def test_help_flag(self):
        rc, out, err = assert_python_ok('-m', 'kim_edn.tool', '-h')
        self.assertEqual(rc, 0)
        self.assertTrue(out.startswith(b'usage: '))
        self.assertEqual(err, b'')

    @unittest.skipIf(sys.version_info.minor < 9, "not supported in this Python version")
    def test_sort_keys_flag(self):
        infile = self._create_infile()
        rc, out, err = assert_python_ok('-m', 'kim_edn.tool', '--sort-keys', infile)
        self.assertEqual(rc, 0)
        self.assertEqual(out.splitlines(),
                         self.expect_without_sort_keys.encode().splitlines())
        self.assertEqual(err, b'')

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
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')

    def test_no_indent(self):
        input_ = '[1,\n2]'
        expect = '[1 2]\n\n'
        args = sys.executable, '-m', 'kim_edn.tool', '--no-indent'
        process = subprocess.run(args, input=input_, capture_output=True, text=True, check=True)
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')

    def test_tab(self):
        input_ = '[1, 2]'
        expect = '[\n\t1 \n\t2\n]\n\n'
        args = sys.executable, '-m', 'kim_edn.tool', '--tab'
        process = subprocess.run(args, input=input_, capture_output=True, text=True, check=True)
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')

    def test_compact(self):
        input_ = '[ 1 ,\n 2]'
        expect = '[1 2]\n\n'
        args = sys.executable, '-m', 'kim_edn.tool', '--compact'
        process = subprocess.run(args, input=input_, capture_output=True, text=True, check=True)
        self.assertEqual(process.stdout, expect)
        self.assertEqual(process.stderr, '')
