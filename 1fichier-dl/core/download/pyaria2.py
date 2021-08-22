'''The MIT License (MIT)

Copyright (c) 2014 Killua

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Description: pyaria2 is a Python 3 module that provides a wrapper class around Aria2's RPC interface. It can be used to build applications that use Aria2 for downloading data.
Author: Killua
Email: killua_hzl@163.com
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import xmlrpc.client
import os
import time

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6800
SERVER_URI_FORMAT = 'http://{}:{:d}/rpc'

class PyAria2(object):
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, session=None):
        '''
        PyAria2 constructor.

        host: string, aria2 rpc host, default is 'localhost'
        port: integer, aria2 rpc port, default is 6800
        session: string, aria2 rpc session saving.
        '''
      
        server_uri = SERVER_URI_FORMAT.format(host, port)
        self.server = xmlrpc.client.ServerProxy(server_uri, allow_none=True)
        try:
            self.server.aria2.getGlobalStat()
        except:
            print("Make sure aria2 is running.")
            exit()
        print("aria2 init success.")
            

    def addUri(self, uris, options=None, position=None):
        '''
        This method adds new HTTP(S)/FTP/BitTorrent Magnet URI.

        uris: list, list of URIs
        options: dict, additional options
        position: integer, position in download queue

        return: This method returns GID of registered download.
        '''
        uris, options = self.fixUris(uris), self.fixOptions(options)
        return self.server.aria2.addUri(uris, options, position)

    def fixUris(self, uris):
        return uris or list()

    def fixOptions(self, options):
        return options or dict()

    
