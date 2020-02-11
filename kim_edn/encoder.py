"""Implementation of KIMEDNEncoder."""
import re

ESCAPE_ASCII = re.compile(r'([\\"]|[^\ -~])')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

for _i in range(0x20):
    ESCAPE_DCT.setdefault(chr(_i), '\\u{0:04x}'.format(_i))
del(_i)

INFINITY = float('inf')


def encode_basestring_ascii(s):
    """Return an ASCII-only KIM-EDN representation of a Python string."""
    def replace(match):
        s = match.group(0)
        try:
            return ESCAPE_DCT[s]
        except KeyError:
            n = ord(s)
            if n < 0x10000:
                return '\\u{0:04x}'.format(n)
            else:
                # surrogate pair
                n -= 0x10000
                s1 = 0xd800 | ((n >> 10) & 0x3ff)
                s2 = 0xdc00 | (n & 0x3ff)
                return '\\u{0:04x}\\u{1:04x}'.format(s1, s2)
    return '"' + ESCAPE_ASCII.sub(replace, s) + '"'


class KIMEDNEncoder(object):
    """KIM-EDN encoder (KIMEDNEncoder) for OpenKIM Python data structures.

    Supports the following objects and types by default:
    +-------------------+---------------------------------------------+
    | Python            | KIM-EDN                                     |
    +===================+=============================================+
    | dict              | Maps (or "hash", "dicts", "hashmaps", etc.) |
    +-------------------+---------------------------------------------+
    | list              | Vectors (or "arrays")                       |
    +-------------------+---------------------------------------------+
    | str               | Strings                                     |
    +-------------------+---------------------------------------------+
    | int               | Integers numbers                            |
    +-------------------+---------------------------------------------+
    | float             | Floating point numbers                      |
    +-------------------+---------------------------------------------+
    | True              | true                                        |
    +-------------------+---------------------------------------------+
    | False             | false                                       |
    +-------------------+---------------------------------------------+

    """

    def __init__(self, *, sort_keys=False, indent=None, default=None):
        """KIM-EDN encoder (KIMEDNEncoder) constructor with sensible defaults.

        # NOTE:
        By default it is false (a TypeError) to attempt encoding of keys that
        are not str.

        If sort_keys is true, then the output of dictionaries will be
        sorted by key; this is useful for regression tests to ensure
        that KIM-EDN serializations can be compared on a day-to-day basis.

        If indent is a non-negative integer, then KIM-EDN array elements and
        object members will be pretty-printed with that indent level.
        An indent level of 0 will only insert newlines.
        None is the most compact representation.

        If specified, default is a function that gets called for objects that
        can't otherwise be serialized. It should return a KIM-EDN encodable
        version of the object or raise a ``TypeError``.

        """
        self.sort_keys = sort_keys
        self.indent = indent
        if default is not None:
            self.default = default

    def default(self, o):
        """Return a serializable object for ``o`` or raise a ``TypeError``.

        Implement this method in a subclass such that it returns a
        serializable object for ``o``, or calls the base implementation (to
        raise a ``TypeError``).

        For example, to support arbitrary iterators, you could implement
        default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)

                # Let the base class default method raise the TypeError
                return KIMEDNEncoder.default(self, o)

        """
        msg = 'Object of type {} is not '.format(o.__class__.__name__)
        msg += 'KIM-EDN serializable'
        raise TypeError(msg)

    def encode(self, o):
        """Return a KIM-EDN string representation of a Python data structure.

        For example,

        >>> from kim_edn.encoder import KIMEDNEncoder

        >>> KIMEDNEncoder().encode({"instance-id": 1})
        '{"instance-id" 1}'

        >>> KIMEDNEncoder().encode({"basis-atom-coordinates": {"source-value": [0,0,0]}})
        '{"basis-atom-coordinates" {"source-value" [0 0 0]}}'

        >>> KIMEDNEncoder().encode({"foo": ["bar", "baz"]})
        '{"foo" ["bar" "baz"]}'

        """
        # This is for extremely simple cases and benchmarks.
        if isinstance(o, str):
            return encode_basestring_ascii(o)

        # This doesn't pass the iterator directly to ''.join() because the
        # exceptions aren't as detailed.  The list call should be roughly
        # equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(o)

        if not isinstance(chunks, list):
            chunks = list(chunks)

        return ''.join(chunks)

    def iterencode(self, o):
        """Encode the given object.

        Encode the given object and yield each string representation as
        available. For example,

        >>> for chunk in KIMEDNEncoder().iterencode(({"foo": ["bar", "baz"]})):
        >>>     print(chunk)
        {
        "foo"

        ["bar"
         "baz"
        ]
        }

        """
        markers = {}

        def floatstr(o, _repr=float.__repr__):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o or o == INFINITY or o == -INFINITY:
                raise ValueError(
                    "Out of range float values are not KIM-EDN compliant: " + repr(o))
            else:
                return _repr(o)

        _iterencode = _make_iterencode(markers,
                                       self.default,
                                       encode_basestring_ascii,
                                       self.indent,
                                       floatstr,
                                       self.sort_keys)

        return _iterencode(o, 0)


def _make_iterencode(markers, _default, _encoder, _indent, _floatstr, _sort_keys,
                     # HACK: hand-optimized bytecode; turn globals into locals
                     ValueError=ValueError,
                     dict=dict,
                     list=list,
                     tuple=tuple,
                     float=float,
                     int=int,
                     str=str,
                     id=id,
                     isinstance=isinstance,
                     _intstr=int.__repr__,
                     ):
    item_separator = ' '
    key_separator = ' '

    if _indent is not None and not isinstance(_indent, str):
        _indent = ' ' * _indent

    # Vectors (or "arrays") is a subset of KIM-EDN allowed is the KIM infrastructure
    def _iterencode_vect(vct, _current_indent_level):
        if not vct:
            yield '[]'
            return

        if markers is not None:
            markerid = id(vct)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = vct

        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            separator = item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = item_separator

        first = True
        for value in vct:
            if first:
                first = False
            else:
                buf = separator

            if isinstance(value, str):
                yield buf + _encoder(value)
            elif value is True:
                yield buf + 'true'
            elif value is False:
                yield buf + 'false'
            elif isinstance(value, int):
                # Subclasses of int/float may override __repr__, but we still
                # want to encode them as integers/floats in EDN. One example
                # within the standard library is IntEnum.
                yield buf + _intstr(value)
            elif isinstance(value, float):
                # see comment above for int
                yield buf + _floatstr(value)
            else:
                yield buf

                if isinstance(value, list):
                    chunks = _iterencode_vect(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)
                yield from chunks

        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + _indent * _current_indent_level

        yield ']'

        if markers is not None:
            del markers[markerid]

    def _iterencode_dict(dct, _current_indent_level):
        if not dct:
            yield '{}'
            return

        if markers is not None:
            markerid = id(dct)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = dct

        yield '{'

        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            separator = item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            separator = item_separator

        first = True
        if _sort_keys:
            items = sorted(dct.items())
        else:
            items = dct.items()

        for key, value in items:
            if isinstance(key, str):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elif isinstance(key, float):
                # see comment for int/float in _make_iterencode
                key = _floatstr(key)
            elif key is True:
                key = 'true'
            elif key is False:
                key = 'false'
            elif isinstance(key, int):
                # see comment for int/float in _make_iterencode
                key = _intstr(key)
            else:
                raise TypeError(f'keys must be str, int, float, or bool, '
                                f'not {key.__class__.__name__}')

            if first:
                first = False
            else:
                yield separator

            yield _encoder(key)

            yield key_separator

            if isinstance(value, str):
                yield _encoder(value)
            elif value is True:
                yield 'true'
            elif value is False:
                yield 'false'
            elif isinstance(value, int):
                # see comment for int/float in _make_iterencode
                yield _intstr(value)
            elif isinstance(value, float):
                # see comment for int/float in _make_iterencode
                yield _floatstr(value)
            else:
                if isinstance(value, list):
                    chunks = _iterencode_vect(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level)

                yield from chunks

        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + _indent * _current_indent_level

        yield '}'

        if markers is not None:
            del markers[markerid]

    def _iterencode(o, _current_indent_level):
        if isinstance(o, str):
            yield _encoder(o)
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, int):
            # see comment for int/float in _make_iterencode
            yield _intstr(o)
        elif isinstance(o, float):
            # see comment for int/float in _make_iterencode
            yield _floatstr(o)
        elif isinstance(o, list):
            yield from _iterencode_vect(o, _current_indent_level)
        elif isinstance(o, dict):
            yield from _iterencode_dict(o, _current_indent_level)
        else:
            if markers is not None:
                markerid = id(o)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o

            o = _default(o)

            yield from _iterencode(o, _current_indent_level)

            if markers is not None:
                del markers[markerid]

    return _iterencode
