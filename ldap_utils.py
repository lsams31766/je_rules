#ldap_utils.py
# ldap connection, queries ...

from ldap3 import ALL_ATTRIBUTES, LEVEL, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, BASE, NTLM, SUBTREE, ASYNC, ALL, Server, Connection, AUTO_BIND_TLS_BEFORE_BIND
from utils import *

DATASERVERS_ATTRIBS = ['cn','description','mdsgeneralconfiguration','mdsexternalruleparameters']
DATASERVERS_SEARCH_BASE = 'cn=Data Servers,cn=JoinEngine Configuration,ou=Injoinv8,ou=Config,o=bms.com'

CONNECTORS_ATTRIBS = ['cn','description','mdscvid','mdsviewlocation']
CONNECTORS_SEARCH_BASE = 'cn=Connector Views,cn=JoinEngine Configuration,ou=Injoinv8,ou=Config,o=bms.com'

ATTRIB_FLOW_SETS_ATTRIBS = ['cn','description','mdsfolder','mdsattributeflowconfigurationsetlist']
ATTRIB_FLOW_SETS_SEARCH_BASE = 'cn=ConfigurationSets,cn=Attribute Flow,cn=Shared Configuration,cn=JoinEngine Configuration,ou=Injoinv8,ou=Config,o=bms.com'

ATTRIB_FLOW_RULES_ATTRIBS = ['cn','mdsfolder','mdsattributeflowdirection','mdsgeneralconfiguration','mdsattributemappingpairs','mdsattributeflowselectioncriteria']
ATTRIB_FLOW_RULES_SEARCH_BASE = 'cn=Configurations,cn=Attribute Flow,cn=Shared Configuration,cn=JoinEngine Configuration,ou=Injoinv8,ou=Config,o=bms.com'

METADIR_FLOW_RULES_ATTRIBS = ['cn','mdsattributeflowtocv','mdsattributeflowtomv']
METADIR_FLOW_RULES_SEARCH_BASE = 'cn=bmsMV,cn=uslvlbmsasp177.net.bms.com,cn=Meta-Directories,cn=JoinEngine Configuration,ou=Injoinv8,ou=Config,o=bms.com'

METADIR_FLOW_RULES_SEARCH_BASE_UAT = 'cn=bmsMV,cn=usabhbmsvhz395.net.bms.com,cn=Meta-Directories,cn=JoinEngine Configuration,ou=InJoinv8,ou=Config,o=bms.com'


# CONSTRUCTED ATTRIBUTES
CA_PARENT_ATTRIBS = ['*']
CA_PARENT_SEARCH_BASE = 'cn=Constructed Attributes,cn=Shared Configuration,cn=JoinEngine Configuration,ou=Injoinv8,ou=Config,o=bms.com'

def getCon(env='prod'):
    if env == 'prod':
        server = Server('metaview.bms.com:10389', use_ssl=False)
        return Connection(server, 'cn=join engine,ou=nonpeople,o=bms.com','cpjevkprod',
            auto_bind=True)
    else:
        server = Server('metaview-uat.bms.com:10389', use_ssl=False)
        return Connection(server, 'cn=join engine,ou=nonpeople,o=bms.com', "cpjevkstag", auto_bind=True)

def search(con, search_base, search_filter, search_scope=SUBTREE, attributes=None, paged_size=500):
    return con.extend.standard.paged_search(search_base = search_base, search_filter=search_filter, search_scope=search_scope, attributes=attributes, paged_size=paged_size, generator=False)

def getDataservers():
    # example get dataservers 
    with getCon('prod') as con:
        search(con, search_base=DATASERVERS_SEARCH_BASE, search_filter='(objectclass=*)', search_scope=SUBTREE, attributes=DATASERVERS_ATTRIBS)
    results = []
    for entry in con.entries:
        data = {
            'dn': entry.entry_dn,
            'name': getv(entry, 'cn'),
            'description': getv(entry, 'description'),
            'url': entryToUrl(getv(entry, 'cn')),
            'script_location': entryToScriptLoc(getv(entry, 'mdsexternalruleparameters'))
        }
        if data['name'] == 'Data Servers':
            continue
        results.append(data)
    return results

#d = getDataservers()
#for item in d:
#    print(item['name'],item['url'])
