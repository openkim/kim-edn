r"""KIM-EDN Object Notation.

KIM-EDN object notation <https://openkim.org/doc/schema/edn-format/> is a
subset of EDN syntax <https://github.com/edn-format/edn> used as a standard
data format in the KIM infrastructure <https://openkim.org/>.

:mod:`kim_edn` exposes an API familiar to users of the standard library.

Encoding basic Python object hierarchies::

    >>> import kim_edn
    >>> kim_edn.dumps(["short-name", {"source-value": ["hcp"]}])
    '["short-name" {"source-value" ["hcp"]}]'

    >>> print(kim_edn.dumps("\"P6_3/mmc"))
    "\"P6_3/mmc"

    >>> print(kim_edn.dumps('\\'))
    "\\"

    >>> print(kim_edn.dumps({"domain": "openkim.org", "data-method": "computation", "author": "John Doe"}, sort_keys=True))
    {"author" "John Doe" "data-method" "computation" "domain" "openkim.org"}

    >>> from io import StringIO
    >>> io = StringIO()
    >>> kim_edn.dump(['openkim.org'], io)
    >>> io.getvalue()
    '["openkim.org"]'

Pretty printing::

    >>> import kim_edn
    >>> print(kim_edn.dumps({"domain": "openkim.org", "data-method": "computation", "author": "John Doe"}, sort_keys=True, indent=4))
    {
        "author" "John Doe"
        "data-method" "computation"
        "domain" "openkim.org"
    }

Decoding KIM-EDN::

    >>> import kim_edn
    >>> obj = ["a", {"source-value": 6.9790981921, "source-unit": "angstrom"}]
    >>> kim_edn.loads('["a", {"source-value": 6.9790981921, "source-unit": "angstrom"}]') == obj
    True
    >>> kim_edn.load('["a", {"source-value": 6.9790981921, "source-unit": "angstrom"}]') == obj
    True
    >>> kim_edn.loads('"\\"foo\\bar"') == '"foo\x08ar'
    True
    >>> kim_edn.load(kim_edn.dumps(obj)) == obj
    True
    >>> from io import StringIO
    >>> io = StringIO('["openkim.org"]')
    >>> kim_edn.load(io)[0] == 'openkim.org'
    True

Decoding Commented KIM-EDN::
    >>> obj = {"property-id": "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass"}
    >>> c_str = '{\n  ; property-id\n  "property-id"           "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass" ; property id containing the unique ID of the property.\n }'
    >>> kim_edn.load(c_str) == obj
    True

Specializing KIM-EDN object decoding::

    >>> import kim_edn
    >>> def as_complex(dct):
    ...     if '__complex__' in dct:
    ...         return complex(dct['real'], dct['imag'])
    ...     return dct
    ...
    >>> kim_edn.loads('{"__complex__": true, "real": 1, "imag": 2}',
    ...     object_hook=as_complex)
    (1+2j)
    >>> from decimal import Decimal
    >>> kim_edn.loads('1.1', parse_float=Decimal) == Decimal('1.1')
    True

Specializing KIM-EDN object encoding::

    >>> import kim_edn
    >>> def encode_complex(obj):
    ...     if isinstance(obj, complex):
    ...         return [obj.real, obj.imag]
    ...     msg = 'Object of type {} is not '.format(obj.__class__.__name__)
    ...     msg += 'KIM-EDN serializable'
    ...     raise TypeError(msg)
    ...
    >>> kim_edn.dumps(2 + 1j, default=encode_complex)
    '[2.0 1.0]'
    >>> kim_edn.KIMEDNEncoder(default=encode_complex).encode(2 + 1j)
    '[2.0 1.0]'
    >>> ''.join(kim_edn.KIMEDNEncoder(default=encode_complex).iterencode(2 + 1j))
    '[2.0 1.0]'

Using kim_edn.tool from the shell to validate and pretty-print::

    $ echo '{"kim_edn" "obj"}' | python -m kim_edn.tool
    {
        "kim_edn" "obj"
    }

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

    $ echo '{"property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-potential-energy-hexagonal-crystal" "instance-id" 1 "space-group" {"source-value" "P6_3/mmc"} "basis-atom-coordinates" {"source-value" [[0, 0, 0][0.5, 0, 0.5]]}}' | python -m kim_edn.tool
    {
        "property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-potential-energy-hexagonal-crystal"
        "instance-id" 1
        "space-group" {
            "source-value" "P6_3/mmc"
        }
        "basis-atom-coordinates" {
            "source-value" [
                [
                    0
                    0
                    0
                ]
                [
                    0.5
                    0
                    0.5
                ]
            ]
        }
    }

"""

"""
Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019 Python Software Foundation;
All Rights Reserved
"""

import codecs
from .encoder import KIMEDNEncoder
from .decoder import KIMEDNDecoder, KIMEDNDecodeError

__all__ = [
    'dump',
    'dumps',
    'load',
    'loads',
    'KIMEDNDecoder',
    'KIMEDNDecodeError',
    'KIMEDNEncoder',
]

__author__ = 'Bob Ippolito <bob@redivi.com> Yaser Afshar <yafshar@umn.edu>'


_default_encoder = KIMEDNEncoder()


def dump(obj, fp, *, cls=None, indent=None, default=None, sort_keys=False):
    r"""Serialize ``obj``.

    Serialize ``obj`` as a KIM-EDN formatted stream to ``fp`` (a ``.write()``
    -supporting file-like object or a name string to open a file).

    By default ``dict`` keys that are not basic types (``str``, ``int``,
    ``float``, ``bool``) will be raising a ``TypeError``.

    If ``indent`` is a non-negative integer, then EDN array elements and object
    members will be pretty-printed with that indent level. An indent level of 0
    will only insert newlines.

    ``default(obj)`` is a function that should return a serializable version of
    obj or raise TypeError. The default simply raises TypeError.

    If *sort_keys* is true (default: ``False``), then the output of dictionaries
    will be sorted by key.

    To use a custom ``KIMEDNEncoder`` subclass (e.g. one that overrides the
    ``.default()`` method to serialize additional types), specify it with
    the ``cls`` kwarg; otherwise ``KIMEDNEncoder`` is used.

    """
    # cached encoder
    if (cls is None
        and indent is None
        and default is None
            and not sort_keys):
        iterable = _default_encoder.iterencode(obj)
    else:
        if cls is None:
            cls = KIMEDNEncoder

        iterable = cls(indent=indent,
                       default=default,
                       sort_keys=sort_keys).iterencode(obj)

    if isinstance(fp, str):
        # See if this is a file name
        with open(fp, 'w') as fo:
            for chunk in iterable:
                fo.write(chunk)
            fo.write("\n")
    else:
        # could accelerate with writelines in some versions
        # of Python, at a debuggability cost
        for chunk in iterable:
            fp.write(chunk)
        fp.write("\n")


def dumps(obj, *, cls=None, indent=None, default=None, sort_keys=False):
    r"""Serialize ``obj`` to a KIM-EDN formatted ``str``.

    By default ``dict`` keys that are not basic types (``str``, ``int``,
    ``float``, ``bool``) will be raising a ``TypeError``.

    If ``indent`` is a non-negative integer, then KIM-EDN array elements and
    object members will be pretty-printed with that indent level. An indent
    level of 0 will only insert newlines.

    ``default(obj)`` is a function that should return a serializable version of
    obj or raise TypeError. The default simply raises TypeError.

    If *sort_keys* is true (default: ``False``), then the output of
    dictionaries will be sorted by key.

    To use a custom ``KIMEDNEncoder`` subclass (e.g. one that overrides the
    ``.default()`` method to serialize additional types), specify it with the
    ``cls`` kwarg; otherwise ``KIMEDNEncoder`` is used.

    """
    # cached encoder
    if (cls is None
        and indent is None
        and default is None and
            not sort_keys):
        return _default_encoder.encode(obj)

    if cls is None:
        cls = KIMEDNEncoder

    return cls(indent=indent,
               default=default,
               sort_keys=sort_keys).encode(obj)


_default_decoder = KIMEDNDecoder()


def detect_encoding(b):
    bstartswith = b.startswith

    if bstartswith((codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE)):
        return 'utf-32'

    if bstartswith((codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE)):
        return 'utf-16'

    if bstartswith(codecs.BOM_UTF8):
        return 'utf-8-sig'

    if len(b) >= 4:
        if not b[0]:
            # 00 00 -- -- - utf-32-be
            # 00 XX -- -- - utf-16-be
            return 'utf-16-be' if b[1] else 'utf-32-be'
        if not b[1]:
            # XX 00 00 00 - utf-32-le
            # XX 00 00 XX - utf-16-le
            # XX 00 XX -- - utf-16-le
            return 'utf-16-le' if b[2] or b[3] else 'utf-32-le'
    elif len(b) == 2:
        if not b[0]:
            # 00 XX - utf-16-be
            return 'utf-16-be'
        if not b[1]:
            # XX 00 - utf-16-le
            return 'utf-16-le'

    # default
    return 'utf-8'


def load(fp, *, cls=None, parse_float=None, parse_int=None, parse_constant=None,
         object_hook=None, object_pairs_hook=None):
    r"""Deserialize ``fp``.

    Deserialize ``fp`` (a ``.read()``-supporting file-like object, or a name
    string to a file containing a KIM-EDN document or a valid KIM-EDN
    formatted string) to a Python object.

    ``object_hook`` is an optional function that will be called with the
    result of any object literal decode (a ``dict``). The return value of
    ``object_hook`` will be used instead of the ``dict``. This feature
    can be used to implement custom decoders.

    ``object_pairs_hook`` is an optional function that will be called with the
    result of any object literal decoded with an ordered list of pairs.  The
    return value of ``object_pairs_hook`` will be used instead of the ``dict``.
    This feature can be used to implement custom decoders.  If ``object_hook``
    is also defined, the ``object_pairs_hook`` takes priority.

    To use a custom ``KIMEDNDecoder`` subclass, specify it with the ``cls``
    kwarg; otherwise ``KIMEDNDecoder`` is used.

    """
    if isinstance(fp, str):
        try:
            # See if this is a file name
            with open(fp) as fo:
                s = fo.read()
        except IOError:
            # Assume it's a valid KIM-EDN formatted string
            s = fp
    else:
        s = fp.read()

    return loads(s,
                 cls=cls,
                 parse_float=parse_float,
                 parse_int=parse_int,
                 parse_constant=parse_constant,
                 object_hook=object_hook,
                 object_pairs_hook=object_pairs_hook)


def loads(s, *, cls=None, parse_float=None, parse_int=None,
          parse_constant=None, object_hook=None, object_pairs_hook=None):
    r"""Deserialize ``s``.

    Deserialize ``s`` (a ``str``, ``bytes`` or ``bytearray`` instance
    containing a KIM-EDN document) to a Python object.

    ``object_hook`` is an optional function that will be called with the
    result of any object literal decode (a ``dict``). The return value of
    ``object_hook`` will be used instead of the ``dict``. This feature
    can be used to implement custom decoders.

    ``object_pairs_hook`` is an optional function that will be called with the
    result of any object literal decoded with an ordered list of pairs.  The
    return value of ``object_pairs_hook`` will be used instead of the ``dict``.
    This feature can be used to implement custom decoders.  If ``object_hook``
    is also defined, the ``object_pairs_hook`` takes priority.

    ``parse_float``, if specified, will be called with the string
    of every EDN float to be decoded. By default this is equivalent to
    float(num_str). This can be used to use another datatype or parser
    for EDN floats (e.g. decimal.Decimal).

    ``parse_int``, if specified, will be called with the string
    of every EDN int to be decoded. By default this is equivalent to
    int(num_str). This can be used to use another datatype or parser
    for EDN integers (e.g. float).

    ``parse_constant``, if specified, will be called with one of the
    following strings: -Infinity, Infinity, NaN.
    This can be used to raise an exception if invalid EDN numbers
    are encountered.

    To use a custom ``KIMEDNDecoder`` subclass, specify it with the ``cls``
    kwarg; otherwise ``KIMEDNDecoder`` is used.

    """
    if isinstance(s, str):
        if s.startswith('\ufeff'):
            msg = 'Unexpected UTF-8 BOM (decode using utf-8-sig)'
            raise KIMEDNDecodeError(msg, s, 0)
    else:
        if not isinstance(s, (bytes, bytearray)):
            msg = 'the EDN object must be str, bytes or bytearray, '
            msg += 'not {}'.format(s.__class__.__name__)
            raise TypeError(msg)

        s = s.decode(detect_encoding(s), 'surrogatepass')

    if (cls is None
        and parse_float is None
        and parse_int is None
        and parse_constant is None
        and object_hook is None and
            object_pairs_hook is None):
        return _default_decoder.decode(s)

    if cls is None:
        cls = KIMEDNDecoder

    kw = {}
    if parse_float is not None:
        kw['parse_float'] = parse_float

    if parse_int is not None:
        kw['parse_int'] = parse_int

    if parse_constant is not None:
        kw['parse_constant'] = parse_constant

    if object_hook is not None:
        kw['object_hook'] = object_hook

    if object_pairs_hook is not None:
        kw['object_pairs_hook'] = object_pairs_hook

    return cls(**kw).decode(s)


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
