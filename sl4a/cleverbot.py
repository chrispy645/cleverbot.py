from __future__ import print_function, unicode_literals
import sys
from urllib import urlencode
from hashlib import md5
import urllib2
import json


__all__ = ['Cleverbot', 'CleverbotAPIRejection']


class Cleverbot(object):
    HOST = "www.cleverbot.com"
    SCHEME = "http"
    PATH = "/webservicemin"
    RESOURCE = "{0}://{1}{2}".format(SCHEME, HOST, PATH)

    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
        'Accept': 'text/html,application/xhtml+xml'
        ',application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept-Language': 'en-us,en;q=0.8,en-us;q=0.5,en;q=0.3',
        'Cache-Control': 'no-cache',
        'Host': HOST,
        'Referer': "{0}://{1}/".format(SCHEME, HOST),
        'Pragma': 'no-cache',
    }

    QUERY_DATA = {
        'start': 'y',
        'icognoid': 'wsf',
        'fno': 0,
        'sub': 'Say',
        'islearning': '1',
        'cleanslate': 'false',
    }

    def __init__(self, data=QUERY_DATA):
        self.data = {}
        self.data.update(self.QUERY_DATA)
        if data:
            self.data.update(data)

    def ask(self, question):
        self._send(question)
        return self.data['ttsText'].decode('utf-8',"ignore")

    def _generate_token(self):
        """
        Cleverbot tries to prevent unauthorized access to its API by
        obfuscating how it generates the 'icognocheck' token, so we have
        to URLencode the data twice: once to generate the token, and
        twice to add the token to the data we're sending to Cleverbot.
        """
        enc_data = urlencode(self.data)
        # (!) this appears to be where the old api broke
        digest_txt = enc_data[9:35]
        return md5(digest_txt.encode('utf-8')).hexdigest()

    def _send(self, question):
        self.data['stimulus'] = question
        self.data['icognocheck'] = self._generate_token()

        #r = requests.post(
        #    self.RESOURCE,
        #    data=self.data,
        #    headers=self.REQUEST_HEADERS)
        req = urllib2.Request(self.RESOURCE, urlencode(self.data), self.REQUEST_HEADERS)
        r = urllib2.urlopen(req)
        r_content = r.read()
        r_code = r.getcode()
        #r.close()
        #print (req.getcode())
        #sys.exit(0)

        if b'DENIED' in r_content or r_code == 403:
            raise CleverbotAPIRejection(r_code)
        elif r_code != 200: #elif not r.ok:
            r.raise_for_status()
        else:
            self._update_conversation_history(r_content)

    def _update_conversation_history(self, response):
        field_names = (
            None, 'sessionid', 'logurl', 'vText8',
            'vText7', 'vText6', 'vText5', 'vText4',
            'vText3', 'vText2', 'prevref', None,
            'emotionalhistory', 'ttsLocMP3', 'ttsLocTXT', 'ttsLocTXT3',
            'ttsText', 'lineRef', 'lineURL', 'linePOST',
            'lineChoices', 'lineChoicesAbbrev', 'typingData', 'divert')
        for k, v in zip(field_names, response.split(b'\r')):
            if k:
                self.data[k] = v


class CleverbotAPIRejection(Exception):
    pass


if __name__ == "__main__":
    cb1 = Cleverbot()
    cb2 = Cleverbot()

    resp1 = cb1.ask("Hello.")
    print("Bob:", "Hello")

    while True:
        print("Alice:" + resp1)
        resp2 = cb2.ask(resp1)
        print("Bob:" + resp2)
        resp1 = cb1.ask(resp2)
