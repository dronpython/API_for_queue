from ldap3 import (
    Server,
    Connection,
    SIMPLE,
    SYNC,
    ASYNC,
    SUBTREE,
    ALL,
    RESTARTABLE
)

from core.settings import config


class LDAP:
    def __init__(self, server, domain, login, password, defaultTree, defaultTreeCA):
        self.server = server
        self.domain = domain
        self.login = login
        self.password = password
        self.defaultTree = defaultTree
        self.defaultTreeCA = defaultTreeCA

        self.lconn = False
        self.attributes = ["*"]
        self.group_attributes = ["cn", "distinguishedName"]
        self.group_attributes_all = ['cn', 'dSCorePropagationData', 'description', 'distinguishedName', 'groupType',
                                     'instanceType', 'managedBy', 'member', 'name', 'objectCategory', 'objectClass',
                                     'objectGUID', 'objectSid', 'sAMAccountName', 'sAMAccountType', 'uSNChanged',
                                     'uSNCreated', 'whenChanged', 'whenCreated']
        self.__connect(self.server, self.domain, self.login, self.password)

    def __connect(self, server, domain, login, password):
        try:
            server_connection = Server(server)
            self.lconn = Connection(
                server_connection,
                user=domain + "\\" + login,
                password=password,
                authentication="NTLM",
                client_strategy=RESTARTABLE,
            )
            if self.lconn.bind():
                print("-= libldap: __init__: connected to " + str(server))
                print(
                    f">> connectors.libldap.LDAP.__connect >> Successfully connected to LDAP >> domain = {domain}; server = {str(server)}"
                )
            else:
                print(
                    f">> connectors.libldap.LDAP.__connect >> [!] Failed to connect to LDAP >> domain = {domain}; server = {str(server)}"
                )
                print("!!!LDAP: INITIALIZE FAIL!!!! ")
        except Exception as EE:
            print("!!!LDAP: INITIALIZE FAIL!!!! " + str(EE))
            print(
                f">> connectors.libldap.LDAP.__connect >> [!] Exception occured while connecting to LDAP >> domain = {domain}; server = {str(server)}"
            )
            print(
                f">> connectors.libldap.LDAP.__connect >> [!] Exception occured while connecting to LDAP >> domain = {domain}; server = {str(server)}; Error = {str(EE)}"
            )

        self.attributes = [
            "objectClass",
            "distinguishedName",
            "cn",
            "department",
            "description",
            "displayName",
            "distinguishedName",
            "givenName",
            "mail",
            "mailNickname",
            "middleName",
            "name",
            "primaryGroupID",
            "sAMAccountName",
            "sAMAccountType",
            "sn",
            "userAccountControl",
            "userPrincipalName",
            "proxyAddresses",
            "msExchExtensionAttribute20",
            "msExchExtensionAttribute21",
            "msExchExtensionAttribute22",
            "msExchExtensionAttribute23",
            "extensionAttribute14",
            "userAccountControl",
            "employeeID",
            "manager",
            "title",
            "lockoutTime",
            "msDS-User-Account-Control-Computed",  # added new attr
        ]

    def __reconnect(self):
        if not self.lconn:
            print(f">> connectors.libldap.LDAP.__reconnect >> ")
            print("!!!LDAP: INIT RECONNECT!!!! ")
            self.__connect(self.server, self.domain, self.login, self.password)

    def _conn(self):
        if not self.lconn:
            self.__reconnect()
        if not self.lconn:
            raise ConnectionError(
                f"[!] Failed to connect to LDAP >> domain = {self.domain}; server = {str(self.server)} >> try again later"
            )
        return self.lconn

    def _check_auth(self, server, domain, login, password):
        try:
            lconn = Connection(
                server,
                user=domain + "\\" + login,
                password=password,
                authentication="NTLM",
            )
            if lconn.bind():
                print(f"-= libldap: _check_auth: success; user = {login}")
                print(
                    f">> connectors.libldap.LDAP._check_auth >> Successfully connected to LDAP >> domain = {domain}; server = {str(server)}; user = {login}"
                )
                return True
            else:
                print(
                    f">> connectors.libldap.LDAP._check_auth >> [!] Failed to connect to LDAP >> domain = {domain}; server = {str(server)}; user = {login}"
                )
                print(f"-= libldap: _check_auth: failed; user = {login}")
                return False
        except Exception as EE:
            print(
                f"-= libldap: _check_auth: Exception; user = {login}; Error = {str(EE)}"
            )
            print(
                f">> connectors.libldap.LDAP._check_auth >> [!] Exception occured while connecting to LDAP >> domain = {domain}; server = {str(server)}"
            )
            print(
                f">> connectors.libldap.LDAP._check_auth >> [!] Exception occured while connecting to LDAP >> domain = {domain}; server = {str(server)}; Error = {str(EE)}"
            )
            return False


ldap = LDAP(
    server=config.fields.get('servers').get('ldap'),
    domain='SIGMA',
    login=config.fields.get('cred').get('domain_auth').get('login'),
    password=config.fields.get('cred').get('domain_auth').get('password'),
    defaultTree=config.fields.get('ldap').get('search_tree'),
    defaultTreeCA=config.fields.get('ldap').get('search_tree_ca'),
)
