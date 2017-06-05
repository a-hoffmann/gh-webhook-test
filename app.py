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
    print("city is "+city)
    url="http://api.openweathermap.org/data/2.5/weather?q={0}&units=metric&appid=03db7a687f5d94e7f63cf259e88e42fa".format(city)
    result = urlopen(url).read()
    data = json.loads(result)
    speech="The weather in {0} is {1} degrees, with {2}.".format(city, param.get("main").get("temp"), param.get("weather")[0].get("description"))
    return speech

def checkstocks(param):
    speech="I don't have the reference for that one yet."
    company=param.get("company")
    compdict={"givaudan":["VTX:GIVN","Swiss Francs"], "symrise": ["ETR:SY1","Euros"],"iff": ["NYSE:IFF","USD"]}
    if compdict[company]:
        url="https://www.google.com/finance/info?q={0}".format(compdict[company][0])
        result = urlopen(url).read()
        data = json.loads(result[3:])
        speech="The current stock price for {0} is {1} {2}.".format(company, data.get("l"), compdict[company][1])
    return speech
                                                      

def processRequest(req):
    intent=req.get("result")
    action=intent.get("action")
    parameters=intent.get("parameters")

    #just assign speech here, more data to follow
    if action=="weathercheck":
        speech=weathercheck(parameters)
    elif action=="check.sp":
        speech=checkstocks(parameters)
    elif action=="ping":
        speech="Ping!"
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
