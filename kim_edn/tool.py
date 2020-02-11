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
                        type=argparse.FileType(encoding="utf-8"),
                        help='a KIM-EDN file to be validated or pretty-printed',
                        default=sys.stdin)

    parser.add_argument('outfile', nargs='?',
                        type=argparse.FileType('w', encoding="utf-8"),
                        help='write the output of infile to outfile',
                        default=sys.stdout)

    parser.add_argument('--sort-keys', action='store_true', default=False,
                        help='sort the output of dictionaries alphabetically by key')

    parser.add_argument('--edn-lines', action='store_true', default=False,
                        help='parse input using the kim_edn lines format')

    options = parser.parse_args()

    with options.infile as infile, options.outfile as outfile:
        try:
            if options.edn_lines:
                objs = (kim_edn.loads(line) for line in infile)
            else:
                objs = (kim_edn.load(infile), )

            for obj in objs:
                kim_edn.dump(obj, outfile, sort_keys=options.sort_keys,
                             indent=4)
                outfile.write('\n')
        except ValueError as e:
            raise SystemExit(e)


if __name__ == '__main__':
    main()
