# KIM-EDN encoder and decoder

[![Build Status](https://travis-ci.org/yafshar/kim_edn.svg?branch=master)](https://travis-ci.org/yafshar/kim_edn)
[![License](https://img.shields.io/badge/license-CDDL--1.0-blue)](LICENSE)

## edn

Extensible data notation [eed-n]

[**edn**](<https://github.com/edn-format/edn>) is an extensible data notation. A superset of **edn** is used by Clojure to represent programs, and it is used by [**KIM**](https://openkim.org) and other applications as a data format.

## kim_edn

The **KIM** infrastructure embraces a subset of **edn** as a [standard data format](https://openkim.org/doc/schema/edn-format). The primary purpose of this data format choice is to serve as a notational superset to [**JSON**](https://en.wikipedia.org/wiki/JSON) with the enhancements being that it (1) allows for comments and (2) treats commas as whitespace enabling easier templating.

The subset of **EDN** allowed is constrained to:

* [Booleans](https://github.com/edn-format/edn#booleans)
* [Strings](https://github.com/edn-format/edn#strings)
* [Integers](https://github.com/edn-format/edn#integers)
* [Floating point numbers](https://github.com/edn-format/edn#floating-point-numbers)
* [Vectors](https://github.com/edn-format/edn#vectors) (or arrays)
* [Maps](https://github.com/edn-format/edn#maps) (or hash, dicts, hashmaps, etc.)

Exceptions:

* [nil](https://github.com/edn-format/edn#nil) is not allowed, this includes JSON's null which is not allowed. Instead consider:
    1. using an empty string ("") as the value,
    2. using the number 0 as the value,
    3. or omitting a key-value pair.
* [Symbols](https://github.com/edn-format/edn#symbols) are not allowed
* [Keywords](https://github.com/edn-format/edn#keywords) are not allowed
* [Lists](https://github.com/edn-format/edn#lists) are not allowed, please use [vectors](https://github.com/edn-format/edn#vectors) instead
* [Sets](https://github.com/edn-format/edn#sets) are not allowed
* [Tagged elements](https://github.com/edn-format/edn#tagged-elements) are not allowed

`kim_edn` module exposes an API familiar to users of the standard library.

Encoding basic Python object hierarchies::

```py
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
    >>> kim_edn.dump(['streaming API'], io)
    >>> io.getvalue()
    '["streaming API"]'
```

Pretty printing::

```py
    >>> import kim_edn
    >>> print(kim_edn.dumps({"domain": "openkim.org", "data-method": "computation", "author": "John Doe"}, sort_keys=True, indent=4))
    {
        "author" "John Doe"
        "data-method" "computation"
        "domain" "openkim.org"
    }
```

Decoding KIM-EDN::

```py
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
```

Decoding Commented KIM-EDN::

```py
    >>> obj = {"property-id": "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass"}
    >>> c_str = '{\n  ; property-id\n  "property-id"           "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass" ; property id containing the unique ID of the property.\n }'
    >>> kim_edn.load(c_str) == obj
    True
```

Specializing KIM-EDN object decoding::

```py
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
```

Specializing KIM-EDN object encoding::

```py
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
```

Using kim_edn.tool from the shell to validate and pretty-print::

```sh
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
```

## Installation

This package requires Python 3.6 (or newer).

*kim_edn* can be installed with `pip`:

```sh
pip install kim_edn
```

### Note

* Depending on your Python installation, you may need to use `pip3` instead of `pip`.

## References

This module has been adapted and updated from the [python](https://docs.python.org) **json**  module to comply with the [subset of **edn** format used in **KIM**](https://openkim.org/doc/schema/edn-format).

## Copyright

Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019 Python Software Foundation;
All Rights Reserved

Copyright (c) 2019, Regents of the University of Minnesota.\
All Rights Reserved

## Contributing

Contributors:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Yaser Afshar
