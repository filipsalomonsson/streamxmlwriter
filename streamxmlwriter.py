#!/usr/bin/env python
"""streamxmlwriter - A simple library for incrementally writing XML
files of arbitrary size. Supports pretty-printing and custom attribute
ordering. Experimental namespace support.

In early development; poor documentation and tests; may eat your
children. The latest development version is available from the git
repository: http://github.com/infixfilip/streamxmlwriter/tree/master

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
__version__ = "0.1"


INDENT = "  "

def escape_attribute(value, encoding):
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace("\"", "&quot;")
    return value.encode(encoding, "xmlcharrefreplace")

def escape_cdata(data, encoding):
    data = data.replace("&", "&amp;")
    data = data.replace("<", "&lt;")
    data = data.replace(">", "&gt;")
    return data.encode(encoding, "xmlcharrefreplace")

def sorter_factory(attrib_order):
    for tag, names in attrib_order.iteritems():
        attrib_order[tag] = dict((name, n) for (n, name) in enumerate(names))
    def asort(pairs, tag):
        def key(a):
            name, value = a
            keys = attrib_order.get(tag, {})
            if name in keys:
                return keys.get(name), name
            else:
                return keys.get(None, len(keys)), name
        return sorted(pairs, key=key)
    return asort


class XMLSyntaxError(Exception):
    pass


class XMLWriter(object):
    """Stream XML writer"""
    def __init__(self, file, encoding="utf-8",
                 pretty_print=False, sort=True):
        self.write = file.write
        self.encoding = encoding
        self._pretty_print = pretty_print
        self._sort = sort
        if isinstance(sort, dict):
            self._sort = sorter_factory(sort)
        self._tags = []
        self._start_tag_open = False
        if self.encoding not in ("us-ascii", "utf-8"):
            self.declaration()
    
    def start(self, tag, attributes=None, **kwargs):
        self._close_start()
        if self._pretty_print and self._tags and not self._wrote_data:
            self.write("\n" + INDENT * len(self._tags))
        self.write("<" + tag)
        if attributes or kwargs:
            if attributes is None: attributes={}
            attributes = attributes.items() + kwargs.items()
            if self._sort:
                if callable(self._sort):
                    attributes = self._sort(attributes, tag)
                else:
                    attributes = sorted(attributes)
                for name, value in attributes:
                    self.write(" " + name + "=\""
                               + escape_attribute(value, self.encoding)
                               + "\"")
        self._start_tag_open = True
        self._wrote_data = False
        self._tags.append(tag)

    def end(self, tag=None):
        open_tag = self._tags.pop()
        if tag is not None and open_tag != tag:
            raise XMLSyntaxError("Start and end tag mismatch: %s and /%s."
                                 % (open_tag, tag))
        if self._start_tag_open:
            self.write(" />")
            self._start_tag_open = False
        else:
            if self._pretty_print and not self._wrote_data:
                self.write("\n" + INDENT * len(self._tags))
            self.write("</" + open_tag + ">")
        self._wrote_data = False

    def data(self, data):
        self._close_start()
        self.write(escape_cdata(data, self.encoding))
        self._wrote_data = True

    def element(self, tag, attributes=None, data=None, **kwargs):
        self.start(tag, attributes, **kwargs)
        if data:
            self.data(data)
        self.end(tag)

    def _close_start(self):
        if self._start_tag_open:
            self.write(">")
        self._start_tag_open = False

    def declaration(self):
        self.write("<?xml version='1.0' encoding='" + self.encoding + "'?>")

    def comment(self, data):
        self.write("<!-- " + escape_cdata(data, self.encoding) + " -->")

    def close(self):
        while self._tags:
            self.end()
