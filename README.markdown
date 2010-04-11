Streamxmlwriter
===============

Streamxmlwriter is a simple python library for writing XML files.

It allows you to generate XML documents without building the whole
document tree in memory first, which means you can generate
arbitrarily large documents with a very small memory footprint.

Its features include pretty-printing and custom ordering of element
attributes.


Usage example
-------------

    >>> from cStringIO import StringIO
    >>> output = StringIO()

    >>> from streamxmlwriter import XMLWriter
    >>> writer = XMLWriter(output, pretty_print=True)

    >>> writer.start_ns("a", "http://example.org/ns")
    >>> writer.start("foo", {"{http://example.org/ns}one": "1"}, two="2")
    >>> writer.start("bar")
    >>> writer.data("something")
    >>> writer.end("bar")
    >>> writer.comment("hello")
    >>> writer.element("{http://example.org/ns}baz", data="whatnot", x="y")
    >>> writer.start("empty")
    >>> writer.close()

    >>> print output.getvalue()
    <foo xmlns:a="http://example.org/ns" two="2" a:one="1">
      <bar>something</bar>
      <!--hello-->
      <a:baz x="y">whatnot</a:baz>
      <empty />
    </foo>


The API
-------

### writer = XMLWriter(file, encoding="utf-8", pretty_print=False, sort=True, abbrev_empty=True)
creates a new writer instance that writes its output to the file-like
object you pass as the first argument. There are a few optional
arguments as well:

* `encoding` specifies the character encoding for the XML output.
  Default: `"utf-8"`.
* If `pretty_print` is `True`, the XML output will be pretty-printed
  (indented). Default: `False`.
* If `sort` is `True`, every element's attributes will be
  lexicographically sorted by name. See "Attribute ordering" below for
  more advanced options. Default: `True`.
* If `abbrev_empty` is False, empty elements are serialized as a
  start-end tag pair (`<foo></foo>`), instead of the shorter form
  (`<foo />`). Default: `True`.

### writer.start(tag, attributes=None, nsmap=None, **kwargs)
opens an element whose tag is `tag`. To specify attributes, you can
pass it a dictionary as the second argument. In most cases, it's
easier to specify each attribute as a keyword argument.

`nsmap` is an optional dictionary, mapping namespace prefixes to URIs.
This is used automatically if you serialize `Element` instances from
lxml using the `element` method.

### writer.end(tag)
closes the most recently opened element. If you pass it a `tag` that
doesn't match the open element, the writer raises an `XMLSyntaxError`.
If you don't pass any tag at all, the current element is closed.

### writer.data(data)
writes character data to the output file, properly encoded.

### writer.element(element, attributes=None, data=None, **kwargs)
writes a complete element. `element("foo", bar="baz", data="hello!")`
is exactly the same as calling `start("foo", bar="baz")`,
`data("hello!")` and `end("foo")`.

If `element` is an Element instance, the whole element will be
serialized, including children.

### writer.declaration()
outputs an XML declaration. If the character encoding is not
`us-ascii` or `utf-8`, it is called automatically by the constructor.
Does nothing if a declaration has already been written. Raises
`XMLSyntaxError` if XML element data has already been written.

### writer.comment(data)
outputs an XML comment.

### writer.pi(target, data)
outputs an XML processing instruction.

### writer.start_ns(prefix, uri)
adds a namespace prefix mapping to be included in the next start tag.

### writer.end_ns()
does nothing (namespace scope is handled automatically).

### writer.iterwrite(events)
writes XML data based on (event, elem) tuples of the kind that you get
from `iterparse` in ElementTree and lxml. `start`, `end`, `start-ns`,
`end-ns`, `comment` and `pi` events are currently supported. Note that
the `events` iterable *must* include `start` events, since the
document structure can't be inferred from `end` elements alone.

### writer.close()
Closes all open elements.


Attribute ordering
------------------

For more control over attribute ordering, you can pass a dictionary to
the constructor's `sort` argument. In that dictionary:

* each key is a tag name, and
* each corresponding value is a list of attribute names in the order
  you want them to occur in the XML data for that tag.

If `None` appears in the list, it acts as a wildcard for all
attributes not explicitly named in the list. (By default, they will be
placed last.)

Example::

    attrib_order = {
        "person": ["id", "first_name", "last_name"],
        "foo": ["id", None, "put_me_last"],
    }



License
-------

Copyright (c) 2009-2010 Filip Salomonsson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

(That's the MIT license.)