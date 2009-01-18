#!/usr/bin/env python
"""Stream XML Writer module"""

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

INDENT = "  "

def escape_attribute(value, encoding):
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace("\"", "&quot;")
    return value.encode(encoding, "xmlcharrefreplace")

def escape_cdata(data, encoding):
    data = data.replace("&", "&amp;")
    data = data.replace("<", "&lt;")
    data = data.replace(">", "&gt;")
    return data.encode(encoding, "xmlcharrefreplace")


class XMLWriter(object):
    """Stream XML writer"""
    def __init__(self, file, encoding="us-ascii", pretty_print=False):
        self.write = file.write
        self.encoding = encoding
        self._pretty_print = pretty_print
        self._tags = []
        self._start_tag_open = False
        self.declaration()
    
    def start(self, tag, attributes=None):
        self._close_start()
        if self._pretty_print and self._tags and not self._wrote_data:
            self.write("\n" + INDENT * len(self._tags))
        self.write("<" + tag)
        if attributes is not None:
            for name, value in sorted(attributes.items()):
                self.write(" " + name + "=\""
                           + escape_attribute(value, self.encoding)
                           + "\"")
        self._start_tag_open = True
        self._wrote_data = False
        self._tags.append(tag)

    def end(self):
        tag = self._tags.pop()
        if self._start_tag_open:
            self.write(" />")
            self._start_tag_open = False
        else:
            if self._pretty_print and not self._wrote_data:
                self.write("\n" + INDENT * len(self._tags))
            self.write("</" + tag + ">")
        self._wrote_data = False

    def data(self, data):
        self._close_start()
        self.write(escape_cdata(data, self.encoding))
        self._wrote_data = True

    def _close_start(self):
        if self._start_tag_open:
            self.write(">")
        self._start_tag_open = False

    def declaration(self):
        if self.encoding not in ("us-ascii", "utf-8"):
            self.write("<?xml version='1.0' encoding='" + self.encoding + "'?>")

    def close(self):
        while self._tags:
            self.end()
