#!/usr/bin/env python
"""Test suite for Stream XML Writer module"""

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

import unittest
from streamxmlwriter import *

class XMLWriterTestCase(unittest.TestCase):
    def setUp(self):
        global StringIO
        from cStringIO import StringIO

    def testSingleElement(self):
        out = StringIO()
        writer = XMLWriter(out)
        writer.start("foo")
        writer.end()
        self.assertEqual(out.getvalue(), "<foo />")

    def testTextData(self):
        out = StringIO()
        writer = XMLWriter(out)
        writer.start("foo")
        writer.data("bar")
        writer.end()
        self.assertEqual(out.getvalue(), "<foo>bar</foo>")

    def testSingleAttribute(self):
        out = StringIO()
        writer = XMLWriter(out)
        writer.start("foo", {"bar": "baz"})
        writer.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"baz\" />")

    def testSortedAttributes(self):
        out = StringIO()
        writer = XMLWriter(out)
        writer.start("foo", {"bar": "bar", "baz": "baz"})
        writer.end()
        self.assertEqual(out.getvalue(),
                         "<foo bar=\"bar\" baz=\"baz\" />")

    def testEscapeAttributes(self):
        out = StringIO()
        writer = XMLWriter(out)
        writer.start("foo", {"bar": "<>&\""})
        writer.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"&lt;&gt;&amp;&quot;\" />")

    def testEscapeCharacterData(self):
        out = StringIO()
        writer = XMLWriter(out)
        writer.start("foo")
        writer.data("<>&")
        writer.end()
        self.assertEqual(out.getvalue(), "<foo>&lt;&gt;&amp;</foo>")


if __name__ == "__main__":
    unittest.main()
