from __future__ import print_function, unicode_literals
import sys
if sys.version_info.major == 3 and sys.version_info.minor >= 3:
    from urllib.parse import urlunparse, urlencode
else:
    from urlparse import urlunparse
    from urllib import urlencode
from hashlib import md5
import logging
import requests


__all__ = ['Cleverbot', 'CleverbotAPIRejection']


class Cleverbot(object):

    """
    This class abstracts the cleverbot api.  It also
    allows you to instantiate it with a preserved
    conversation (data attribute).
    """

    _scheme = "http"
    _netloc = "www.cleverbot.com"
    _path = "webservicemin"
    resource = urlunparse((_scheme, _netloc, _path, "", "", ""))

    _request_headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
        'Accept': 'text/html,application/xhtml+xml'
        ',application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept-Language': 'en-us,en;q=0.8,en-us;q=0.5,en;q=0.3',
        'Cache-Control': 'no-cache',
        'Host': _netloc,
        'Referer': "{0}://{1}/".format(_scheme, _netloc),
        'Pragma': 'no-cache',
    }

    _sample_default_data = {
        'start': 'y',
        'icognoid': 'wsf',
        'fno': 0,
        'sub': 'Say',
        'islearning': '1',
        'cleanslate': 'false',
    }

    def __init__(self, data=_sample_default_data):
        self._log = logging.getLogger()
        self.data = data

    def ask(self, question):
        "Ask Cleverbot a question."

        self._log.debug("Cleverbot query: '%s'" % question)

        self.data['stimulus'] = question
        response = self._send()

        self._update_conversation_history(response)
        return self.data['ttsText'].decode('utf-8')

    def _update_token(self):
        """
        Cleverbot tries to prevent unauthorized access to its API by
        obfuscating how it generates the 'icognocheck' token, so we have
        to URLencode the data twice: once to generate the token, and
        twice to add the token to the data we're sending to Cleverbot.
        """
        enc_data = urlencode(self.data)
        # (!) this appears to be where the old api broke
        digest_txt = enc_data[9:35]
        token = md5(digest_txt.encode('utf-8')).hexdigest()
        self.data['icognocheck'] = token

    def _send(self):
        """Handles POST of current self.data to API."""
        self._update_token()
        r = requests.post(
            self.resource,
            data=self.data,
            headers=self._request_headers)

        self._log.debug('Response content: ' + r.content.decode('utf-8'))
        if b'DENIED' in r.content or r.status_code != 200:
            raise CleverbotAPIRejection(r.status_code)
        else:
            return r.content

    def _update_conversation_history(self, response):
        """Parses an API response and updates self.data."""
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
    logging.basicConfig()
    cb1 = Cleverbot()
    cb2 = Cleverbot()

    resp1 = cb1.ask("Hello.")
    print("Bob:", "Hello")

    while True:
        print("Alice:" + resp1)
        resp2 = cb2.ask(resp1)
        print("Bob:" + resp2)
        resp1 = cb1.ask(resp2)
