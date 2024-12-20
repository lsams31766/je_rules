#models.py
# holds all data pulled from config db
from utils import *
from ldap_utils import *
'''
            'dn': entry.entry_dn,
            'name': getv(entry, 'cn'),
            'description': getv(entry, 'description'),
            'url': entryToUrl(getv(entry, 'cn')),
            'script_location': entryToScriptLoc(getv(entry, 'mdsexternalruleparameters'))
'''
class Dataserver:
    all = []
    def __init__(self, dn, cn, description, mdsexternalruleparameters):
        self.dn = dn
        self.cn = cn
        self.name = cn
        self.description = description
        self.type = self.getType(cn)
        self.url = entryToUrl(cn)
        self.script_location = entryToScriptLoc(mdsexternalruleparameters)

    def __repr__(self): 
        return f"{self.name}, {self.url}, {self.type}"

    def getType(self,cn):
        if cn.startswith('MSDB'):
            return 'SQL_SERVER'
        if cn.startswith('LDAP'):
            return 'LDAP'
        if cn.startswith('PERL'):
            return 'PERL'
        return 'UKNOWN'

    @staticmethod
    def addServer(x):
        Dataserver.all.append(x)
    
    @staticmethod
    def getByType(aType):
        l = []
        for d in Dataserver.all:
            if d.type == aType:
               l.append(d)
        return l

    @staticmethod
    def load(env):
        # load from je config db (ldap)
        with getCon(env) as con:
            search(con, search_base=DATASERVERS_SEARCH_BASE, search_filter='(objectclass=*)', search_scope=SUBTREE, attributes=DATASERVERS_ATTRIBS)
        for entry in con.entries:
            dn = entry.entry_dn
            cn = getv(entry, 'cn')
            description = getv(entry, 'description')
            mdsexternalruleparameters = getv(entry, 'mdsexternalruleparameters')
            if cn == 'Data Servers':
                continue # not a data server
            a = Dataserver(dn, cn, description, mdsexternalruleparameters)
            Dataserver.addServer(a)

################################################################
class Connector:
    all = []
    def __init__(self, dn, cn, shortName, dataserverAssoc, description):
        self.dn = dn
        self.cn = cn
        self.name = cn
        self.shortName = shortName
        self.dataserverAssoc = self.getDsAssoc(dataserverAssoc)
        self.description = description

    def __repr__(self): 
        return f"{self.name}, {self.shortName}, {self.dataserverAssoc}"

    def getDsAssoc(self, dataserverAssoc):
        # chop off after l.com
        pos = dataserverAssoc.find('.com')
        if pos > 0:
            return dataserverAssoc[:pos+4]
        return dataserverAssoc

    @staticmethod
    def addConnector(x):
        Connector.all.append(x)
    
    @staticmethod
    def getByLongName(aLongName):
        if aLongName == '*':
            return '*'
        for c in Connector.all:
            if c.name.lower() == aLongName.lower():
               return c
        return None

    @staticmethod
    def getByShortName(aShortName):
        if aShortName == '*':
            return '*'
        for c in Connector.all:
            if c.shortName.lower() == aShortName.lower():
               return c
        return None

    @staticmethod
    def getTheShortName(aName):
        if aName == '*':
            return '*'
        for c in Connector.all:
            if c.name.lower() == aName.lower():
               return c.shortName
        return None


    @staticmethod
    def load(env):
        # load from je config db (ldap)
        with getCon(env) as con:
            search(con, search_base=CONNECTORS_SEARCH_BASE, search_filter='(objectclass=*)', search_scope=SUBTREE, attributes=CONNECTORS_ATTRIBS)
        for entry in con.entries:
            dn = entry.entry_dn
            cn = getv(entry, 'cn')
            if cn == 'Connector Views':
                continue
            description = getv(entry, 'description')
            shortName = getv(entry, 'mdscvid')
            dataserverAssoc = getv(entry,'mdsviewlocation')
            a = Connector(dn, cn, shortName, dataserverAssoc, description)
            Connector.addConnector(a)

################################################################
class AttribFlowSet:
    all = []
    def __init__(self, dn, cn, description, setlist, mdsfolder):
        self.dn = dn
        self.cn = cn
        self.name = cn
        self.description = description
        self.setlist = setlist.split(',')
        self.mdsfolder = mdsfolder

    def __repr__(self): 
        return f"{self.name}, {self.setlist}"

    @staticmethod
    def addAttribFlowSet(x):
        AttribFlowSet.all.append(x)
    
    @staticmethod
    def getByName(aName):
        for a in AttribFlowSet.all:
            if a.name.lower() == aName.lower():
               return a
        return None

    @staticmethod
    def getRuleSetForAtributeFlowRule(aName):
        for a in AttribFlowSet.all:
            sl = [s.lower() for s in a.setlist]
            if aName.lower() in sl:
                return a
        return None

    @staticmethod
    def load(env):
        # load from je config db (ldap)
        with getCon(env) as con:
            search(con, search_base=ATTRIB_FLOW_SETS_SEARCH_BASE, search_filter='(objectclass=*)', search_scope=SUBTREE, attributes=ATTRIB_FLOW_SETS_ATTRIBS)
        for entry in con.entries:
            dn = entry.entry_dn
            cn = getv(entry, 'cn')
            if cn == 'ConfigurationSets':
                continue
            description = getv(entry, 'description')
            setlist = getv(entry,'mdsattributeflowconfigurationsetlist')
            mdsfolder = getv(entry,'mdsfolder')
            a = AttribFlowSet(dn, cn, description, setlist, mdsfolder)
            AttribFlowSet.addAttribFlowSet(a)

################################################################

class MappingPair:
    def __init__(self, mapping_pairs):
        self.ignored_map_tokens = []
        self.all = self.get_tokens(mapping_pairs) 

    def __repr__(self): 
        return f"{self.first}, {self.second}, {self.flow_type}" 
    
    def get_tokens(self, mapping_pairs):
        global ignored_map_tokens
        ignored_map_tokens = []
        mp = mapping_pairs
        all_mps = []
        if type(mp) != list:
            if type(mp) != str:
                print('BAD MAPPING', mp)
                return None
            mp = [mp] # make it a list of length 1
        for m in mp:
            if type(m) != str:
                print('BAD MAPPING',m)
                continue
            # format "MyAdMail" "mail" 1
            pos = find_positions(m,'"')
            token1 = m[pos[0]+1:pos[1]]
            token2 = m[pos[2]+1:pos[3]]
            if "," in token1 or ";" in token1:
                self.ignored_map_tokens.append(token1)
                token1 = "UNKONWN"
            if "," in token2 or ";" in token2:
                token2 = "UKNOWN"
            all_mps.append((token1, token2))
        return all_mps

class AttribFlowRule:
    all = []
    def __init__(self, dn, cn, mdsfolder, direction, mdsgeneralconfiguration, mdsattributemappingpairs,criteria):
        self.dn = dn
        self.cn = cn
        self.name = cn
        self.mdsfolder = mdsfolder
        self.from_server, self.to_server = self.get_from_to_server(mdsgeneralconfiguration, self.name)
        self.direction = direction
        m = MappingPair(mdsattributemappingpairs)
        self.mapping_pairs = m.all
        self.criteria = criteria

    def __repr__(self): 
        return f"{self.name}, {self.direction} {self.from_server}->{self.to_server} "

    def get_from_to_server(self, config, ruleName):
        if not config or type(config) != list:
            return None, None
        from_server = None 
        to_server = None
        for c in config:
            # DestinationDataServer=LDAP://metaview.bms.com
            # SourceDataServer=PERL://ccure
            pos =  c.find('SourceDataServer=')
            if pos >= 0:
                pos = c.find('=') + 1
                from_server = c[pos:]
            pos =  c.find('DestinationDataServer=')
            if pos >= 0:
                pos = c.find('=') + 1
                to_server = c[pos:]

        # we want the short connector name using ruleName
        # get the Metadirectory entry where setname has ruleName
        # return the Metadirectory short name

        m = Metadirectory.getFromAttributeFlowName(ruleName)
        if m == None: # not mapped:
            return from_server, to_server
        shortName = Connector.getTheShortName(m.name)
        if 'metaview' in from_server.lower():
            from_server = 'MV'
            to_server = shortName
        else:
            from_server = shortName
            to_server = 'MV'
        return from_server, to_server

    @staticmethod
    def addAttribFlowRule(x):
        AttribFlowRule.all.append(x)
    
    @staticmethod
    def getByName(aName):
        for a in AttribFlowRule.all:
            if a.name.lower() == aName.lower():
               return a
        return None

    @staticmethod
    def getAllMappings():
        l = []
        for a in AttribFlowRule.all:
            l.extend(a.mapping_pairs)
        return l

    @staticmethod
    def getMappingByName(aName):
        l = []
        for a in AttribFlowRule.all:
            if a.name.lower() == aName.lower():
                return a.mapping_pairs
        return None

    @staticmethod
    def getRulesForAttribute(aAttribute):
        # search all mappings, for attribute
        # if attirbute in mapping, add to list of rules
        rulesFound = []
        for a in AttribFlowRule.all:
            for m in a.mapping_pairs:
                if aAttribute.lower() == m[0].lower():
                    rulesFound.append(a)
                if aAttribute.lower() == m[1].lower():
                    rulesFound.append(a)
        return rulesFound

    @staticmethod
    def getRulesForConnector(aConnector, direction='*'):
        # if connector is in rule, return the rule
        # Metadirectory maps connector to rule sets
        # Each rule set contains the rules

        rules_found = []
        aConnectorLongName = Connector.getByShortName(aConnector).name
        toMvRuleSet, toCvRuleSet = Metadirectory.getRulesFromName(aConnectorLongName)
        toMvRules = AttribFlowSet.getByName(toMvRuleSet).setlist if toMvRuleSet else []
        toMvRules = [t.lower() for t in toMvRules]
        toCvRules = AttribFlowSet.getByName(toCvRuleSet).setlist if toCvRuleSet else []
        toCvRules = [t.lower() for t in toCvRules]
        for a in AttribFlowRule.all:
            if direction == '*' or direction.lower() == 'tomv':
                if toMvRuleSet and a.name.lower() in toMvRules:
                   rules_found.append(a)
            if direction == '*' or direction.lower() == 'tocv':
                if toCvRuleSet and a.name.lower() in toCvRules:
                    rules_found.append(a)
        return rules_found

    @staticmethod
    def filterGivenRuleForAttribute(aAttribute, aConnector, aDirection, aFlowRule):
        # get the attribute's rule set 
        # get the Connector Name from Metadiretory given rule set
        # check check connector name small matches given connector name
        # check flow diretion matches using MetaDirectory
        
        # make sure flowrule contains the attribute
        mappings = AttribFlowRule.getMappingByName(aFlowRule)
        if mappings == None or mappings == 'None':
            return None
        # see if attribute in mapping
        found = False
        for m in mappings:
            if aAttribute.lower() == m[0] or aAttribute.lower() == m[1]:
                found = True
                break
        if not found:
            return None

        rules = AttribFlowRule.getRulesForAttribute(aAttribute)
        for r in rules:
            rs = AttribFlowSet.getRuleSetForAtributeFlowRule(r.name)
            cFound = Metadirectory.getConnectorsForRuleSet(rs.name)
            m = Metadirectory.getFromAttributeFlowName(r.name)
            # check directtion - either we are in toMv or toCv
            if aDirection.lower() == 'tocv' and r.direction.lower() == 'tomv':
                    return None
            if aDirection.lower() == 'tomv' and r.direction.lower() == 'tocv':
                    return None
            # check connector
            if aConnector == '*': # passed filter:
                return [aFlowRule]
            connectorSmallName = Connector.getByName(m.name).shortName
            cFound = [c.lower() for c in cFound]
            if connectorSmallName in cFound:
                return  [aFlowRule]
        return None # connector does not match
                    
    @staticmethod
    def filterRulesForAttribute(aAttribute, aConnector='*', aDirection='*', aFlowRule='*'):
        if aFlowRule != '*':
            return AttribFlowRule.filterGivenRuleForAttribute(aAttribute, aConnector=aConnector, aDirection=aDirection, aFlowRule=aFlowRule)
        rulesFound = set()
        # check for connector and direction math
        # 1) Get Metadirectory for connector
        # 2) Get toMv,toCV rule sets from Metadirectory
        # 3) Get the attribute flow rules from the rule sets
        # 4) If the attribute rule is not in these found rules, skip it        
        found_rule = False
        attrFlowRulesToSearch = []
        if aConnector == '*':
            connectorsToCheck = [a.name for a in Connector.all]
        else:
            connectorLongName = Connector.getByShortName(aConnector).name
            connectorsToCheck = [connectorLongName]
        for aConnector in connectorsToCheck:
            aConnectorLongName = Connector.getByLongName(aConnector).name
            toMvRuleSet, toCvRuleSet = Metadirectory.getRulesFromName(aConnectorLongName)
            # direction check
            if (toMvRuleSet != None) and ((aDirection == '*') or (aDirection.lower() == 'tomv')):
                attrFlowRuleSet = AttribFlowSet.getByName(toMvRuleSet)
                afr = [AttribFlowRule.getByName(a) for a in attrFlowRuleSet.setlist]
                for a in afr:
                    if a.direction.lower() == 'tomv':
                        found_rule = True
                        attrFlowRulesToSearch.append(a.name)
            if (toCvRuleSet != None) and ((aDirection == '*') or (aDirection.lower() == 'tocv')):
                attrFlowRuleSet = AttribFlowSet.getByName(toCvRuleSet)
                afr = [AttribFlowRule.getByName(a) for a in attrFlowRuleSet.setlist]
                for a in afr:
                    if a.direction.lower() == 'tocv':
                        found_rule = True
                        attrFlowRulesToSearch.append(a.name)
            if not found_rule:
                continue
                # connectors check
                if toMvRuleSet != None:
                    cFound = Metadirectory.getConnectorsForRuleSet(toMvRuleSet)
                else:
                    cFound = Metadirectory.getConnectorsForRuleSet(toCvRuleSet)
                if cFound == None or len(cFound) == 0:
                    continue
        if not found_rule:
            return None
        # now cehck the attribute flow rules found for matches in mapping pairs
        for a in attrFlowRulesToSearch:
            obj = AttribFlowRule.getByName(a)
            # if looking for all attributes, add all rules found
            if aAttribute == '*':
                 rulesFound.add(obj.name)
                 continue
            for m in obj.mapping_pairs:
                if aAttribute.lower() == m[0].lower():
                    rulesFound.add(obj.name)
                if aAttribute.lower() == m[1].lower():
                    rulesFound.add(obj.name)
        return rulesFound

    @staticmethod
    def load(env):
        # load from je config db (ldap)
        with getCon(env) as con:
            search(con, search_base=ATTRIB_FLOW_RULES_SEARCH_BASE, search_filter='(objectclass=*)', search_scope=SUBTREE, attributes=ATTRIB_FLOW_RULES_ATTRIBS)
        for entry in con.entries:
            dn = entry.entry_dn
            cn = getv(entry, 'cn')
            if cn == 'Configurations':
                continue
            mdsfolder = getv(entry,'mdsfolder')
            direction = getv(entry,'mdsattributeflowdirection')
            mdsgeneralconfiguration = getv(entry,'mdsgeneralconfiguration')
            mdsattributemappingpairs = getv(entry,'mdsattributemappingpairs')
            criteria = getv(entry,'mdsattributeflowselectioncriteria')
            a = AttribFlowRule(dn, cn, mdsfolder, direction, mdsgeneralconfiguration, mdsattributemappingpairs,criteria)
            AttribFlowRule.addAttribFlowRule(a)

################################################################
class ConstructedAttribute:
    all = []
    def __init__(self, dn, cn, ca_type, mdsrulesetlist, description, config, requirements, substitution ):
        self.dn = dn
        self.cn = cn
        self.name = cn
        self.ca_type = ca_type 
        self.mdsrulesetlist = mdsrulesetlist
        self.description = description
        self.config = config
        self.requirements = requirements
        self.substitution = substitution

    def __repr__(self): 
        return f"{self.name}, {self.ca_type} "

    @staticmethod
    def addConstructedAttribute(x):
        ConstructedAttribute.all.append(x)    

    @staticmethod
    def getByNameAndType(aName,aType):
        for c in ConstructedAttribute.all:
            if type(c.name) == list:
                for ci in c.name:
                    if ci.lower() == aName.lower() and c.ca_type.lower() == aType.lower():
                        return c
            else:
                if c.name.lower() == aName.lower() and c.ca_type.lower() == aType.lower():
                    return c
        return None

    @staticmethod
    def getChildCAs(parentName):
        parent = ConstructedAttribute.getByNameAndType(parentName,'RULE_SET')
        # pattern is x,parent.name
        found_cas = []
        search_pattern = f',{parent.dn}'
        search_pattern = search_pattern.replace(' ','')
        search_pattern = search_pattern.lower()
        for r in parent.mdsrulesetlist.split(','): # assure correct order of rules
            for c in ConstructedAttribute.all:
                if c.ca_type == ('RULE'):
                    # cn=set initial password,cn=FRDSUserPassword,cn=Constructed Attributes,cn=Shared Configuration,cn=JoinEngine Configuration,ou=Injoinv8,ou=Config,o=bms.com
                    dn = c.dn.replace(' ','')
                    dn = dn.lower()
                    if search_pattern in dn:
                        r_no_spaces = r.replace(' ','')
                        if dn.startswith("cn=" + r_no_spaces.lower()):
                            found_cas.append(c)
        return found_cas

    def load(env):
        # load from je config db (ldap)
        with getCon(env) as con:
            search(con, search_base=CA_PARENT_SEARCH_BASE, search_filter='(objectclass=*)', search_scope=SUBTREE, attributes=CA_PARENT_ATTRIBS)
        for entry in con.entries:
            dn = entry.entry_dn
            cn = getv(entry, 'cn')
            if 'mdsrulesetlist' in entry.entry_attributes:
                mdsrulesetlist = getv(entry,'mdsrulesetlist')
                ca_type = 'RULE_SET'
                a = ConstructedAttribute(dn, cn, ca_type, mdsrulesetlist, None, None, None, None)
                ConstructedAttribute.addConstructedAttribute(a)
            else:
                ca_type = 'RULE'
                description = getv(entry,'description')
                # 'mdsgeneralconfiguration', mdsgenericrulerequirements', 'mdsgenericrulesubstitution',
                config = getv(entry, 'mdsgeneralconfiguration')
                requirements = getv(entry, 'mdsgenericrulerequirements')
                substitution = getv(entry, 'mdsgenericrulesubstitution')
                a = ConstructedAttribute(dn, cn, ca_type, None, description, config, requirements, substitution)
                ConstructedAttribute.addConstructedAttribute(a)

################################################################
class Metadirectory:
    all = []
    def __init__(self, dn, cn, mdsattributeflowtocv=None, mdsattributeflowtomv=None):
        self.dn = dn
        self.cn = cn
        self.name = cn
        self.mdsattributeflowtocv = mdsattributeflowtocv
        self.mdsattributeflowtomv = mdsattributeflowtomv

    def __repr__(self): 
        return f"{self.name}"

    @staticmethod
    def addMetadirectory(x):
        Metadirectory.all.append(x)    

    @staticmethod
    def getByName(aName):
        for m in Metadirectory.all:
            if m.name.lower() == aName.lower():
               return m
        return None

    @staticmethod
    def getFromAttributeFlowName(aName):
        for m in Metadirectory.all:
            for sl in [m.mdsattributeflowtocv, m.mdsattributeflowtomv]:
                if sl != None:
                    set_list = AttribFlowSet.getByName(sl).setlist
                    set_list_lower = [s.lower() for s in set_list]
                    if aName.lower() in set_list_lower:
                        return m
        return None

    @staticmethod
    def getRulesFromName(aName):
        toMv = None
        toCv = None
        m = Metadirectory.getByName(aName)
        if not m:
            return None, None
        if m.mdsattributeflowtocv != None:
            toCv = m.mdsattributeflowtocv
        if m.mdsattributeflowtomv != None:
            toMv = m.mdsattributeflowtomv
        return toMv, toCv

    @staticmethod
    def getConnectorsForRuleSet(aName):
        foundConnectors = []
        for m in Metadirectory.all:
            if m.mdsattributeflowtocv != None:
                if aName.lower() == m.mdsattributeflowtocv.lower():
                    foundConnectors.append(m)
            if m.mdsattributeflowtomv != None:
                if aName.lower() == m.mdsattributeflowtomv.lower():
                    foundConnectors.append(m)
        return foundConnectors

    @staticmethod
    def load(env):
        # load from je config db (ldap)
        with getCon(env) as con:
            if env.lower() == 'prod':
                search_base = METADIR_FLOW_RULES_SEARCH_BASE
            else:
                search_base = METADIR_FLOW_RULES_SEARCH_BASE_UAT
            search(con, search_base=search_base, search_filter='(objectclass=*)', search_scope=SUBTREE, attributes=METADIR_FLOW_RULES_ATTRIBS)
        for entry in con.entries:
            dn = entry.entry_dn
            cn = getv(entry, 'cn')
            mdsattributeflowtocv = getv(entry, 'mdsattributeflowtocv')
            mdsattributeflowtomv = getv(entry, 'mdsattributeflowtomv')
            m = Metadirectory(dn, cn, mdsattributeflowtocv, mdsattributeflowtomv)
            Metadirectory.addMetadirectory(m)

###############################################

def load_rules(env):
    Dataserver.load(env)
    Connector.load(env)
    Metadirectory.load(env)
    AttribFlowSet.load(env)
    AttribFlowRule.load(env)
    ConstructedAttribute.load(env)

def remove_rules():
    Dataserver.all = []
    Connector.all = []
    Metadirectory.all = []
    AttribFlowSet.all = []
    AttribFlowRule.all = []
    ConstructedAttribute.all = []

#load_rules()

# test code
#for d in Dataserver.all:
#    print(d)
#print('LDAP dataservers are: ',Dataserver.getByType('LDAP'))

#for c in Connector.all:
#    print(c)
#print('entwr is: ', Connector.getByShortName('entwr'))
#TODO - a module will be built to join models
#       such as: give me dataserver details, given connector shortName

#print('CDtoMV set is: ', AttribFlowSet.getByName('cdtomv'))

# print('CCUREtomv rule is: ', AttribFlowRule.getByName('CCUREtomv'))

#print('CONSUtoMV-workstyle ca is ', ConstructedAttribute.getByNameAndType('CONSUtoMV-workstyle','RULE_SET'))
#print('CONSUtoMV-HOM-FLD-NLS ca is ', ConstructedAttribute.getByNameAndType('HOM-FLD-NLS','RULE'))
