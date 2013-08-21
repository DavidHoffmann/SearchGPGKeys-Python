searchgpgkeys.py
================

Search GPG-Keys for emailadresses.

Requirements
------------
* Python 2.7
* Python module: mechanize

Parameters
----------
-f FileWithEmailaddresses.txt   
-d OutputDirectory

Example
-------
python searchgpgkeys.py -f FileWithEmailaddress.txt -d /tmp

searchgpgkeys-tbgc.py
=====================

Search GPG-Keys for emailaddresses with searchgpgkeys.py.
It uses the google-contacts extension for thunderbird as source.

Requirements
------------
* Python 2.7
* searchgpgkeys.py

Parameters
----------
-c GoogleContacts cache directory
-d OutputDirectory

Example
-------
python searchgpgkeys-tbgc.py -c /home/user/.thunderbird/aabbccddee.default/GoogleContacts/cache -d /tmp

Info
----
All scripts are developed and tested on a lubuntu (Linux) system.