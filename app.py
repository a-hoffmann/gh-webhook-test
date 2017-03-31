#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import sys

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    sys.stdout.flush()

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    sys.stdout.flush()
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    
    if req.get("result").get("action") == "read-recipe":
        speech = "You wanted to read the recipe. Unfortunately, I forgot it."
        
    elif req.get("result").get("action") == "add-ingredient":
        #do another
        if urlopen("http://www.bbc.com/news").read().find("Singapore") == -1:
            speech="No news of Singapore on BBC News front page"

    return {
        "speech": speech,
        "displayText": speech,
            # "data": data,
            # "contextOut": [],
        "source": "fast-wave-17456"
        }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
