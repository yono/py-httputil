#!/usr/bin/env python
# -*- coding:utf-8 -*-

import httplib
import socket
import urllib
import urlparse
import re
import time

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
        self.is_exist_flg = None

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
            self.is_exist_flg = False
            return (False, url)

        statuses = set([301, 302, 303, 307])
        try:
            self.conn.request("HEAD", self.path, self.params, self.headers)
            resp = self.conn.getresponse()
            if resp.status == 200:
                found = True
                newurl = url
            elif resp.status in statuses:
                newurl = urlparse.urljoin(url,
                            resp.getheader('location', ''))
                if url == newurl:
                    return (False, url)
                time.sleep(5)
                found, newurl = self.is_exist(newurl, depth + 1)
            else:
                print "Status %d %s : %s" % (resp.status, resp.reason, url)
                self.is_exist_flg = False
                return (False, url)
        except Exception, e:
            print e.__class__, e, url
            self.is_exist_flg = False
            return (False, url)
        self.is_exist_flg = found
        return (found, newurl)

    def get_content_type(self):
        if not self.is_exist_flg:
            self._set_all_false()
        elif self.content_type is None:
            self._get_header()
        return self.content_type

    def get_charset_from_header(self):
        if not self.is_exist_flg:
            self._set_all_false()
        elif self.charset_from_header is None:
            self._get_header()
        return self.charset_from_header

    def get_charset_from_html(self):
        if not self.is_exist_flg:
            self._set_all_false()
        elif self.charset_from_html is None:
            self.html = self.get_html()
            char_re = re.compile(r"(?is)content=[\"'].*?;\s*charset=(.*?)[\"']")
            result = char_re.search(self.html)
            if result is not None:
                self.charset_from_html= result.group(1)
            else:
                self.charset_from_html = ''
        return self.charset_from_html

    def get_html(self):
        if not self.is_exist_flg:
            self._set_all_false()
        elif self.html is None:
            try:
                self.conn.request("GET", self.path)
                resp = self.conn.getresponse()
                self.html = resp.read()
            except:
                self.html = ''
        return self.html

    def _get_header(self):
        try:
            self.conn.request("GET", self.path)
            metadata = self.conn.getresponse().getheader('Content-Type')
            if metadata is None:
                self.charset_from_header = ''
            else:
                meta_list = metadata.split(';')
                self.content_type = meta_list[0]
                if len(meta_list) < 2:
                    self.charset_from_header = ''
                else:
                    self.charset_from_header = meta_list[1].split('=')[1]
        except:
            self._set_all_false()


    def _set_all_false(self):
        self.is_exist_flg = False
        self.content_type = ''
        self.charset_from_header = ''
        self.charset_from_html = ''
        self.html = ''


if __name__ == '__main__':
    url = 'http://twitter.com/'
    hutil = HTTPUtil(url)
    print hutil.get_content_type()
    print hutil.get_charset_from_header()
    print hutil.get_charset_from_html()
    print hutil.is_exist()
    print hutil.get_html()
