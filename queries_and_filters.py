#queries_and_filters.py
from models import *
from presentation import *
import operator

currentEnv = 'prod'

# load_rules()

# some easy queries
def get_all_connectors():
    return [c.shortName for c in Connector.all]

def get_all_constructed_attributes():
    ca_set = set()
    for ca in ConstructedAttribute.all:
        if ca.ca_type == 'RULE_SET':
            if ca.name.lower() not in ca_set:
                ca_set.add(ca.name)
    return ca_set

def get_all_attributes():
    # look in mappings for attribute flow
    # only take unique names
    unique_attrs = set()
    # for now do all the work here, may want to move some of this to the del
    ca = get_all_constructed_attributes()
    ca_lower = [c.lower() for c in ca] # convert to lower for comparison
    mp = AttribFlowRule.getAllMappings()
    for m in mp:
        for t in m:
            if (t.lower() not in unique_attrs) and (t.lower() not in ca_lower):
                unique_attrs.add(t)
    return unique_attrs

def get_all_rules():
    # get rhe rule sets, get the rules within the set
    rs = AttribFlowSet.all
    for r in rs:
        print(r.name)
        print("   ",r.setlist)

def apply_filter(aAttribute, aConnector='*', aDirection='*', aFlowRule='*'):
   r = AttribFlowRule.filterRulesForAttribute(aAttribute, aConnector, aDirection, aFlowRule)
   return r

def get_assoc_constructed_attribute(aAttribute, aConnector='*'):
    # get CA's associated with attribute
    # return the CA's and the CA rules
    ca_found = set()
    ca_set = get_all_constructed_attributes()
    ca_set_lower = [c.lower() for c in ca_set]
    for a in AttribFlowRule.all:
        # if connector chosen, get allowable rules
        conOk = False
        if aConnector == '*':
            conOk = True
        else:
            aConnectorLongName = Connector.getByShortName(aConnector).name
            toMvRuleSet, toCvRuleSet = Metadirectory.getRulesFromName(aConnectorLongName)
            if toMvRuleSet:
                toMvRuleSet = AttribFlowSet.getByName(toMvRuleSet)
                toMvRules = [t.lower() for t in toMvRuleSet.setlist]
                if a.name.lower() in toMvRules:
                    conOk = True
            if toCvRuleSet:
                toCvRuleSet = AttribFlowSet.getByName(toCvRuleSet)
                toCvRules = [t.lower() for t in toCvRuleSet.setlist]
                if a.name.lower() in toCvRules:
                    conOk = True
        if not conOk:
            continue

        # now check in attribute in mapping pair            
        for m in a.mapping_pairs:
            if (aAttribute.lower() == m[0].lower()) and (m[1].lower() in ca_set_lower):
                ca_found.add(m[1])
            if (aAttribute.lower() == m[1].lower()) and (m[0].lower() in ca_set_lower):
                ca_found.add(m[0])
    if len(ca_found) == 0:
        return None
    else:
        # get rule set names
        rule_sets = []
        for c in ca_found:
           rule_sets.append(ConstructedAttribute.getByNameAndType(c,'RULE_SET'))
        sorted_rule_sets = sorted(rule_sets, key=operator.attrgetter('name'))
        return(sorted_rule_sets)

def check_env_switched(newEnv):
    # if environment changed, load data from that config db
    global currentEnv
    if currentEnv == newEnv:
        return
    print(f'..LOADING RULES for {newEnv}...', flush=True)
    remove_rules()
    load_rules(newEnv)
    print(f'..LOADING RULES DONE!', flush=True)
    currentEnv = newEnv
    return currentEnv
    
if __name__ == "__main__":
    load_rules('prod')
    # {'connector': '*', 'direction': '*', 'attribute': 'mail', 'flowRule': '*', 'view': 'text', 'env': 'uat', 'showAttribute': False}
    r =  apply_filter('*', 'FRU', 'toCV','*') 
    #r =  apply_filter('bmscity', '*', '*', 'MVtoConsumer') 
    print('rules for FRU: ')
    for item in r:
        print(print_rule(item, showAttribute=True))
    
    #print(GetTreeForFilteredRule(r))
    #load_rules('prod')
#rules = AttribFlowRule.getRulesForConnector('CONSU')
#for r in rules:
#    print(r)
    #ca_rules = get_assoc_constructed_attribute('userpassword','*')
#print(len(ca_rules))
    #for c in ca_rules:
        #s = print_constructed_attribute_rule(c)
        #print(s)
        #print('---')

    #ca_rules = get_assoc_constructed_attribute('mdsentityowner')
    #ca_rules = get_assoc_constructed_attribute('bmsaduser')
    #ca_rules = get_assoc_constructed_attribute('bmscity','CONSU')
    #print('CONSTRUCTED ATTRIBUTES associated with telephonenumber:')
    #s = ''
    #for item in ca_rules:
        #s = print_constructed_attribute_rule(item)
        #print(s)
    #j = GetTreeForConstructedAttributeRuleSet(ca_rules)
    #print(j)
    #content: {'connector': '*', 'direction': '*', 'attribute': 'userpassword', 'flowRule': '*'}
    # content: {'connector': '*', 'direction': 'Both', 'attribute': 'bmscity', 'flowRule': '*'}
    # content: {'connector': '*', 'direction': '*', 'attribute': 'standardcode', 'flowRule': 'REFDtoMV-georegion', 'view': 'tree'}
    # r =  apply_filter('*', 'SECUR', '*', '*')
    #r =  apply_filter('bmscity', 'CONSU', 'toCv')
    #r =  apply_filter('bmsid', 'CONSU', 'ToCV','*') 
    # r =  apply_filter('bmscity', '*', '*', 'MVtoConsumer') 
    #print('rules for SECUR: ')
    #for item in r:
        #print(print_rule(item, showAttribute=True))
    #print(GetTreeForFilteredRule(r))
#s = get_all_connectors()
#s = '\n'.join(s)
#print(s)

#ca = list(get_all_constructed_attributes())
# print some
#for c in ca[:5]:
#    print(c)

#ca = list(get_all_constructed_attributes())

#attrs = list(get_all_attributes())
# print some
#print('-----------------------------')
#for a in sorted(attrs, key=str.casefold):
#for a in sorted(attrs):
    #print(a)

#get_all_rules()
