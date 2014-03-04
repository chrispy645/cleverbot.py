from hashlib import md5
import requests
import logging
from collections import deque
from urllib import urlencode


class Cleverbot(object):
    """
    This class abstracts the cleverbot api.  It also
    allows you to instantiate it with a preserved
    conversation (data attribute).
    """

    def __init__(self, data=None):
        self.host = "www.cleverbot.com"
        self.protocol = "http://"
        self.resource = "/webservicemin"
        self.api_url = self.protocol + self.host + self.resource
        self.log = logging.getLogger()

        # request headers
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Accept-Language': 'en-us,en;q=0.8,en-us;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Host': self.host,
            'Referer': self.protocol + self.host + '/',
            'Pragma': 'no-cache',
        }

        # initialize request payload
        if data:
            self.data = data
        else:
            self.data = {
                'start': 'y',
                'icognoid': 'wsf',
                'fno': 0,
                'sub': 'Say',
                'islearning': '1',
                'cleanslate': 'false',
            }

    def ask(self,q):
        """Asks Cleverbot a question.
        
        Maintains message history.

        Args:
            q (str): The question to ask
        Returns:
            Cleverbot's answer
        """
        self.log.debug("Cleverbot query: '%s'" % q)

        # Set the current question
        self.data['stimulus'] = q

        # Connect to Cleverbot's API and remember the response
        resp = self._send()

        parsed = self._parse(resp)

        return parsed

    def _send(self):
        """POST the user's question and all required information to the 
        Cleverbot API

        Cleverbot tries to prevent unauthorized access to its API by
        obfuscating how it generates the 'icognocheck' token, so we have
        to URLencode the data twice: once to generate the token, and
        twice to add the token to the data we're sending to Cleverbot.
        """

        # Generate the token
        enc_data = urlencode(self.data)
        digest_txt = enc_data[9:35]  # (!) this appears to be where the old api broke
        token = md5(digest_txt).hexdigest()
        self.data['icognocheck'] = token

        # Add the token to the data
        r = requests.post(self.api_url, data=self.data, headers=self.headers)

        # POST the data to Cleverbot's API
        self.log.debug('Response content: ' + r.content)

        if 'DENIED' in r.content or r.status_code != 200:
            raise Exception('The Cleverbot API has rejected the query.')

        # Return Cleverbot's response
        return r.content

    def _parse(self, response):
        """
        Parses Cleverbot's response, returns the text of the reply
        """

        parsed = response.split('\r')

        #self.data['??'] = parsed[0]
        self.data['sessionid'] = parsed[1]
        self.data['logurl'] = parsed[2]
        self.data['vText8'] = parsed[3]
        self.data['vText7'] = parsed[4]
        self.data['vText6'] = parsed[5]
        self.data['vText5'] = parsed[6]
        self.data['vText4'] = parsed[7]
        self.data['vText3'] = parsed[8]
        self.data['vText2'] = parsed[9]
        self.data['prevref'] = parsed[10]
        #self.data['??'] = parsed[11]
        self.data['emotionalhistory'] = parsed[12]
        self.data['ttsLocMP3'] = parsed[13]
        self.data['ttsLocTXT'] = parsed[14]
        self.data['ttsLocTXT3'] = parsed[15]
        self.data['ttsText'] = parsed[16]
        self.data['lineRef'] = parsed[17]
        self.data['lineURL'] = parsed[18]
        self.data['linePOST'] = parsed[19]
        self.data['lineChoices'] = parsed[20]
        self.data['lineChoicesAbbrev'] = parsed[21]
        self.data['typingData'] = parsed[22]
        self.data['divert'] = parsed[23]

        return self.data['ttsText']

if __name__ == "__main__":
    cb1 = Cleverbot()
    cb2 = Cleverbot()

    resp1 = cb1.ask("Hello.")
    print "Bob:", "Hello"

    while True:
        print "Alice:", resp1
        resp2 = cb2.ask(resp1)
        print "Bob:", resp2
        resp1 = cb1.ask(resp2)
