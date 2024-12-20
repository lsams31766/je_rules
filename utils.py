#utils.py

def getv(entry, attr):
    if attr in entry and entry[attr].values:
        if type(entry[attr].values) == list and len((entry[attr].values)) == 1:
            return entry[attr].values[0] # single item
        return entry[attr].values # list
    return None

def entryToUrl(cn):
    # get url form the cn
    if cn.startswith('LDAP'):
        pos1 = 7
        pos2 = cn.find(':',pos1)
        if pos2 > pos1:
            return cn[pos1:pos2]
        else:
            return cn[pos1:]
    if cn.startswith('MDSDB'):
        pos1 = 7
        pos2 = cn.find('&',pos1)
        if pos2 > pos1:
            return cn[pos1:pos2]
        else:
            return cn[pos1:]
    if cn.startswith('PERL'):
        pos1 = 7
        return cn[pos1:]
    # not found 
    return ''

def entryToScriptLoc(mdsexternalruleparameters):
    # get perl script location from mdsexternalruleparameters
    # ExternalLocation=/opt/BMSapps/metaconnect/scripts/beeline.pl
    if not mdsexternalruleparameters:
        return None
    for m in mdsexternalruleparameters:
        if m.startswith('ExternalLocation'):
            pos1 = 17
            return m[17:]
    return ''

def find_positions(aString, aCharacter):
    return [i for i, ltr in enumerate(aString) if ltr == aCharacter]


