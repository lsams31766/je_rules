#presentation.py
from models import *

def print_all_attrib_flows(attribFlowRule):
    #  FORMAT:
    # attrib | from Connector | Direction | To Connector | To Attribute | Rule Name | Criteia
    a = attribFlowRule
    rs = AttribFlowSet.getRuleSetForAtributeFlowRule(a.name)
    if rs == None: # not mapped
        return ''
    cons = Metadirectory.getConnectorsForRuleSet(rs.name)
    s = ''
    for c in cons:
        shortName = Connector.getTheShortName(c.name)
        if a.direction.lower() == 'tomv':
            s += f"<b>{a.name}: MV <- {shortName}  </b> <br />"
        else:
            s += f"<b>{a.name}: MV -> {shortName} </b> <br />"
    # break critiera into multiple lines, and indent them
    c_list = breakLongString(cleanJeText(str(a.criteria)),';',100)
    s += f'CRITERIA: '
    indent = '&nbsp' * 14
    s += f"{c_list[0]} <br />"
    for c in c_list[1:]:
        s += f"{indent} {c} <br />"
    for m in a.mapping_pairs:
        if a.direction.lower() == 'tomv':
            s += f"{m[1]} <- {m[0]} <br />"
        else:
            s += f"{m[0]} -> {m[1]} <br />"
    s += '-' * 160 + '<br />'
    return s

def print_rule(rule, showAttribute=False):
    # show rule name, from to servers, criteria
    # IF showAttribute is True show:
    #  from attrib | from Connector | Direction | To Connector | To Attribute | Rule Name | Criteia
    a = AttribFlowRule.getByName(rule)
    # if have a flow rule, need to see what rule set it is in
    # with the rule set we can figure out the from to connectors
    # can be multiple from to's for a rule
    rs = AttribFlowSet.getRuleSetForAtributeFlowRule(a.name)
    if rs == None: # not mapped
        return ''
    cons = Metadirectory.getConnectorsForRuleSet(rs.name)

    if showAttribute:
        return print_all_attrib_flows(a)

    s = ''
    for c in cons:
        shortName = Connector.getTheShortName(c.name)
        if a.direction.lower() == 'tomv':
            s += f"<b>{a.name}: MV <- {shortName}  </b> <br />"
        else:
            s += f"<b>{a.name}: MV -> {shortName} </b> <br />"
    s += f'{a.criteria} <br />'
    s += '-' * 160 + '<br />'
    return s

def print_constructed_attribute_rule(ca_rule_set):
    # print name of rule set, find it's rules, print each rule
    s = '&nbsp &nbsp &nbsp <b>' + ca_rule_set.name + '</b> <br />'
    rules = ConstructedAttribute.getChildCAs(ca_rule_set.name)
    if rules:
        for r in rules:
            s += f"   {r.name}<br />"
            s+= f"   REQUIRES: {r.requirements}<br />"
            s+= f"   OUTPUT: {r.substitution}<br />"
            s += "----------<br />"
    s = s[:-6] + "-" * 160 + "<br />"
    # we need to esacape out <U> and <L> type chars
    s = s.replace('<U>','&lt;U&gt;')
    s = s.replace('<L>','&lt;L&gt;')
    return s

def TestTreeData():
    # sample data for the jstree for testing
    dataDict = {'data':
    [
        {
            "text" : "TEST-MVtoFRDS-Consultant: MV -> frds",
            "state" : { "opened" : True },
            "children" : 
            [
                {"text" : "TEST-(%objectclass%==bmsentperson)"},
                { "text" : "(%MDS.PVRN%==ou\=people)"},
                { "text" : "((%MDS.OPERATION%==JoinFromMVToCV)"},
                { "text" : "(%bmspersonassociation%==Consultant)"}
            ]
        },
        {
            "text" : "TEST2-CDtoMV-nonpeople: Consu -> MV",
            "state" : { "opened" : True },
            "children" : 
            [
                {"text" : "TEST2-(%objectClass%==inetOrgPerson)"},
                { "text" : "((%MDS.OPERATION%==AddFromCVToMV) OR (%MDS.OPERATION%==UpdateFromCVToMV))"},
                { "text" : "(%MDS.PVRN%==ou\=nonpeople)"}
            ]
        }
    ]}
    return dataDict

def cleanJeText(s):
    s = s.replace('<U>','&lt;U&gt;')
    s = s.replace('<L>','&lt;L&gt;')
    return s

# for buidling Tree
idNbr = 0 # global var
def idnbr(n):
    return "id" + str(n)

def addTreeNode(parent, text, state={"opened": True}, icon=None):
    global idNbr
    item =  {
            "id": idnbr(idNbr),
            "parent": parent,
            "text" : text,
            "state" : state
        }
    if icon != None:
        item['icon'] = icon
    idNbr += 1
    return item, idNbr - 1

def breakLongString(longStr, token ,maxLength):
    if longStr == 'None':
        return ['']
    outList = []
    strSplit = longStr.split(token)
    curStr = ''
    for item in strSplit:
        if len(item) + len(curStr) > maxLength:
            if len(curStr) > 0:
                outList.append(curStr)
            curStr = item
        else:
            curStr = curStr + ';' + item
            if curStr.startswith(';'):
                curStr = curStr[1:]
    outList.append(curStr)
    # check for OR or AND in each item and exceeding size
    outList2 = []
    for item in outList:
        if len(item) < maxLength:
            outList2.append(item)
        else:
            # split at or or and, whichever is first
            if 'OR' in item:
                splitter = 'OR'
            else:
                splitter = 'AND'
            itemSplit = item.split(splitter)
            # add splitter value to all but last one
            for i in range(len(itemSplit) - 1):
                itemSplit[i] += splitter
            outList2.extend(itemSplit)
    return outList2

def GetTreeForConstructedAttributeRuleSet(ca_rule_set):
    # return rules in tree data format
    '''
    'data' : 
    [
        { "id" : "ajson1", "parent" : "#", "text" : "Simple root node","state" : { "opened" : true }, },
        { "id" : "ajson2", "parent" : "#", "text" : "Root node 2","state" : { "opened" : true }, },
        { "id" : "ajson3", "parent" : "ajson2", "text" : "Child 1","state" : { "opened" : true }, },
        { "id" : "ajson4", "parent" : "ajson2", "text" : "Child 2" },
        { "id" : "ajson5", "parent" : "ajson3", "text" : "Child 3" }
    ]
    '''
    global idNbr
    idNbr = 1
    outputData = []
    for rule_set in ca_rule_set:
        item, parentIdNbr = addTreeNode('#', rule_set.name)
        outputData.append(item)
        rules = ConstructedAttribute.getChildCAs(rule_set.name)
        if rules:
            for r in rules:
                parent = idnbr(parentIdNbr)
                item, childIdNbr = addTreeNode(parent, r.name)
                outputData.append(item)

                reqList = breakLongString(cleanJeText(str(r.requirements)),';',100)
                for rl in reqList:
                    item, _ = addTreeNode(idnbr(childIdNbr), "REQUIRES: "  +  rl, icon='jstree-file')
                    outputData.append(item)

                item, _ = addTreeNode(idnbr(childIdNbr), "OUTPUT: " + cleanJeText(str(r.substitution)), icon='jstree-file')
                outputData.append(item)
    dataDict = {'data':outputData}
    return dataDict

def GetTreeForAttribFlowRules(rules):
    # top level is rule name 
    # next level is critiera (fixed length)
    # next level is attributes: mv_attrib <-- (or -->) cv_attrib
    global idNbr
    idNbr = 1
    outputData = []
    for rule in rules:
        a = AttribFlowRule.getByName(rule)
        rs = AttribFlowSet.getRuleSetForAtributeFlowRule(a.name)
        if rs == None: # not mapped
            continue
        cons = Metadirectory.getConnectorsForRuleSet(rs.name)
        for c in cons:
            shortName = Connector.getTheShortName(c.name)
            if a.direction.lower() == 'tomv':
                s = f"{a.name}: MV <- {shortName} "
            else:
                s = f"{a.name}: MV -> {shortName}"
            item, parentIdNbr = addTreeNode('#', s)
            outputData.append(item)
        # add criteria
        critList = breakLongString(cleanJeText(str(a.criteria)),';',100)
        cnbr = 0
        for cl in critList:
            if cnbr > 0 : # part of previous criteria
                item, _ = addTreeNode(idnbr(parentIdNbr), "&nbsp &nbsp &nbsp" + cl, icon='jstree-file')
            else:
                item, _ = addTreeNode(idnbr(parentIdNbr), "CRITERIA: "  +  cl, icon='jstree-file')
            cnbr += 1
            outputData.append(item)
        # add attributes 
        for m in a.mapping_pairs:
            if a.direction.lower() == 'tomv':
                s = f"{m[1]} <- {m[0]}"
            else:
                s = f"{m[0]} -> {m[1]}"
            item, _ = addTreeNode(idnbr(parentIdNbr), s,  icon='jstree-file')
            outputData.append(item)

    dataDict = {'data':outputData}
    return dataDict

def GetTreeForFilteredRule(rules, showAttribute=False):
    if showAttribute == True:
        return GetTreeForAttribFlowRules(rules)
    global idNbr
    idNbr = 1
    outputData = []
    for rule in rules:
        a = AttribFlowRule.getByName(rule)
        rs = AttribFlowSet.getRuleSetForAtributeFlowRule(a.name)
        if rs == None: # not mapped
            continue
        cons = Metadirectory.getConnectorsForRuleSet(rs.name)

        for c in cons:
            shortName = Connector.getTheShortName(c.name)
            if a.direction.lower() == 'tomv':
                s = f"{a.name}: MV <- {shortName} "
            else:
                s = f"{a.name}: MV -> {shortName}"
            item, parentIdNbr = addTreeNode('#', s)
            outputData.append(item)

        critList = breakLongString(cleanJeText(str(a.criteria)),';',100)
        cnbr = 0
        for cl in critList:
            if cnbr > 0 : # part of previous criteria
                item, _ = addTreeNode(idnbr(parentIdNbr), "&nbsp &nbsp &nbsp" + cl, icon='jstree-file')
            else:
                item, _ = addTreeNode(idnbr(parentIdNbr), "CRITERIA: "  +  cl, icon='jstree-file')
            cnbr += 1
            outputData.append(item)
    dataDict = {'data':outputData}
    return dataDict
