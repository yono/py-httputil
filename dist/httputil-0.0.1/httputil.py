#!/usr/bin/env python
# -*- coding:utf-8 -*-

import httplib
import socket
import urllib
import urlparse
import re

socket.setdefaulttimeout(30)
class HTTPUtil(object):

    def __init__(self, url, HTTPConnection=httplib.HTTPConnection):
        self.url = url
        self.HTTPConn = HTTPConnection
        self.postdata = {}
        self.params = urllib.urlencode(self.postdata)
        self.headers = {
          "User-Agent":"Mozilla/4.0 (compatileb; MSIE 7.0; Windows NT 5.1)"
        }
        self.MAXDEPTH = 10
        self.html = None
        self.content_type = None
        self.charset_from_header = None
        self.charset_from_html = None

        """
        Access Section
        """
        self.host, self.path = urlparse.urlsplit(url)[1:3]
        if ':' in self.host:
            self.host, self.port = self.host.split(':', 1)
            try:
                self.port = int(self.port)
            except ValueError:
                print 'invalid port number %r' % (self.port,)
                return (False, self.url)
        else:
            self.port = None
        self.conn = self.HTTPConn(self.host, port=self.port)

    def is_exist(self, _url=None, depth=0):
        if _url == None:
            url = self.url
        else:
            url = _url
        socket.setdefaulttimeout(30)
        if depth == self.MAXDEPTH:
            return (False, url)

        statuses = set([301, 302, 303, 307])
        try:
            self.conn.request("HEAD", self.path, self.params, self.headers)
            resp = self.conn.getresponse()
            if resp.status == 200:
                found = True
                newurl = url
            elif resp.status in statuses:
                newurl = urlparse.urljoin(url, resp.getheader('location', ''))
                if url == newurl:
                    return (False, url)
                time.sleep(5)
                found, newurl = self.isexist(newurl, depth + 1)
            else:
                print "Status %d %s : %s" % (resp.status, resp.reason, url)
                return (False, url)
        except Exception, e:
            print e.__class__, e, url
            return (False, url)
        return (found, newurl)

    def get_content_type(self):
        if self.content_type is None:
            self.conn.request("GET", self.path)
            response = self.conn.getresponse()
            header = response.getheader('Content-Type')
            if header is None:
                self.content_type = ''
            else:
                self.content_type = header.split(';')[0]
                self.charset_from_header = header[1].split('=')[1]
        return self.content_type

    def get_charset_from_header(self):
        if self.charset_from_header is None:
            self.conn.request("GET", self.path)
            response = self.conn.getresponse()
            contenttype = response.getheader('Content-Type')
            if contenttype is None:
                self.charset_from_header = ''
            else:
                _contenttype = contenttype.split(';')
                if len(_contenttype) < 2:
                    self.charset_from_header = ''
                else:
                    self.charset_from_header = _contenttype[1].split('=')[1]
                    self.content_type = _contenttype[0]
        return self.charset_from_header

    def get_charset_from_html(self):
        if self.charset_from_html is None:
            self.conn.request("GET", self.path)
            response = self.conn.getresponse()
            self.html = response.read()
            char_re = re.compile(r"(?is)content=[\"'].*?;\s*charset=(.*?)[\"']")
            result = char_re.search(self.html)
            if result is not None:
                self.charset_from_html= result.group(1)
            else:
                self.charset_from_html = ''
        return self.charset_from_html

    def get_html(self):
        if self.html is None:
            self.conn.request("GET", self.path)
            response = self.conn.getresponse()
            self.html = response.read()
        return self.html

if __name__ == '__main__':
    url = 'http://twitter.com/'
    hutil = HTTPUtil(url)
    print hutil.get_content_type()
    print hutil.get_charset_from_header()
    print hutil.get_charset_from_html()
    print hutil.is_exist()
    print hutil.get_html()
