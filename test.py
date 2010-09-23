#!/usr/bin/env python
# -*- coding:utf-8 -*-
import httplib
from StringIO import StringIO

import sys
import httputil

class FakeSocket:
    sendbuf = None
    recvbuf = None

    def close(self):
        pass

    def sendall(self, data):
        self.sendbuf.write(data)

    def makefile(self, mode, bufsize):
        return self.recvbuf

class FakeHTTPConnection(httplib.HTTPConnection):
    def connect(self):
        self.sock = FakeSocket()

class TestHTTPUtil(object):

    def __init__(self):
        pass

    def setup(self):
        httplib.HTTP._conection_class = FakeHTTPConnection
        FakeSocket.sendbuf = StringIO()
        FakeSocket.recvbuf = StringIO('Content-type: text/html;\n\n')
        self.url = 'http://twitter.com'
        self.hutil = httputil.HTTPUtil(self.url, FakeHTTPConnection)

    def test_is_exist(self):
        self.setup()
        assert self.hutil.is_exist() == (True, self.url)

    def test_get_charset_from_header(self):
        self.setup()
        assert self.hutil.get_charset_from_header() is None

    def test_get_charset_from_html(self):
        self.setup()
        assert self.hutil.get_charset_from_html() is None

    def test_get_content_type(self):
        self.setup()
        assert self.hutil.get_content_type() is None

    def test_get_html(self):
        self.setup()
        assert self.hutil.get_html() == 'Content-type: text/html;\n\n'
