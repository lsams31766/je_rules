#!/usr/bin/python3
import sys
import logging as l
from functools import wraps
from io import StringIO
import os
import operator

from models import *
from presentation import *
from queries_and_filters import get_all_attributes, get_assoc_constructed_attribute, apply_filter, check_env_switched

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_USER = 'samuell3'
APP_LOG_PATH = os.path.join(BASE_DIR, 'logs', 'app.log')
LOG_LEVEL = l.INFO

def setupLogger(name, logFile, formatter, level=LOG_LEVEL):
    handler = l.FileHandler(logFile)
    handler.setFormatter(formatter)
    logger = l.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

appLog = setupLogger('appInfo', APP_LOG_PATH, l.Formatter('%(asctime)s: %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))


from flask import Flask, render_template, request, jsonify, url_for, redirect, g, abort, send_file, Response
from flask_cors import CORS, cross_origin

import traceback

app = Flask(__name__)
CORS(app)

@app.before_request
def auth():
    g.user = str(request.headers.get('Smuid'))

@app.route('/', methods=['GET'])
def index():
    print("### index ###")
    return render_template('index.html')

@app.route('/changeEnv', methods=['POST'])
def changeEnv():
    print("### changeEnv ###")
    content = request.json
    env = content['env']
    newenv = check_env_switched(env)
    return jsonify({
            "newenv": newenv
    })

@app.route('/getConnectors', methods=['GET'])
def getConnectors():
    print('### GetConnectors ###')
    s = [c.shortName for c in Connector.all]
    s_sorted = [a for a in sorted(s, key=str.casefold)]
    print(f"GetConnectors found {len(s_sorted)} connectors")
    return jsonify({
            "items": s_sorted
    })

@app.route('/getAttributes', methods=['GET'])
def getAttributes():
    print('### GetAttributes ###')
    a = get_all_attributes()
    a_sorted = [a for a in sorted(a, key=str.casefold)]
    print(f"getAttributes found {len(a_sorted)} attributes")
    return jsonify({
            "items": a_sorted
    })

@app.route('/getFlowRules', methods=['GET'])
def getAttrigetFlowRulesutes():
    print('### getFlowRules ###')
    rs = AttribFlowSet.all
    flowRules = []
    for r in rs:
        flowRules.extend(r.setlist)
    flowRules_sorted = sorted(flowRules, key=str.casefold)
    #flowRules_sorted = [f.name for f in flowRules_sorted]
    print(f"getFlowRules found {len(flowRules_sorted)} flow rules")
    return jsonify({
            "items": flowRules_sorted
    })

@app.route('/getConstructedAttributes', methods=['POST'])
def getConstructedAttributes():
    print('### getConstructedAttributes ###')
    content = request.json
    view = content['view']
    env = content['env']
    # will receive connnector and attribute
    # attribute cannot be *
    print("content:",content)
    if 'attribute' not in content:
        print("Error missing attribute")
        return jsonify({"item": 'ERROR - Missing attribute selection'})
    if content['attribute'] == '*':
        print('Error attribute cannot be * for constructed attribute selection')
        return jsonify({"item": 'ERROR - attribute cannot be "*"'})
    if 'connector' not in content:
        aConnector = '*'
    else:
        aConnector = content['connector']
    aAttribute = content['attribute']
    ca_rules = get_assoc_constructed_attribute(aAttribute,aConnector)
    if (not ca_rules) or len(ca_rules) == 0:
        return jsonify({"item":"No matches found"})
    #
    #s = print_constructed_attribute_rule(ca_rules[0])
    if view == 'tree':
        # test for now static data
        newData = GetTreeForConstructedAttributeRuleSet(ca_rules)
        return jsonify({
            "item": newData
        })
    s = ''
    for item in ca_rules:
        s += print_constructed_attribute_rule(item)
    return jsonify({
            "item": s
    })

@app.route('/applyFilter', methods=['POST'])
@cross_origin()
def applyFilter():
    print('### applyFilter ###')
    content = request.json
    # will receive connnector and attribute
    # attribute cannot be *
    print("content:",content)
    if 'attribute' not in content:
        print("Error missing attribute")
        return jsonify({"item": 'ERROR - Missing attribute selection'})
    #if content['attribute'] == '*':
    #    print('Error attribute cannot be * for constructed attribute selection')
    #    return jsonify({"item": 'ERROR - attribute cannot be "*"'})
    attribute = content['attribute']
    connector = content['connector']
    direction = content['direction']
    flowRule = content['flowRule']
    view = content['view']
    env = content['env']
    showAttribute = content['showAttribute']
    check_env_switched(env)
    print("showAttribute", showAttribute)
    r = apply_filter(attribute, connector, direction, flowRule)
    if r == None or r == 'None':
        return jsonify({
            "item": "No Matches"
        })

    if view == 'tree':
        newData = GetTreeForFilteredRule(r, showAttribute=showAttribute)
        return jsonify({
            "item": newData
        })

    s = f'<span class="vertical-center rule-text">Apply filter - attribute: {attribute} connector: {connector} direction: {direction}  </span>'
    for item in r:
        s += print_rule(item,showAttribute)
    return jsonify({
            "item": s
    })


if __name__ == "__main__":
    load_rules('prod')
    app.debug = True
    appLog.info("LOADING!")
    app.run(host="0.0.0.0", port=8001, debug=True)
 
