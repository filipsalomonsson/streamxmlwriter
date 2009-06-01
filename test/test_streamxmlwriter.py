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

def writer_and_output(*args, **kwargs):
    out = StringIO()
    return XMLWriter(out, *args, **kwargs), out


class XMLWriterTestCase(unittest.TestCase):
    def testSingleElement(self):
        w, out = writer_and_output()
        w.start("foo")
        w.end()
        self.assertEqual(out.getvalue(), "<foo />")

    def testTextData(self):
        w, out = writer_and_output()
        w.start("foo")
        w.data("bar")
        w.end()
        self.assertEqual(out.getvalue(), "<foo>bar</foo>")

    def testSingleAttribute(self):
        w, out = writer_and_output()
        w.start("foo", {"bar": "baz"})
        w.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"baz\" />")

    def testSortedAttributes(self):
        w, out = writer_and_output()
        w.start("foo", {"bar": "bar", "baz": "baz"})
        w.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"bar\" baz=\"baz\" />")

    def testEscapeAttributes(self):
        w, out = writer_and_output()
        w.start("foo", {"bar": "<>&\""})
        w.end()
        self.assertEqual(out.getvalue(), "<foo bar=\"&lt;>&amp;&quot;\" />")

    def testEscapeCharacterData(self):
        w, out = writer_and_output()
        w.start("foo")
        w.data("<>&")
        w.end()
        self.assertEqual(out.getvalue(), "<foo>&lt;&gt;&amp;</foo>")

    def testFileEncoding(self):
        w1, out1 = writer_and_output()
        w2, out2 = writer_and_output(encoding="us-ascii")
        w3, out3 = writer_and_output(encoding="iso-8859-1")
        w4, out4 = writer_and_output(encoding="utf-8")
        for w in (w1, w2, w3, w4):
            w.start("foo")
            w.data(u"\xe5\xe4\xf6\u2603\u2764")
            w.end()
        self.assertEqual(out1.getvalue(),
                         "<foo>\xc3\xa5\xc3\xa4\xc3\xb6\xe2\x98\x83\xe2\x9d\xa4</foo>")
        self.assertEqual(out2.getvalue(),
                         "<foo>&#229;&#228;&#246;&#9731;&#10084;</foo>")
        self.assertEqual(out3.getvalue(),
                         "<?xml version='1.0' encoding='iso-8859-1'?>" \
                         "<foo>\xe5\xe4\xf6&#9731;&#10084;</foo>")
        self.assertEqual(out4.getvalue(),
                         "<foo>\xc3\xa5\xc3\xa4\xc3\xb6\xe2\x98\x83\xe2\x9d\xa4</foo>")

    def testClose(self):
        w, out = writer_and_output()
        w.start("a")
        w.start("b")
        w.close()
        self.assertEqual(out.getvalue(), "<a><b /></a>")

    def testPrettyPrint(self):
        w, out = writer_and_output(pretty_print=True)
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


class NamespaceTestCase(unittest.TestCase):
    def testSimple(self):
        w, out = writer_and_output()
        w.start_ns("", "http://example.org/ns")
        w.start("{http://example.org/ns}foo")
        w.close()
        self.assertEqual(out.getvalue(),
                         '<foo xmlns="http://example.org/ns" />')

    def testAttribute(self):
        w, out = writer_and_output()
        w.start_ns("a", "http://example.org/ns")
        w.start("foo", {"{http://example.org/ns}bar": "baz"})
        w.close()
        self.assertEqual(out.getvalue(),
                         '<foo xmlns:a="http://example.org/ns" a:bar="baz" />')

    def testPrefixedElement(self):
        w, out = writer_and_output()
        w.start_ns("a", "http://example.org/ns")
        w.start("{http://example.org/ns}foo")
        w.close()
        self.assertEqual(out.getvalue(),
                         '<a:foo xmlns:a="http://example.org/ns" />')

    def testDefaultUnbinding(self):
        w, out = writer_and_output()
        w.start_ns("", "http://example.org/ns")
        w.start("foo")
        w.start_ns("", "")
        w.start("foo")
        w.close()
        self.assertEqual(out.getvalue(),
                         '<foo xmlns="http://example.org/ns">'
                         '<foo xmlns="" /></foo>')

    def testPrefixRebinding(self):
        w, out = writer_and_output()
        w.start_ns("a", "http://example.org/ns")
        w.start("{http://example.org/ns}foo")
        w.start_ns("a", "http://example.org/ns2")
        w.start("{http://example.org/ns2}foo")
        w.close()
        self.assertEqual(out.getvalue(),
                         '<a:foo xmlns:a="http://example.org/ns">'
                         '<a:foo xmlns:a="http://example.org/ns2" />'
                         '</a:foo>')

    def testAttributesSameLocalName(self):
        w, out = writer_and_output()
        w.start_ns("a", "http://example.org/ns1")
        w.start_ns("b", "http://example.org/ns2")
        w.start("foo")
        w.start("bar", {"{http://example.org/ns1}attr": "1",
                        "{http://example.org/ns2}attr": "2"})
        w.close()
        self.assertEquals(out.getvalue(),
                          '<foo xmlns:a="http://example.org/ns1"'
                          ' xmlns:b="http://example.org/ns2">'
                          '<bar a:attr="1" b:attr="2" />'
                          '</foo>')

    def testAttributesSameLocalOnePrefixed(self):
        w, out = writer_and_output()
        w.start_ns("a", "http://example.org/ns")
        w.start("foo")
        w.start("bar", {"{http://example.org/ns}attr": "1",
                        "attr": "2"})
        w.close()
        self.assertEquals(out.getvalue(),
                          '<foo xmlns:a="http://example.org/ns">'
                          '<bar attr="2" a:attr="1" />'
                          '</foo>')

    def testAttributesSameLocalOnePrefixedOneDefault(self):
        w, out = writer_and_output()
        w.start_ns("", "http://example.org/ns1")
        w.start_ns("a", "http://example.org/ns2")
        w.start("foo")
        w.start("bar", {"{http://example.org/ns1}attr": "1",
                        "{http://example.org/ns2}attr": "2"})
        w.close()
        self.assertEquals(out.getvalue(),
                          '<foo xmlns="http://example.org/ns1"'
                          ' xmlns:a="http://example.org/ns2">'
                          '<bar attr="1" a:attr="2" />'
                          '</foo>')


# from lxml import etree
# 
# rmt = etree.parse("test/xmlconf/eduni/namespaces/1.0/rmt-ns10.xml")
# 
# #<TEST RECOMMENDATION="NS1.0" SECTIONS="2" URI="001.xml" ID="rmt-ns10-001" TYPE="valid">
# def test_factory(uri, id):
#     def func(self):
#         doc = etree.parse(uri)
#         canonical = StringIO()
#         doc.write_c14n(canonical, with_comments=False)
#         # print
#         # print
#         # print uri
#         # print tostring(doc.getroot())
#         events = ("start", "end", "start-ns", "end-ns")
#         out = StringIO()
#         w = XMLWriter(out, encoding="utf-8")
#         for event, elem in etree.iterparse(uri, events):
#             if event == "start-ns":
#                 prefix, ns = elem
#                 w.start_ns(prefix, ns)
#             elif event == "end-ns":
#                 w.end_ns()
#             elif event == "start":
#                 w.start(elem.tag, elem.attrib)
#                 if elem.text:
#                     w.data(elem.text)
#             elif event == "end":
#                 w.end(elem.tag)
#                 if elem.tail:
#                     w.data(elem.tail)
#         w.close()
#         canonical2 = StringIO()
#         tree = etree.ElementTree(etree.XML(out.getvalue()))
#         tree.write_c14n(canonical2, with_comments=False)
#         self.assertEquals(canonical.getvalue(),
#                           canonical2.getvalue())
#     return func
# for test in rmt.xpath(".//TEST[@TYPE='valid' or @TYPE='invalid']"):
#     uri = "test/xmlconf/eduni/namespaces/1.0/" + test.get("URI")
#     id = "test_" + test.get("ID").replace("-", "_")
#     setattr(NamespaceTestCase, id, test_factory(uri, id))



if __name__ == "__main__":
    unittest.main()
