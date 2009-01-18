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
from cStringIO import StringIO
from streamxmlwriter import *

class XMLWriterTestCase(unittest.TestCase):
    def writer_and_output(self, *args, **kwargs):
        out = StringIO()
        return XMLWriter(out, *args, **kwargs), out

    def testSingleElement(self):
        w, out = self.writer_and_output()
        w.start("foo")
        w.end()
        self.assertEqual(out.getvalue(), "<foo />")

    def testTextData(self):
        w, out = self.writer_and_output()
        w.start("foo")
        w.data("bar")
        w.end()
        self.assertEqual(out.getvalue(), "<foo>bar</foo>")

    def testSingleAttribute(self):
        w, out = self.writer_and_output()
        w.start("foo", {"bar": "baz"})
        w.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"baz\" />")

    def testSortedAttributes(self):
        w, out = self.writer_and_output()
        w.start("foo", {"bar": "bar", "baz": "baz"})
        w.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"bar\" baz=\"baz\" />")

    def testEscapeAttributes(self):
        w, out = self.writer_and_output()
        w.start("foo", {"bar": "<>&\""})
        w.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"&lt;&gt;&amp;&quot;\" />")

    def testEscapeCharacterData(self):
        w, out = self.writer_and_output()
        w.start("foo")
        w.data("<>&")
        w.end()
        self.assertEqual(out.getvalue(), "<foo>&lt;&gt;&amp;</foo>")

    def testFileEncoding(self):
        w1, out1 = self.writer_and_output()
        w2, out2 = self.writer_and_output(encoding="us-ascii")
        w3, out3 = self.writer_and_output(encoding="iso-8859-1")
        w4, out4 = self.writer_and_output(encoding="utf-8")
        for w in (w1, w2, w3, w4):
            w.start("foo")
            w.data(u"\xe5\xe4\xf6\u2603\u2764")
            w.end()
        self.assertEqual(out1.getvalue(),
                         "<foo>&#229;&#228;&#246;&#9731;&#10084;</foo>")
        self.assertEqual(out2.getvalue(),
                         "<foo>&#229;&#228;&#246;&#9731;&#10084;</foo>")
        self.assertEqual(out3.getvalue(),
                         "<?xml version='1.0' encoding='iso-8859-1'?>" \
                         "<foo>\xe5\xe4\xf6&#9731;&#10084;</foo>")
        self.assertEqual(out4.getvalue(),
                         "<foo>\xc3\xa5\xc3\xa4\xc3\xb6\xe2\x98\x83\xe2\x9d\xa4</foo>")

    def testClose(self):
        w, out = self.writer_and_output()
        w.start("a")
        w.start("b")
        w.close()
        self.assertEqual(out.getvalue(), "<a><b /></a>")

    def testPrettyPrint(self):
        w, out = self.writer_and_output(pretty_print=True)
        w.start("a")
        w.start("b")
        w.data("foo")
        w.end()
        w.start("b")
        w.data("bar")
        w.end()
        w.start("b")
        w.start("c")
        w.close()
        self.assertEqual(out.getvalue(), "<a>\n  <b>foo</b>\n  <b>bar</b>\n  <b>\n    <c />\n  </b>\n</a>")

if __name__ == "__main__":
    unittest.main()
