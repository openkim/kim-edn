"""Implementation of KIMEDNDecoder."""
import re

from kim_edn import scanner

__all__ = ['KIMEDNDecoder', 'KIMEDNDecodeError']


class KIMEDNDecodeError(ValueError):
    """Raise an exception.

    It raises an exception when receives an argument that has the right type
    but an inappropriate value. It is a subclass of ValueError with the
    following additional properties:

    msg: The unformatted error message
    doc: The KIM-EDN document being parsed
    pos: The start index of the doc where parsing failed
    lineno: The line corresponding to pos
    colno: The column corresponding to pos

    """

    def __init__(self, msg, doc, pos):
        """KIM-EDEN KIMEDNDecodeError constuctor."""
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        """Efficient pickling."""
        return self.__class__, (self.msg, self.doc, self.pos)


def _decode_uXXXX(s, pos):
    esc = s[pos + 1:pos + 5]
    if len(esc) == 4 and esc[1] not in 'xX':
        try:
            return int(esc, 16)
        except ValueError:
            pass
    msg = "Invalid \\uXXXX escape"
    raise KIMEDNDecodeError(msg, s, pos)


# VERBOSE     Ignore whitespace and comments for nicer looking RE's.
# MULTILINE   "^" matches the beginning of lines (after a newline)
#             as well as the string.
#             "$" matches the end of lines (before a newline) as well
#             as the end of the string.
# DOTALL      "." matches any character at all, including the newline.
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)
BACKSLASH = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}
# This is an EDN specification escape characters \t, \r, \n
BACKSLASHEXCEPTION = {
    '\n': '\n',
    '\r': '\r',
    '\t': '\t',
}


def py_scanstring(s, end, strict=True, _b=BACKSLASH, _m=STRINGCHUNK.match, _be=BACKSLASHEXCEPTION):
    """Scan the string s for an KIM-EDN string.

    Scan the string s for an KIM-EDN string. End is the index of the
    character in s after the quote that started the KIM-EDN string. Unescapes
    all valid KIM-EDN string escape sequences and raises ValueError on attempt
    to decode an invalid string. If strict is False then literal control
    characters are allowed in the string.

    Returns a tuple of the decoded string and the index of the character in s
    after the end quote.

    """
    chunks = []
    chunks_append = chunks.append

    begin = end - 1

    while True:
        chunk = _m(s, end)
        if chunk is None:
            raise KIMEDNDecodeError(
                "Unterminated string starting at", s, begin)

        end = chunk.end()

        content, terminator = chunk.groups()

        # Content is contains zero or more unescaped string characters
        if content:
            chunks_append(content)

        # Terminator is the end of string, a literal control character,
        # or a backslash denoting that an escape sequence follows
        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                # This is an EDN specification escape characters \t, \r, \n in
                # a string
                if terminator in _be:
                    chunks_append(_be[terminator])
                    continue
                else:
                    msg = "Invalid control character {0!r} at".format(
                        terminator)
                    raise KIMEDNDecodeError(msg, s, end)
            else:
                chunks_append(terminator)
                continue

        try:
            esc = s[end]
        except IndexError:
            raise KIMEDNDecodeError("Unterminated string starting at",
                                    s, begin) from None

        # If not a unicode escape sequence, must be in the lookup table
        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = "Invalid \\escape: {0!r}".format(esc)
                raise KIMEDNDecodeError(msg, s, end)

            end += 1
        else:
            uni = _decode_uXXXX(s, end)
            end += 5
            if 0xd800 <= uni <= 0xdbff and s[end:end + 2] == '\\u':
                uni2 = _decode_uXXXX(s, end + 1)
                if 0xdc00 <= uni2 <= 0xdfff:
                    uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
                    end += 6

            char = chr(uni)

        chunks_append(char)

    return ''.join(chunks), end


WHITESPACE = re.compile(r'[, \t\n\r]*', FLAGS)
WHITESPACE_STR = ', \t\n\r'

# A ';' character encountered outside of a string indicates
# the start of a comment.
STRIP_COMMENT = re.compile(r'[;][^\n]*')


def KIMEDNObject(s_and_end, strict, scan_once, object_hook, object_pairs_hook,
                 memo=None, _w=WHITESPACE.match, _ws=WHITESPACE_STR,
                 _sc=STRIP_COMMENT.search):
    s, end = s_and_end

    pairs = []
    pairs_append = pairs.append

    # Backwards compatibility
    if memo is None:
        memo = {}

    memo_get = memo.setdefault

    # Use a slice to prevent IndexError from being raised, the following
    # check will raise a more specific ValueError if the string is empty
    nextchar = s[end:end + 1]

    # Normally we expect nextchar == '"'
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end:end + 1]

        while nextchar == ';':
            end += _sc(s[end:]).end()
            end = _w(s, end).end()
            nextchar = s[end:end + 1]

        # Trivial empty object
        if nextchar == '}':
            if object_pairs_hook is not None:
                result = object_pairs_hook(pairs)
                return result, end + 1

            pairs = {}
            if object_hook is not None:
                pairs = object_hook(pairs)

            return pairs, end + 1
        elif nextchar != '"':
            raise KIMEDNDecodeError("Expecting property name enclosed in "
                                    "double quotes", s, end)

    end += 1
    while True:
        key, end = py_scanstring(s, end, strict)
        key = memo_get(key, key)

        # This is to address cases where we have "  : " or similar pattern
        if s[end:end + 1] in _ws:
            end = _w(s, end).end()
            # If we remove the extra space and the next character is not ":"
            # then we should move the index one behind
            if s[end:end + 1] != ':':
                end -= 1

        end += 1

        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            raise KIMEDNDecodeError("Expecting value", s, err.value) from None

        pairs_append((key, value))

        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ''

        while nextchar == ';':
            end += _sc(s[end:]).end()
            end = _w(s, end).end()
            nextchar = s[end:end + 1]

        end += 1

        if nextchar == '}':
            break
        elif nextchar == '"':
            end = _w(s, end).end()
            continue
        else:
            raise KIMEDNDecodeError("Expecting property name enclosed in "
                                    "double quotes", s, end - 1)

    if object_pairs_hook is not None:
        result = object_pairs_hook(pairs)
        return result, end

    pairs = dict(pairs)

    if object_hook is not None:
        pairs = object_hook(pairs)

    return pairs, end


def KIMEDNArray(s_and_end, scan_once, _w=WHITESPACE.match,
                _ws=WHITESPACE_STR, _sc=STRIP_COMMENT.search):
    s, end = s_and_end

    values = []
    values_append = values.append

    nextchar = s[end:end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:end + 1]

    while nextchar == ';':
        end += _sc(s[end:]).end()
        end = _w(s, end).end()
        nextchar = s[end:end + 1]

    # Look-ahead for trivial empty array
    if nextchar == ']':
        return values, end + 1

    while True:
        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            raise KIMEDNDecodeError("Expecting value", s, err.value) from None

        values_append(value)

        nextchar = s[end:end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:end + 1]

        while nextchar == ';':
            end += _sc(s[end:]).end()
            end = _w(s, end).end()
            nextchar = s[end:end + 1]

        if nextchar == ']':
            end += 1
            break
        elif nextchar == '[':
            continue

        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

    return values, end


class KIMEDNDecoder(object):
    """A KIM-EDN decoder (KIMEDNDecoder) object.

    Performs the following translations in decoding by default:
    +-------------------------------+----------+
    | KIM-EDN                       | Python   |
    +===============================+==========+
    | Object                        | dict     |
    +-------------------------------+----------+
    | Vectors (or "arrays")         | list     |
    +-------------------------------+----------+
    | Strings                       | str      |
    +-------------------------------+----------+
    | Integers numbers (int)        | int      |
    +-------------------------------+----------+
    | Floating point numbers (real) | float    |
    +-------------------------------+----------+
    | true                          | True     |
    +-------------------------------+----------+
    | false                         | False    |
    +-------------------------------+----------+

    """

    def __init__(self, *, parse_float=None, parse_int=None, strict=True,
                 object_hook=None, object_pairs_hook=None):
        r"""KIM-EDN decoder (KIMEDNDecoder) constructor.

        ``parse_float``, if specified, will be called with the string of every
        KIM-EDN float to be decoded. By default this is equivalent to
        float(num_str). This can be used to use another datatype or parser for
        KIM-EDN floats (e.g. decimal.Decimal).

        ``parse_int``, if specified, will be called with the string
        of every KIM-EDN int to be decoded. By default this is equivalent to
        int(num_str). This can be used to use another datatype or parser
        for KIM-EDN integers (e.g. float).

        If ``strict`` is false (true is the default), then control characters
        will be allowed inside strings. Control characters in this context are
        those with character codes in the 0-31 range, including ``'\\t'`` (tab),
        ``'\\n'``, ``'\\r'`` and ``'\\0'``.

        ``object_hook``, if specified, will be called with the result of every
        KIM-EDN object decoded and its return value will be used in place of the
        given ``dict``. This can be used to provide custom deserializations.

        ``object_pairs_hook``, if specified will be called with the result of
        every KIM-EDN object decoded with an ordered list of pairs. The return
        value of ``object_pairs_hook`` will be used instead of the ``dict``.
        This feature can be used to implement custom decoders.
        If ``object_hook`` is also defined, the ``object_pairs_hook``
        takes priority.

        """
        self.parse_string = py_scanstring
        self.parse_object = KIMEDNObject
        self.parse_array = KIMEDNArray
        self.parse_float = parse_float or float
        self.parse_int = parse_int or int
        self.strict = strict
        self.object_hook = object_hook
        self.object_pairs_hook = object_pairs_hook
        self.memo = {}

        self.scan_once = scanner.make_scanner(self)

    def decode(self, s, _w=WHITESPACE.match):
        """Return the Python representation of ``s``.

        Return the Python representation of ``s`` (a ``str`` instance
        containing a KIM-EDN document).

        """
        obj, end = self.raw_decode(s, idx=_w(s, 0).end())

        end = _w(s, end).end()
        if end != len(s):
            raise KIMEDNDecodeError("Extra data", s, end)

        return obj

    def raw_decode(self, s, idx=0):
        """Decode an KIM-EDN document from ``s``.

        Decode an KIM-EDN document from ``s`` (a ``str`` beginning with a
        KIM-EDN document) and return a 2-tuple of the Python representation
        and the index in ``s`` where the document ended.

        This can be used to decode a KIM-EDN document from a string that may
        have extraneous data at the end.

        """
        try:
            obj, end = self.scan_once(s, idx)
        except StopIteration as err:
            raise KIMEDNDecodeError("Expecting value", s, err.value) from None

        return obj, end
