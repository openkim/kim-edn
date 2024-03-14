r"""Validate and pretty-print KIM-EDN tool.

Command-line tool to validate and pretty-print KIM-EDN
    Usage::
    $ echo '{"property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal"}' | python -m kim_edn.tool
    {
        "property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal"
    }

    $ echo '{"foo": ["bar", "baz"]}' | python -m kim_edn.tool
    {
        "foo" [
            "bar"
            "baz"
        ]
    }

    $ echo '{"foo" ["bar" "baz"]}' | python -m kim_edn.tool
    {
        "foo" [
            "bar"
            "baz"
        ]
    }

    # NOTE
    Wrong use case::
    $ echo '{1.2 3.4}' | python -m kim_edn.tool

    Expecting property name enclosed in double quotes: line 1 column 2 (char 1)

"""
import argparse
import kim_edn
import sys


def main():
    """Validate and pretty-print KIM-EDN tool main file."""
    prog = 'python -m kim_edn.tool'

    description = ('A simple command line interface for KIM-EDN module '
                   'to validate and pretty-print kim-EDN objects.')

    parser = argparse.ArgumentParser(prog=prog, description=description)

    parser.add_argument('infile', nargs='?',
                        help='a KIM-EDN file to be validated or pretty-printed',
                        default='-')

    parser.add_argument('outfile', nargs='?',
                        help='write the output of infile to outfile',
                        default=None)

    parser.add_argument('--sort-keys', action='store_true', default=False,
                        help='sort the output of dictionaries alphabetically by key')

    parser.add_argument('--edn-lines', action='store_true', default=False,
                        help='parse input using the kim_edn lines format')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--indent', default=4, type=int,
                       help='separate items with newlines and use this number '
                       'of spaces for indentation')

    group.add_argument('--tab', action='store_const', dest='indent',
                       const='\t', help='separate items with newlines and use '
                       'tabs for indentation')

    group.add_argument('--no-indent', action='store_const', dest='indent',
                       const=None,
                       help='separate items with spaces rather than newlines')

    group.add_argument('--compact', action='store_true',
                       help='suppress all whitespace separation (most compact)')

    options = parser.parse_args()

    if options.compact:
        options.indent = None

    try:
        if options.infile == '-':
            infile = sys.stdin
        else:
            infile = open(options.infile, encoding='utf-8')

        try:
            if options.edn_lines:
                objs = (kim_edn.loads(line) for line in infile)
            else:
                objs = (kim_edn.load(infile), )
        finally:
            if infile is not sys.stdin:
                infile.close()

        if options.outfile is None:
            outfile = sys.stdout
        else:
            outfile = open(options.outfile, 'w', encoding='utf-8')

        with outfile:
            for obj in objs:
                kim_edn.dump(obj, outfile, sort_keys=options.sort_keys, indent=options.indent)
                outfile.write('\n')

        if outfile is not sys.stdout:
            outfile.close()
    except ValueError as e:
        raise SystemExit(e)


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError as exc:
        sys.exit(exc.errno)
