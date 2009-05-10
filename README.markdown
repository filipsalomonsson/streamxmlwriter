Streamxmlwriter
===============

Streamxmlwriter is a simple python library for writing XML files. It
is very similar to the SimpleXMLWriter that is included in Fredrik
Lundh's ElementTree package, but also supports pretty-printing and
custom element attribute ordering.


Usage example
-------------

    >>> from cStringIO import StringIO
    >>> output = StringIO()

    >>> from streamxmlwriter import XMLWriter
    >>> writer = XMLWriter(output)
    >>> writer.start("foo", one="1", two="2")
    >>> writer.data("something")
    >>> writer.start("bar")
    >>> writer.close()
    
    >>> print output.getvalue()
    <foo one="1" two="2">something<bar /></foo>
    

The API
-------

### writer = XMLWriter(file, encoding="utf-8", pretty_print=False, sort=True)

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

### writer.start(tag, attributes=None, **kwargs)
opens an element whose tag is `tag`. To specify attributes, you can
pass it a dictionary as the second argument. In most cases, it's
easier to specify each attribute as a keyword argument.

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

### writer.close()
Closes all open elements.


Attribute ordering
------------------

For more control over attribute ordering, you can pass a dictionary to
the constructor's `sort` argument. In that dictionary:

* each key is a tag name, and
* each corresponding value is a list of attribute names in the order
  you want them to occur in the XML data for that tag.

You can use `None` as a tag name to specify a default order for all
tags that don't have specific entries. A `None` value in the list of
attribute names can be used as a place marker for all attributes whose
names are not in the list; by default, they will be placed last.


Todo
----

* Avoid multiple XML declarations
* Make namespace support solid
* C14N?
* Additional safeguards against generating bad XML?


License
-------

Copyright (c) 2009 Filip Salomonsson

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