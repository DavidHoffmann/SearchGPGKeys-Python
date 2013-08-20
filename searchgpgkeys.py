#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
SearchGPGKeys is a program to search GPG-Keys for emailadresses at GPG-Keyservers
Copyright (C) 2013  David Hoffmann

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''


class SearchGPGKeys(object):
    def __init__(self, debug):
        self.__InitLogging(debug)
        self.__logging.info('Start logging - ' + self.__class__.__name__)
        
        self.__browser = self.__GetBrowser()


    def __InitLogging(self, debug):
        '''initialise logging'''
        import logging, os.path, tempfile
        
        logFile = os.path.join(tempfile.gettempdir(), self.__class__.__name__ + '.log')

        if debug:
            logLevel = logging.DEBUG
        else:
            logLevel = logging.INFO

        logging.basicConfig(level = logLevel,
            format = '%(asctime)s %(levelname)-8s %(message)s',
            datefmt = '%a, %d %b %Y %H:%M:%S',
            filename = logFile,
            filemode = 'w')

        self.__logging = logging


    def __GetRandomUserAgent(self):
        '''return user-agent'''

        import random

        # list of browsers
        browsers = [ "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7",\
                     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.91 Chrome/12.0.742.9 Safari/534.30",\
                     "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0" ]

        # randomize browsers
        random.shuffle(browsers)

        # get first random browser
        curBrowser = browsers[0]

        self.__logging.debug("User-Agent: " + curBrowser)

        return curBrowser


    def __GetBrowser(self):
        '''returns browser objectr'''
        import mechanize, cgi

        # create browser
        userAgent = self.__GetRandomUserAgent()

        # setup browser
        browser = mechanize.Browser()
        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.addheaders = [('User-Agent', userAgent)]

        return browser

    
    def __GetKeyForEmail(self, address):
        '''load key for emailaddress'''
        # base keyserver url
        keyserverUrl = 'http://p80.pool.sks-keyservers.net/pks/lookup?op=get&search='

        encAddress = address.strip().replace('@', '%40')

        url = keyserverUrl + encAddress
        self.__logging.info('request url: ' + url)

        # request
        response = None
        try:
            self.__browser.open(url)
            response = self.__browser.response().read()
            self.__logging.debug(response)

            # extract key
            import re
            regex = re.compile("-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END PGP PUBLIC KEY BLOCK-----",re.DOTALL)
            r = regex.search(response)        

            if r:
                return r.group(0)
            else:
                self.__logging.info('Key ' + address + ' not found')
                return None
        except Exception as ex:
            self.__logging.error("ERROR: " + str(ex))
            pass

        return None

    def __SaveKey(self, address, outputDirectoryName, key):
        '''save key to file'''
        import os.path
        # create filename
        outputFilename = os.path.join(outputDirectoryName, address.strip().lower().replace('@', '_AT_') + '.asc')

        self.__logging.debug('Output filename: ' + outputFilename)

        f = open(outputFilename, 'w')
        f.write(key)
        f.close()


    def Search(self, addresses, outputDirectoryName):
        '''search the given keys at online keyservers'''
        import os.path

        # check params
        if addresses == None or len(addresses) == 0:
            self.__logging.warn('Search with no addresses')
            return
        
        # load keys for all addresses
        for address in addresses:
            key = self.__GetKeyForEmail(address)

            if key != None and key != '':
                outputFilename = os.path.join(outputDirectoryName, address.strip().lower().replace('@', '_AT_') + '.asc')
                if os.path.isfile(outputFilename):
                    self.__logging.info('key exists - ' + address.strip().lower())
                else:
                    self.__SaveKey(address, outputDirectoryName, key)
        
    
    def LoadAddressFile(self, filename):
        '''load file with emailadresses'''
        # check params
        if filename == None or filename == '':
            self.__logging.warn('no filename')
            return

        addresses = None
        
        # load addressdata
        try:
            with open(filename) as f:
                addresses = f.readlines()
        except:
            self.__logging.error('file with emailaddresses does not exists. - filename: ' + filename)

        # TODO: remove empty lines

        # logging
        if len(addresses) == 0:
            self.__logging.warn('Addressfile has no adresses')
        else:
            self.__logging.debug('Load file with ' + str(len(addresses)) + ' lines.')

        return addresses


if __name__ == '__main__':
    '''main for console'''
    import sys, getopt
    
    # get args
    try:
        args = sys.argv[1:]
        opts, args = getopt.gnu_getopt(args, "f:d:", ['debug'])
    except getopt.GetoptError:
        pass

    inFilename = None
    outDirectory = None
    debug = False

    for o, a in opts:
        if o == '-f':
            inFilename = a
        
        if o == '-d':
            outDirectory = a

        if o == '--debug':
            debug = True

    searchGPGKeys = SearchGPGKeys(debug)

    # start
    addresses = searchGPGKeys.LoadAddressFile(inFilename)
    searchGPGKeys.Search(addresses, outDirectory)

