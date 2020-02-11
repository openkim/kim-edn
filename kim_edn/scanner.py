"""KIM-EDN token scanner."""
import re

__all__ = ['make_scanner']

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
NUMBER_RE = re.compile(r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?', FLAGS)

# A ';' character encountered outside of a string indicates
# the start of a comment.
STRIP_COMMENT = re.compile(r'[;][^\n]*')
WHITESPACE = re.compile(r'[, \t\n\r]*', FLAGS)


def make_scanner(context):
    """Create KIM-EDN scanner."""
    parse_string = context.parse_string
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_float = context.parse_float
    parse_int = context.parse_int
    strict = context.strict
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    match_number = NUMBER_RE.match

    def _scan_once(string, idx, _w=WHITESPACE.match,
                   _sc=STRIP_COMMENT.search):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx) from None

        if nextchar == '"':
            return parse_string(string,
                                idx + 1,
                                strict)
        elif nextchar == '{':
            return parse_object((string, idx + 1),
                                strict,
                                _scan_once,
                                object_hook,
                                object_pairs_hook,
                                memo)
        elif nextchar == '[':
            return parse_array((string, idx + 1), _scan_once)
        elif nextchar == 't' and string[idx:idx + 4] == 'true':
            return True, idx + 4
        elif nextchar == 'f' and string[idx:idx + 5] == 'false':
            return False, idx + 5
        elif nextchar == ';':
            while nextchar == ';':
                idx += _sc(string[idx:]).end()
                idx = _w(string, idx).end()
                nextchar = string[idx:idx + 1]
            return _scan_once(string, idx)

        m = match_number(string, idx)
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or '') + (exp or ''))
            else:
                res = parse_int(integer)
            return res, m.end()
        else:
            raise StopIteration(idx)

    def scan_once(string, idx):
        try:
            return _scan_once(string, idx)
        finally:
            memo.clear()

    return scan_once
