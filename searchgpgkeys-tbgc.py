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


class SearchGPGKeysTBGC(object):
    def __init__(self, debug):
        self.__InitLogging(debug)
        self.__logging.info('Start logging - ' + self.__class__.__name__)


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


    def LoadAddresses(self, contactsDirectory):
        '''Load emailadresses from google contacts files'''
        # param check
        if contactsDirectory == None or contactsDirectory == '':
            self.__logging.warn('contactsDirectory is empty')
            return None

        emailaddresses = []
        filenames = []
        import os, re

        # get all filenames
        dirList = os.listdir(contactsDirectory)
        for dirFile in dirList:
            filenames.append(dirFile)
            self.__logging.debug("File found: " + dirFile)

        if filenames != None and len(filenames) > 0:
            regex = re.compile("\<gd\:email.*?address=\"(.*?)\".*?\/\>", re.DOTALL)

            # read addresses from files
            for filename in filenames:
                # open file
                try:
                    with open(os.path.join(contactsDirectory, filename), 'r') as f:
                        fileData = f.read()
                        f.close()
                except:
                    pass

                # add address to list
                r = regex.search(fileData)
                if r:
                    emailaddresses.append(r.group(1).lower())
                    self.__logging.debug("Address found: " + r.group(1))
                

        if emailaddresses != None:
            self.__logging.info(str(len(emailaddresses)) + " email addresses found")
        else:
            self.__logging.info("no email addresses found")

        return emailaddresses


    def RemoveTBABMailRules(self, contactsDirectoy, keysFound):
        '''Remove encrypt rules for email addresses with gpg keys'''

        import os, re
        
        # param check
        if contactsDirectory == None or contactsDirectory == '':
            self.__logging.warn('contactsDirectory is empty')
            return None

        Filedata = None
        pgpRulesFile = None

        # load pgrules.xml
        # open file                                                       
        try:
            pgpRulesFile = os.path.join(os.path.join(os.path.join(contactsDirectory, '..'), '..'), 'pgprules.xml')
            self.__logging.info("pgprules: " + pgpRulesFile)

            # load pgpRules.xml
            with open(pgpRulesFile, 'r') as f:
                fileData = f.read()
                f.close()
        except:
            self.__logging.error("can't open pgprules.xml file")
            pass

        # remove rule for mailadresses with keys
        if fileData != None:
            for kf in keysFound:
                fileData = re.sub("<pgpRule email=\"{" + kf.strip() + "}\".*?/>\n", "", fileData)

        # write pgpRules.xml
        with open(pgpRulesFile, 'w') as f:
            f.write(fileData)
            f.close()


    def ImportKeys(self, outDirectory):
        import os, subprocess
        cmd = 'gpg --import ' + os.path.join(outDirectory + '*.asc')
        self.__logging.info ('command: ' + cmd)
        subprocess.call(cmd, shell = True)


if __name__ == '__main__':
    '''main for console'''
    import sys, getopt

    # get args                                                                                                 
    try:
        args = sys.argv[1:]
        opts, args = getopt.gnu_getopt(args, "c:d:", ['debug'])
    except getopt.GetoptError:
        pass

    contactsDirectory = None
    outDirectory = None
    debug = False

    for o, a in opts:
        if o == '-c':
            contactsDirectory = a

        if o == '-d':
            outDirectory = a

        if o == '--debug':
            debug = True

    # start
    searchGPGKeysTBGC = SearchGPGKeysTBGC(debug)
    addresses = searchGPGKeysTBGC.LoadAddresses(contactsDirectory)

    from searchgpgkeys import SearchGPGKeys
    searchGPGKeys = SearchGPGKeys(debug)
    keysFound = searchGPGKeys.Search(addresses, outDirectory)

    if keysFound != None and len(keysFound) > 0:
        searchGPGKeysTBGC.ImportKeys(outDirectory)
        searchGPGKeysTBGC.RemoveTBABMailRules(contactsDirectory, keysFound)

