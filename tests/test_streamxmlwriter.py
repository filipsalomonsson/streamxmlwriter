#!/usr/bin/env python
"""Test suite for Stream XML Writer module"""

# Copyright (c) 2009-2010 Filip Salomonsson
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
from streamxmlwriter import XMLWriter, XMLSyntaxError


class XMLWriterTestCase(unittest.TestCase):
    def assertOutput(self, writer, output):
        self.assertEqual(writer.file.getvalue(), output)


class TestXMLWriter(XMLWriterTestCase):
    def test_single_element(self):
        w = XMLWriter(StringIO())
        w.start("foo")
        w.end()
        self.assertOutput(w, '<foo />')

    def test_text_data(self):
        w = XMLWriter(StringIO())
        w.start("foo")
        w.data("bar")
        w.end()
        self.assertOutput(w, '<foo>bar</foo>')

    def test_single_attribute(self):
        w = XMLWriter(StringIO())
        w.start("foo", {"bar": "baz"})
        w.end()
        self.assertOutput(w, '<foo bar="baz" />')

    def test_sorted_attributes(self):
        w = XMLWriter(StringIO())
        w.start("foo", {"bar": "bar", "baz": "baz"})
        w.end()
        self.assertOutput(w, '<foo bar="bar" baz="baz" />')

    def test_escape_attributes(self):
        w = XMLWriter(StringIO())
        w.start("foo", {"bar": "<>&\""})
        w.end()
        self.assertOutput(w, '<foo bar="&lt;>&amp;&quot;" />')

    def test_escape_character_data(self):
        w = XMLWriter(StringIO())
        w.start("foo")
        w.data("<>&")
        w.end()
        self.assertOutput(w, '<foo>&lt;&gt;&amp;</foo>')

    def test_file_encoding(self):
        ts = [({},
               "<foo>\xc3\xa5\xc3\xa4\xc3\xb6\xe2\x98\x83\xe2\x9d\xa4</foo>"),
              ({"encoding": "us-ascii"},
               "<foo>&#229;&#228;&#246;&#9731;&#10084;</foo>"),
              ({"encoding": "iso-8859-1"},
               "<?xml version='1.0' encoding='iso-8859-1'?>" \
                   "<foo>\xe5\xe4\xf6&#9731;&#10084;</foo>"),
              ({"encoding": "utf-8"},
               "<foo>\xc3\xa5\xc3\xa4\xc3\xb6\xe2\x98\x83\xe2\x9d\xa4</foo>")]
        for (kwargs, output) in ts:
            w = XMLWriter(StringIO(), **kwargs)
            w.start("foo")
            w.data(u"\xe5\xe4\xf6\u2603\u2764")
            w.end()
            self.assertEqual(w.file.getvalue(), output)

    def test_close(self):
        w = XMLWriter(StringIO())
        w.start("a")
        w.start("b")
        w.close()
        self.assertOutput(w, "<a><b /></a>")

    def test_declaration_late_raises_syntaxerror(self):
        w = XMLWriter(StringIO())
        w.start("a")
        self.assertRaises(XMLSyntaxError, w.declaration)

    def test_ignore_double_declaration(self):
        w = XMLWriter(StringIO())
        w.declaration()
        w.declaration()
        w.close()
        self.assertOutput(w, "<?xml version='1.0' encoding='utf-8'?>")

    def test_abbrev_empty(self):
        w = XMLWriter(StringIO(), abbrev_empty=False)
        w.start("a")
        w.close()
        self.assertOutput(w, "<a></a>")

    def test_named_end(self):
        w = XMLWriter(StringIO())
        w.start("a")
        w.end("a")
        w.close()
        self.assertTrue(True)


class TestPrettyPrinting(XMLWriterTestCase):
    def test_simple(self):
        w = XMLWriter(StringIO(), pretty_print=True)
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
        self.assertOutput(w, """\
<a>
  <b>foo</b>
  <b>bar</b>
  <b>
    <c />
  </b>
</a>""")

    def test_comment(self):
        w = XMLWriter(StringIO(), pretty_print=True)
        w.start("a")
        w.comment("comment")
        w.start("b")
        w.close()
        self.assertOutput(w, "<a>\n  <!--comment-->\n  <b />\n</a>")

    def test_comment_before_root(self):
        w = XMLWriter(StringIO(), pretty_print=True)
        w.comment("comment")
        w.start("a")
        w.close()
        self.assertOutput(w, "<!--comment-->\n<a />")

    def test_comment_after_root(self):
        w = XMLWriter(StringIO(), pretty_print=True)
        w.start("a")
        w.end()
        w.comment("comment")
        w.close()
        self.assertOutput(w,"<a />\n<!--comment-->")

    def test_pi(self):
        w = XMLWriter(StringIO(), pretty_print=True)
        w.start("a")
        w.pi("foo", "bar")
        w.start("b")
        w.close()
        self.assertOutput(w, "<a>\n  <?foo bar?>\n  <b />\n</a>")

    def test_pi_before_root(self):
        w = XMLWriter(StringIO(), pretty_print=True)
        w.pi("foo", "bar")
        w.start("a")
        w.close()
        self.assertOutput(w, "<?foo bar?>\n<a />")

    def test_pi_after_root(self):
        w = XMLWriter(StringIO(), pretty_print=True)
        w.start("a")
        w.end()
        w.pi("foo", "bar")
        w.close()
        self.assertOutput(w, "<a />\n<?foo bar?>")


class TestNamespaces(XMLWriterTestCase):
    def test_simple(self):
        w = XMLWriter(StringIO())
        w.start_ns("", "http://example.org/ns")
        w.start("{http://example.org/ns}foo")
        w.close()
        self.assertOutput(w, '<foo xmlns="http://example.org/ns" />')

    def test_attribute(self):
        w = XMLWriter(StringIO())
        w.start_ns("a", "http://example.org/ns")
        w.start("foo", {"{http://example.org/ns}bar": "baz"})
        w.close()
        self.assertOutput(w, '<foo xmlns:a="http://example.org/ns" a:bar="baz" />')

    def test_prefixed_element(self):
        w = XMLWriter(StringIO())
        w.start_ns("a", "http://example.org/ns")
        w.start("{http://example.org/ns}foo")
        w.close()
        self.assertOutput(w, '<a:foo xmlns:a="http://example.org/ns" />')

    def test_default_unbinding(self):
        w = XMLWriter(StringIO())
        w.start_ns("", "http://example.org/ns")
        w.start("{http://example.org/ns}foo")
        w.start_ns("", "")
        w.start("foo")
        w.close()
        self.assertOutput(w, '<foo xmlns="http://example.org/ns">'
                          '<foo xmlns="" /></foo>')

    def test_prefix_rebinding(self):
        w = XMLWriter(StringIO())
        w.start_ns("a", "http://example.org/ns")
        w.start("{http://example.org/ns}foo")
        w.start_ns("a", "http://example.org/ns2")
        w.start("{http://example.org/ns2}foo")
        w.close()
        self.assertOutput(w,'<a:foo xmlns:a="http://example.org/ns">'
                          '<a:foo xmlns:a="http://example.org/ns2" />'
                          '</a:foo>')

    def test_attributes_same_local_name(self):
        w = XMLWriter(StringIO())
        w.start_ns("a", "http://example.org/ns1")
        w.start_ns("b", "http://example.org/ns2")
        w.start("foo")
        w.start("bar", {"{http://example.org/ns1}attr": "1",
                        "{http://example.org/ns2}attr": "2"})
        w.close()
        self.assertOutput(w, '<foo xmlns:a="http://example.org/ns1"'
                          ' xmlns:b="http://example.org/ns2">'
                          '<bar a:attr="1" b:attr="2" />'
                          '</foo>')

    def test_attributes_same_local_one_prefixed(self):
        w = XMLWriter(StringIO())
        w.start_ns("a", "http://example.org/ns")
        w.start("foo")
        w.start("bar", {"{http://example.org/ns}attr": "1",
                        "attr": "2"})
        w.close()
        self.assertOutput(w,'<foo xmlns:a="http://example.org/ns">'
                          '<bar attr="2" a:attr="1" />'
                          '</foo>')

    def test_attributes_same_local_one_prefixed_one_default(self):
        w = XMLWriter(StringIO())
        w.start_ns("", "http://example.org/ns1")
        w.start_ns("a", "http://example.org/ns2")
        w.start("{http://example.org/ns1}foo")
        w.start("{http://example.org/ns1}bar",
                {"{http://example.org/ns1}attr": "1",
                 "{http://example.org/ns2}attr": "2"})
        w.close()
        self.assertOutput(w, '<foo xmlns="http://example.org/ns1"'
                          ' xmlns:a="http://example.org/ns2">'
                          '<bar attr="1" a:attr="2" />'
                          '</foo>')


class TestIterwrite(XMLWriterTestCase):
    def test_basic(self):
        from lxml import etree
        from cStringIO import StringIO
        w = XMLWriter(StringIO())
        xml = """\
<!--comment before--><?pi before?><foo xmlns="http://example.org/ns1">
  <?a pi?>
  <bar xmlns:b="http://example.org/ns2">
    <?pi inside?>some text
    <baz attr="1" b:attr="2" />
    oh dear<!--comment inside -->text here too
  </bar>
</foo><?pi after?><!--comment after-->"""
        events = ("start", "end", "start-ns", "end-ns", "pi", "comment")
        w.iterwrite(etree.iterparse(StringIO(xml), events))
        w.close()
        self.assertOutput(w, xml)

    def test_chunked_text(self):
        from lxml import etree
        from cStringIO import StringIO
        for padding in (16382, 32755):
            padding = " " * padding
            w = XMLWriter(StringIO())
            xml = "%s<doc><foo>hello</foo></doc>" % padding
            events = ("start", "end")
            w.iterwrite(etree.iterparse(StringIO(xml), events))
            w.close()
            self.assertOutput(w, xml.strip())


if __name__ == "__main__":
    unittest.main()
