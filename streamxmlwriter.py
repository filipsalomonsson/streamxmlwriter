#!/usr/bin/env python
"""
streamxmlwriter - A simple library for incrementally writing XML
files of arbitrary size. Supports pretty-printing and custom attribute
ordering. Experimental namespace support.

In development; poor documentation and tests; may eat your children.
The latest development version is available from the git repository [1].

[1] http://github.com/infixfilip/streamxmlwriter/tree/master

Comments and/or patches are always welcome.
"""
# Copyright (c) 2009 Filip Salomonsson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Filip Salomonsson <filip.salomonsson@gmail.com>"
__version__ = "0.3"


INDENT = "  "


def escape_attribute(value, encoding):
    """Escape an attribute value using the given encoding."""
    if "&" in value:
        value = value.replace("&", "&amp;")
    if "<" in value:
        value = value.replace("<", "&lt;")
    if "\"" in value:
        value = value.replace("\"", "&quot;")
    return value.encode(encoding, "xmlcharrefreplace")


def escape_cdata(data, encoding):
    """Escape character data using the given encoding."""
    if "&" in data:
        data = data.replace("&", "&amp;")
    if "<" in data:
        data = data.replace("<", "&lt;")
    if ">" in data:
        data = data.replace(">", "&gt;")
    return data.encode(encoding, "xmlcharrefreplace")


def sorter_factory(attrib_order):
    """Return a function that sorts a list of (key, value) pairs.

    The sort order is determined by the `attrib_order` dictionary,
    whose format is described in the documentation for the `XMLWriter`
    class.

    """
    for tag, names in attrib_order.iteritems():
        attrib_order[tag] = dict((name, n) for (n, name) in enumerate(names))
    for tag, order in attrib_order.iteritems():
        order[None] = len(order)

    def asort(pairs, tag):
        """Sort a list of ``(key, value)`` pairs), using the custom
        sort order for the given `tag` name."""
        def key(a):
            # Sort key
            name, value = a
            if tag not in attrib_order:
                return name
            keys = attrib_order[tag]
            if name in keys:
                return keys[name], name
            else:
                return keys[None], name
        return sorted(pairs, key=key)
    return asort


def tostring(element, *args, **kwargs):
    """Serialize an element to its string representation using an
    `XMLWriter`.

    `element` is an Element instance. All additional positional and
    keyword arguments are passed on to the underlying `XMLWriter`.

    """
    import cStringIO
    out = cStringIO.StringIO()
    writer = XMLWriter(out, *args, **kwargs)
    writer.element(element)
    writer.close()
    return out.getvalue()


class XMLSyntaxError(Exception):
    """XML syntactic errors, such as ill-nestedness."""


class XMLWriter(object):
    """Stream XML writer"""
    def __init__(self, file, encoding="utf-8",
                 nsmap={}, default_namespace=None,
                 pretty_print=False, sort=True):
        """
        Create an `XMLWriter` that writes its output to `file`.

        `encoding` is the output encoding (default: utf-8). If
        `pretty_print` is true, the output will be written in indented.
        form.

        If `sort` is true (which is the default), attributes will be
        sorted alphabetically.

        Optionally, `sort` can be a dictionary specifying a custom
        sort order for attributes. The dictionary keys are tag names,
        and each value is a list of attribute names in the order they
        should appear when sorted. If `None` appears in the list, it
        acts as a wildcard for all attributes not explicitly named in
        the list. (By default, they will be placed last.)

        Example::

        attrib_order = {
            "person": ["id", "first_name", "last_name"],
            "foo": ["id", None, "put_me_last"],
        }

        """
        self.write = file.write
        self.encoding = encoding
        self._pretty_print = pretty_print
        self._sort = sort
        if isinstance(sort, dict):
            self._sort = sorter_factory(sort)
        self._tags = []
        self._start_tag_open = False
        nsmap = nsmap.copy()
        if default_namespace:
            nsmap[default_namespace] = ""
        self._namespace_maps = [nsmap]
        self._new_namespaces = nsmap.items()
        if self.encoding not in ("us-ascii", "utf-8"):
            self.declaration()

    def _cname(self, name):
        # Return a cname from its {ns}tag form
        if name[0] == "{":
            uri, name = name[1:].split("}", 1)
            nsmap = self._namespace_maps[-1]
            if uri not in nsmap:
                prefix = "ns" + str(len(nsmap)+1)
                self.start_ns(prefix, uri)
            else:
                prefix = nsmap[uri]
            if prefix:
                name = prefix + ":" + name
        return name

    def start(self, tag, attributes=None, nsmap={}, **kwargs):
        """Open a new `tag` element.

        Attributes can be given as a dictionary (`attributes`), or as
        keyword arguments.

        """
        if self._start_tag_open:
            self.write(">")
            self._start_tag_open = False
        if self._pretty_print and self._tags and not self._wrote_data:
            self.write("\n" + INDENT * len(self._tags))
        # Generate start-ns events for all new namespaces
        for (prefix, uri) in nsmap.iteritems():
            if self._namespace_maps[-1].get(uri) != prefix:
                self.start_ns(prefix, uri)
        tag = self._cname(tag)
        self.write("<" + tag)
        # Write attributes, including namespace declarations
        # TODO: Handle ns declarations separately
        if attributes or kwargs or self._new_namespaces:
            if attributes is None:
                attributes={}
            else:
                attributes = dict(attributes)
            for (uri, prefix) in self._new_namespaces:
                if prefix:
                    attributes["xmlns:" + prefix] = uri
                else:
                    attributes["xmlns"] = uri
            self._new_namespaces = []
            attributes = attributes.items() + kwargs.items()
            # Sort them, if requested
            if self._sort:
                if callable(self._sort):
                    attributes = self._sort(attributes, tag)
                else:
                    attributes = sorted(attributes)
            # Do the actual writing
            for name, value in attributes:
                name = self._cname(name)
                self.write(" " + name + "=\""
                           + escape_attribute(value, self.encoding)
                           + "\"")
        self._start_tag_open = True
        self._wrote_data = False
        self._tags.append(tag)

    def end(self, tag=None):
        """Close the most recently opened element.

        If `tag` is given, it must match the tag name of the open
        element, or an `XMLSyntaxError will be raised.

        """
        open_tag = self._tags.pop()
        if tag is not None:
            tag = self._cname(tag)
            if open_tag != tag:
                raise XMLSyntaxError("Start and end tag mismatch: %s and /%s."
                                     % (open_tag, tag))
        # Use the short form for empty elements
        # TODO: make this configurable
        if self._start_tag_open:
            self.write(" />")
            self._start_tag_open = False
        else:
            if self._pretty_print and not self._wrote_data:
                self.write("\n" + INDENT * len(self._tags))
            self.write("</" + open_tag + ">")
        self._wrote_data = False

    def start_ns(self, prefix, uri):
        """Add a namespace declaration to the scope of the next
        element."""
        new_map = self._namespace_maps[-1].copy()
        new_map[uri] = prefix
        self._namespace_maps.append(new_map)
        self._new_namespaces.append((uri, prefix))

    def end_ns(self):
        """End a namespace scope."""
        # TODO: remove this, as it should be handled automatically
        del self._namespace_maps[-1]

    def data(self, data):
        """Add character data."""
        if not (self._pretty_print and not data.strip()):
            if self._start_tag_open:
                self.write(">")
                self._start_tag_open = False
            self.write(escape_cdata(data, self.encoding))
            self._wrote_data = True

    def element(self, element, attributes=None, data=None, **kwargs):
        if hasattr(element, "tag"):
            attrib = dict(element.attrib)
            if attributes:
                attrib.update(attributes)
            if hasattr(element, "nsmap"):
                self.start(element.tag, attrib, element.nsmap, **kwargs)
            else:
                self.start(element.tag, attrib, **kwargs)
            if data is not None or element.text:
                if data is not None:
                    self.data(data)
                else:
                    self.data(element.text)
            for child in element:
                self.element(child)
            self.end()
            if element.tail:
                self.data(element.tail)
        else:
            self.start(element, attributes, **kwargs)
            if data:
                self.data(data)
            self.end(element)

    def _close_start(self):
        # Make sure the start tag is finished
        if self._start_tag_open:
            self.write(">")
        self._start_tag_open = False

    def declaration(self):
        """Write an XML declaration."""
        self.write("<?xml version='1.0' encoding='" + self.encoding + "'?>")
    xml = declaration

    def comment(self, data):
        """Add an XML comment."""
        self._close_start()
        self.write("<!--" + escape_cdata(data, self.encoding) + "-->")

    def pi(self, target, data):
        """Add an XML processing instruction."""
        self._close_start()
        self.write("<?" + target + " " + data + "?>")

    def close(self):
        """Close all open elements."""
        while self._tags:
            self.end()
