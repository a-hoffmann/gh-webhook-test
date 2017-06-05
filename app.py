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
import psycopg2
import urlparse

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)



#cur.execute("create TABLE test (id serial PRIMARY KEY, formula varchar);")





@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#def mapAction(action,parameters):
 
def weathercheck(param):
    city=param.get("geo-city")
    url="http://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=03db7a687f5d94e7f63cf259e88e42fa" % (city)
    result = urlopen(url).read()
    data = json.loads(result)
    speech="The weather in %s is %i degrees, with %s." % (city, param.get("main").get("temp"))
    return speech

def checkstocks(param):
    speech="I don't have the reference for that one yet"
    company=param.get("company")
    compdict={"givaudan":["VTX:GIVN","Swiss Francs"], "symrise": ["ETR:SY1","Euros"],"iff": ["NYSE:IFF","USD"]}
    if compdict[company]:
        url="https://www.google.com/finance/info?q=%s" % (compdict[company][0])
        result = urlopen(url).read()
        data = json.loads(result[3:])
        speech="The current stock price for %s is %s %s" % (company, data.get("l"), compdict[company][1])
    return l
                                                      

def processRequest(req):
    print("I have recieved it.")
    intent=req.get("result")
    action=intent.get("action")
    parameters=intent.get("parameters")
    print("my action is "+action)

    #just assign speech here, more data to follow
    if action=="weathercheck":
        speech=weathercheck(parameters)
    elif action=="check.sp":
        speech=checkstocks(parameters)
    else:
        speech="I don't have an answer for that one tet."
    
    return {
        "speech": speech,
        "displayText": speech,
            # "data": data,
            # "contextOut": [],
        "source": "fast-wave-17456"
    }



def oldProcessRequest(req):
    
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port)

    cur=conn.cursor()
    
    if req.get("result").get("action") == "read-recipe":
        ingreds=[]
        cur.execute("SELECT * from test;")
        for ingred in cur.fetchall():
            ingreds.append(ingred[1])
        speech = "The full current recipe is: "+', '.join(ingreds)+"."
        
    elif req.get("result").get("action") == "add-ingredient":
        #do another
        speech = "OK, I'll add %s of %s to the formula." % (req.get("result").get("parameters").get("unit-volume"), req.get("result").get("parameters").get("ingredient"))
        cur.execute("INSERT INTO test (formula) VALUES (%s)" %  (req.get("result").get("parameters").get("ingredient")))

    if len(speech)==0:
        speech="I'm sorry, something went wrong."

    conn.commit()
    cur.close()
    conn.close()
    
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
