#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: keycloak_user_federation

short_description: Allows administration of Keycloak user federations using Keycloak API

version_added: 3.7.0

description:
  - This module allows you to add, remove or modify Keycloak user federations using the Keycloak REST API. It requires access
    to the REST API using OpenID Connect; the user connecting and the client being used must have the requisite access rights.
    In a default Keycloak installation, admin-cli and an admin user would work, as would a separate client definition with
    the scope tailored to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/20.0.2/rest-api/index.html).
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  action_group:
    version_added: 10.2.0

options:
  state:
    description:
      - State of the user federation.
      - On V(present), the user federation will be created if it does not yet exist, or updated with the parameters you provide.
      - On V(absent), the user federation will be removed if it exists.
    default: 'present'
    type: str
    choices:
      - present
      - absent

  realm:
    description:
      - The Keycloak realm under which this user federation resides.
    default: 'master'
    type: str

  id:
    description:
      - The unique ID for this user federation. If left empty, the user federation will be searched by its O(name).
    type: str

  name:
    description:
      - Display name of provider when linked in admin console.
    type: str

  provider_id:
    description:
      - Provider for this user federation. Built-in providers are V(ldap), V(kerberos), and V(sssd). Custom user storage providers
        can also be used.
    aliases:
      - providerId
    type: str

  provider_type:
    description:
      - Component type for user federation (only supported value is V(org.keycloak.storage.UserStorageProvider)).
    aliases:
      - providerType
    default: org.keycloak.storage.UserStorageProvider
    type: str

  parent_id:
    description:
      - Unique ID for the parent of this user federation. Realm ID will be automatically used if left blank.
    aliases:
      - parentId
    type: str

  remove_unspecified_mappers:
    description:
      - Remove mappers that are not specified in the configuration for this federation.
      - Set to V(false) to keep mappers that are not listed in O(mappers).
    type: bool
    default: true
    version_added: 9.4.0

  bind_credential_update_mode:
    description:
      - The value of the config parameter O(config.bindCredential) is redacted in the Keycloak responses. Comparing the redacted
        value with the desired value always evaluates to not equal. This means the before and desired states are never equal
        if the parameter is set.
      - Set to V(always) to include O(config.bindCredential) in the comparison of before and desired state. Because of the
        redacted value returned by Keycloak the module will always detect a change and make an update if a O(config.bindCredential)
        value is set.
      - Set to V(only_indirect) to exclude O(config.bindCredential) when comparing the before state with the desired state.
        The value of O(config.bindCredential) will only be updated if there are other changes to the user federation that
        require an update.
    type: str
    default: always
    choices:
      - always
      - only_indirect
    version_added: 9.5.0

  config:
    description:
      - Dict specifying the configuration options for the provider; the contents differ depending on the value of O(provider_id).
        Examples are given below for V(ldap), V(kerberos) and V(sssd). It is easiest to obtain valid config values by dumping
        an already-existing user federation configuration through check-mode in the RV(existing) field.
      - The value V(sssd) has been supported since community.general 4.2.0.
    type: dict
    suboptions:
      enabled:
        description:
          - Enable/disable this user federation.
        default: true
        type: bool

      priority:
        description:
          - Priority of provider when doing a user lookup. Lowest first.
        default: 0
        type: int

      importEnabled:
        description:
          - If V(true), LDAP users will be imported into Keycloak DB and synced by the configured sync policies.
        default: true
        type: bool

      editMode:
        description:
          - V(READ_ONLY) is a read-only LDAP store. V(WRITABLE) means data will be synced back to LDAP on demand. V(UNSYNCED)
            means user data will be imported, but not synced back to LDAP.
        type: str
        choices:
          - READ_ONLY
          - WRITABLE
          - UNSYNCED

      syncRegistrations:
        description:
          - Should newly created users be created within LDAP store? Priority effects which provider is chosen to sync the
            new user.
        default: false
        type: bool

      vendor:
        description:
          - LDAP vendor (provider).
          - Use short name. For instance, write V(rhds) for "Red Hat Directory Server".
        type: str

      usernameLDAPAttribute:
        description:
          - Name of LDAP attribute, which is mapped as Keycloak username. For many LDAP server vendors it can be V(uid). For
            Active directory it can be V(sAMAccountName) or V(cn). The attribute should be filled for all LDAP user records
            you want to import from LDAP to Keycloak.
        type: str

      rdnLDAPAttribute:
        description:
          - Name of LDAP attribute, which is used as RDN (top attribute) of typical user DN. Usually it is the same as Username
            LDAP attribute, however it is not required. For example for Active directory, it is common to use V(cn) as RDN
            attribute when username attribute might be V(sAMAccountName).
        type: str

      uuidLDAPAttribute:
        description:
          - Name of LDAP attribute, which is used as unique object identifier (UUID) for objects in LDAP. For many LDAP server
            vendors, it is V(entryUUID); however some are different. For example for Active directory it should be V(objectGUID).
            If your LDAP server does not support the notion of UUID, you can use any other attribute that is supposed to be
            unique among LDAP users in tree.
        type: str

      userObjectClasses:
        description:
          - All values of LDAP objectClass attribute for users in LDAP divided by comma. For example V(inetOrgPerson, organizationalPerson).
            Newly created Keycloak users will be written to LDAP with all those object classes and existing LDAP user records
            are found just if they contain all those object classes.
        type: str

      connectionUrl:
        description:
          - Connection URL to your LDAP server.
        type: str

      usersDn:
        description:
          - Full DN of LDAP tree where your users are. This DN is the parent of LDAP users.
        type: str

      customUserSearchFilter:
        description:
          - Additional LDAP Filter for filtering searched users. Leave this empty if you do not need additional filter.
        type: str

      searchScope:
        description:
          - For one level, the search applies only for users in the DNs specified by User DNs. For subtree, the search applies
            to the whole subtree. See LDAP documentation for more details.
        default: '1'
        type: str
        choices:
          - '1'
          - '2'

      authType:
        description:
          - Type of the Authentication method used during LDAP Bind operation. It is used in most of the requests sent to
            the LDAP server.
        default: 'none'
        type: str
        choices:
          - none
          - simple

      bindDn:
        description:
          - DN of LDAP user which will be used by Keycloak to access LDAP server.
        type: str

      bindCredential:
        description:
          - Password of LDAP admin.
        type: str

      startTls:
        description:
          - Encrypts the connection to LDAP using STARTTLS, which will disable connection pooling.
        default: false
        type: bool

      usePasswordModifyExtendedOp:
        description:
          - Use the LDAPv3 Password Modify Extended Operation (RFC-3062). The password modify extended operation usually requires
            that LDAP user already has password in the LDAP server. So when this is used with 'Sync Registrations', it can
            be good to add also 'Hardcoded LDAP attribute mapper' with randomly generated initial password.
        default: false
        type: bool

      validatePasswordPolicy:
        description:
          - Determines if Keycloak should validate the password with the realm password policy before updating it.
        default: false
        type: bool

      trustEmail:
        description:
          - If enabled, email provided by this provider is not verified even if verification is enabled for the realm.
        default: false
        type: bool

      useTruststoreSpi:
        description:
          - Specifies whether LDAP connection will use the truststore SPI with the truststore configured in standalone.xml/domain.xml.
            V(always) means that it will always use it. V(never) means that it will not use it. V(ldapsOnly) means that it
            will use if your connection URL use ldaps.
          - Note even if standalone.xml/domain.xml is not configured, the default Java cacerts or certificate specified by
            C(javax.net.ssl.trustStore) property will be used.
        default: ldapsOnly
        type: str
        choices:
          - always
          - ldapsOnly
          - never

      connectionTimeout:
        description:
          - LDAP Connection Timeout in milliseconds.
        type: int

      readTimeout:
        description:
          - LDAP Read Timeout in milliseconds. This timeout applies for LDAP read operations.
        type: int

      pagination:
        description:
          - Does the LDAP server support pagination.
        default: true
        type: bool

      connectionPooling:
        description:
          - Determines if Keycloak should use connection pooling for accessing LDAP server.
        default: true
        type: bool

      connectionPoolingAuthentication:
        description:
          - A list of space-separated authentication types of connections that may be pooled.
        type: str
        choices:
          - none
          - simple
          - DIGEST-MD5

      connectionPoolingDebug:
        description:
          - A string that indicates the level of debug output to produce. Example valid values are V(fine) (trace connection
            creation and removal) and V(all) (all debugging information).
        type: str

      connectionPoolingInitSize:
        description:
          - The number of connections per connection identity to create when initially creating a connection for the identity.
        type: int

      connectionPoolingMaxSize:
        description:
          - The maximum number of connections per connection identity that can be maintained concurrently.
        type: int

      connectionPoolingPrefSize:
        description:
          - The preferred number of connections per connection identity that should be maintained concurrently.
        type: int

      connectionPoolingProtocol:
        description:
          - A list of space-separated protocol types of connections that may be pooled. Valid types are V(plain) and V(ssl).
        type: str

      connectionPoolingTimeout:
        description:
          - The number of milliseconds that an idle connection may remain in the pool without being closed and removed from
            the pool.
        type: int

      allowKerberosAuthentication:
        description:
          - Enable/disable HTTP authentication of users with SPNEGO/Kerberos tokens. The data about authenticated users will
            be provisioned from this LDAP server.
        default: false
        type: bool

      kerberosRealm:
        description:
          - Name of kerberos realm.
        type: str

      krbPrincipalAttribute:
        description:
          - Name of the LDAP attribute, which refers to Kerberos principal. This is used to lookup appropriate LDAP user after
            successful Kerberos/SPNEGO authentication in Keycloak. When this is empty, the LDAP user will be looked based
            on LDAP username corresponding to the first part of his Kerberos principal. For instance, for principal C(john@KEYCLOAK.ORG),
            it will assume that LDAP username is V(john).
        type: str
        version_added: 8.1.0

      serverPrincipal:
        description:
          - Full name of server principal for HTTP service including server and domain name. For example V(HTTP/host.foo.org@FOO.ORG).
            Use V(*) to accept any service principal in the KeyTab file.
        type: str

      keyTab:
        description:
          - Location of Kerberos KeyTab file containing the credentials of server principal. For example V(/etc/krb5.keytab).
        type: str

      debug:
        description:
          - Enable/disable debug logging to standard output for Krb5LoginModule.
        type: bool

      useKerberosForPasswordAuthentication:
        description:
          - Use Kerberos login module for authenticate username/password against Kerberos server instead of authenticating
            against LDAP server with Directory Service API.
        default: false
        type: bool

      allowPasswordAuthentication:
        description:
          - Enable/disable possibility of username/password authentication against Kerberos database.
        type: bool

      batchSizeForSync:
        description:
          - Count of LDAP users to be imported from LDAP to Keycloak within a single transaction.
        default: 1000
        type: int

      fullSyncPeriod:
        description:
          - Period for full synchronization in seconds.
        default: -1
        type: int

      changedSyncPeriod:
        description:
          - Period for synchronization of changed or newly created LDAP users in seconds.
        default: -1
        type: int

      updateProfileFirstLogin:
        description:
          - Update profile on first login.
        type: bool

      cachePolicy:
        description:
          - Cache Policy for this storage provider.
        type: str
        default: 'DEFAULT'
        choices:
          - DEFAULT
          - EVICT_DAILY
          - EVICT_WEEKLY
          - MAX_LIFESPAN
          - NO_CACHE

      evictionDay:
        description:
          - Day of the week the entry will become invalid on.
        type: str

      evictionHour:
        description:
          - Hour of day the entry will become invalid on.
        type: str

      evictionMinute:
        description:
          - Minute of day the entry will become invalid on.
        type: str

      maxLifespan:
        description:
          - Max lifespan of cache entry in milliseconds.
        type: int

      referral:
        description:
          - Specifies if LDAP referrals should be followed or ignored. Please note that enabling referrals can slow down authentication
            as it allows the LDAP server to decide which other LDAP servers to use. This could potentially include untrusted
            servers.
        type: str
        choices:
          - ignore
          - follow
        version_added: 9.5.0

  mappers:
    description:
      - A list of dicts defining mappers associated with this Identity Provider.
    type: list
    elements: dict
    suboptions:
      id:
        description:
          - Unique ID of this mapper.
        type: str

      name:
        description:
          - Name of the mapper. If no ID is given, the mapper will be searched by name.
        type: str

      parentId:
        description:
          - Unique ID for the parent of this mapper. ID of the user federation will automatically be used if left blank.
        type: str

      providerId:
        description:
          - The mapper type for this mapper (for instance V(user-attribute-ldap-mapper)).
        type: str

      providerType:
        description:
          - Component type for this mapper.
        type: str
        default: org.keycloak.storage.ldap.mappers.LDAPStorageMapper

      config:
        description:
          - Dict specifying the configuration options for the mapper; the contents differ depending on the value of I(identityProviderMapper).
        type: dict

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Laurent Paumier (@laurpaum)
"""

EXAMPLES = r"""
- name: Create LDAP user federation
  community.general.keycloak_user_federation:
    auth_keycloak_url: https://keycloak.example.com/auth
    auth_realm: master
    auth_username: admin
    auth_password: password
    realm: my-realm
    name: my-ldap
    state: present
    provider_id: ldap
    provider_type: org.keycloak.storage.UserStorageProvider
    config:
      priority: 0
      enabled: true
      cachePolicy: DEFAULT
      batchSizeForSync: 1000
      editMode: READ_ONLY
      importEnabled: true
      syncRegistrations: false
      vendor: other
      usernameLDAPAttribute: uid
      rdnLDAPAttribute: uid
      uuidLDAPAttribute: entryUUID
      userObjectClasses: inetOrgPerson, organizationalPerson
      connectionUrl: ldaps://ldap.example.com:636
      usersDn: ou=Users,dc=example,dc=com
      authType: simple
      bindDn: cn=directory reader
      bindCredential: password
      searchScope: 1
      validatePasswordPolicy: false
      trustEmail: false
      useTruststoreSpi: ldapsOnly
      connectionPooling: true
      pagination: true
      allowKerberosAuthentication: false
      debug: false
      useKerberosForPasswordAuthentication: false
    mappers:
      - name: "full name"
        providerId: "full-name-ldap-mapper"
        providerType: "org.keycloak.storage.ldap.mappers.LDAPStorageMapper"
        config:
          ldap.full.name.attribute: cn
          read.only: true
          write.only: false

- name: Create Kerberos user federation
  community.general.keycloak_user_federation:
    auth_keycloak_url: https://keycloak.example.com/auth
    auth_realm: master
    auth_username: admin
    auth_password: password
    realm: my-realm
    name: my-kerberos
    state: present
    provider_id: kerberos
    provider_type: org.keycloak.storage.UserStorageProvider
    config:
      priority: 0
      enabled: true
      cachePolicy: DEFAULT
      kerberosRealm: EXAMPLE.COM
      serverPrincipal: HTTP/host.example.com@EXAMPLE.COM
      keyTab: keytab
      allowPasswordAuthentication: false
      updateProfileFirstLogin: false

- name: Create sssd user federation
  community.general.keycloak_user_federation:
    auth_keycloak_url: https://keycloak.example.com/auth
    auth_realm: master
    auth_username: admin
    auth_password: password
    realm: my-realm
    name: my-sssd
    state: present
    provider_id: sssd
    provider_type: org.keycloak.storage.UserStorageProvider
    config:
      priority: 0
      enabled: true
      cachePolicy: DEFAULT

- name: Delete user federation
  community.general.keycloak_user_federation:
    auth_keycloak_url: https://keycloak.example.com/auth
    auth_realm: master
    auth_username: admin
    auth_password: password
    realm: my-realm
    name: my-federation
    state: absent
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str
  sample: "No changes required to user federation 164bb483-c613-482e-80fe-7f1431308799."

proposed:
  description: Representation of proposed user federation.
  returned: always
  type: dict
  sample:
    {
      "config": {
        "allowKerberosAuthentication": "false",
        "authType": "simple",
        "batchSizeForSync": "1000",
        "bindCredential": "**********",
        "bindDn": "cn=directory reader",
        "cachePolicy": "DEFAULT",
        "connectionPooling": "true",
        "connectionUrl": "ldaps://ldap.example.com:636",
        "debug": "false",
        "editMode": "READ_ONLY",
        "enabled": "true",
        "importEnabled": "true",
        "pagination": "true",
        "priority": "0",
        "rdnLDAPAttribute": "uid",
        "searchScope": "1",
        "syncRegistrations": "false",
        "trustEmail": "false",
        "useKerberosForPasswordAuthentication": "false",
        "useTruststoreSpi": "ldapsOnly",
        "userObjectClasses": "inetOrgPerson, organizationalPerson",
        "usernameLDAPAttribute": "uid",
        "usersDn": "ou=Users,dc=example,dc=com",
        "uuidLDAPAttribute": "entryUUID",
        "validatePasswordPolicy": "false",
        "vendor": "other"
      },
      "name": "ldap",
      "providerId": "ldap",
      "providerType": "org.keycloak.storage.UserStorageProvider"
    }

existing:
  description: Representation of existing user federation.
  returned: always
  type: dict
  sample:
    {
      "config": {
        "allowKerberosAuthentication": "false",
        "authType": "simple",
        "batchSizeForSync": "1000",
        "bindCredential": "**********",
        "bindDn": "cn=directory reader",
        "cachePolicy": "DEFAULT",
        "changedSyncPeriod": "-1",
        "connectionPooling": "true",
        "connectionUrl": "ldaps://ldap.example.com:636",
        "debug": "false",
        "editMode": "READ_ONLY",
        "enabled": "true",
        "fullSyncPeriod": "-1",
        "importEnabled": "true",
        "pagination": "true",
        "priority": "0",
        "rdnLDAPAttribute": "uid",
        "searchScope": "1",
        "syncRegistrations": "false",
        "trustEmail": "false",
        "useKerberosForPasswordAuthentication": "false",
        "useTruststoreSpi": "ldapsOnly",
        "userObjectClasses": "inetOrgPerson, organizationalPerson",
        "usernameLDAPAttribute": "uid",
        "usersDn": "ou=Users,dc=example,dc=com",
        "uuidLDAPAttribute": "entryUUID",
        "validatePasswordPolicy": "false",
        "vendor": "other"
      },
      "id": "01122837-9047-4ae4-8ca0-6e2e891a765f",
      "mappers": [
        {
          "config": {
            "always.read.value.from.ldap": "false",
            "is.mandatory.in.ldap": "false",
            "ldap.attribute": "mail",
            "read.only": "true",
            "user.model.attribute": "email"
          },
          "id": "17d60ce2-2d44-4c2c-8b1f-1fba601b9a9f",
          "name": "email",
          "parentId": "01122837-9047-4ae4-8ca0-6e2e891a765f",
          "providerId": "user-attribute-ldap-mapper",
          "providerType": "org.keycloak.storage.ldap.mappers.LDAPStorageMapper"
        }
      ],
      "name": "myfed",
      "parentId": "myrealm",
      "providerId": "ldap",
      "providerType": "org.keycloak.storage.UserStorageProvider"
    }

end_state:
  description: Representation of user federation after module execution.
  returned: on success
  type: dict
  sample:
    {
      "config": {
        "allowPasswordAuthentication": "false",
        "cachePolicy": "DEFAULT",
        "enabled": "true",
        "kerberosRealm": "EXAMPLE.COM",
        "keyTab": "/etc/krb5.keytab",
        "priority": "0",
        "serverPrincipal": "HTTP/host.example.com@EXAMPLE.COM",
        "updateProfileFirstLogin": "false"
      },
      "id": "cf52ae4f-4471-4435-a0cf-bb620cadc122",
      "mappers": [],
      "name": "kerberos",
      "parentId": "myrealm",
      "providerId": "kerberos",
      "providerType": "org.keycloak.storage.UserStorageProvider"
    }
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from copy import deepcopy


def normalize_kc_comp(comp):
    if 'config' in comp:
        # kc completely removes the parameter `krbPrincipalAttribute` if it is set to `''`; the unset kc parameter is equivalent to `''`;
        # to make change detection and diff more accurate we set it again in the kc responses
        if 'krbPrincipalAttribute' not in comp['config']:
            comp['config']['krbPrincipalAttribute'] = ['']

        # kc stores a timestamp of the last sync in `lastSync` to time the periodic sync, it is removed to minimize diff/changes
        comp['config'].pop('lastSync', None)


def sanitize(comp):
    compcopy = deepcopy(comp)
    if 'config' in compcopy:
        compcopy['config'] = {k: v[0] for k, v in compcopy['config'].items()}
        if 'bindCredential' in compcopy['config']:
            compcopy['config']['bindCredential'] = '**********'
    if 'mappers' in compcopy:
        for mapper in compcopy['mappers']:
            if 'config' in mapper:
                mapper['config'] = {k: v[0] for k, v in mapper['config'].items()}
    return compcopy


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    config_spec = dict(
        allowKerberosAuthentication=dict(type='bool', default=False),
        allowPasswordAuthentication=dict(type='bool'),
        authType=dict(type='str', choices=['none', 'simple'], default='none'),
        batchSizeForSync=dict(type='int', default=1000),
        bindCredential=dict(type='str', no_log=True),
        bindDn=dict(type='str'),
        cachePolicy=dict(type='str', choices=['DEFAULT', 'EVICT_DAILY', 'EVICT_WEEKLY', 'MAX_LIFESPAN', 'NO_CACHE'], default='DEFAULT'),
        changedSyncPeriod=dict(type='int', default=-1),
        connectionPooling=dict(type='bool', default=True),
        connectionPoolingAuthentication=dict(type='str', choices=['none', 'simple', 'DIGEST-MD5']),
        connectionPoolingDebug=dict(type='str'),
        connectionPoolingInitSize=dict(type='int'),
        connectionPoolingMaxSize=dict(type='int'),
        connectionPoolingPrefSize=dict(type='int'),
        connectionPoolingProtocol=dict(type='str'),
        connectionPoolingTimeout=dict(type='int'),
        connectionTimeout=dict(type='int'),
        connectionUrl=dict(type='str'),
        customUserSearchFilter=dict(type='str'),
        debug=dict(type='bool'),
        editMode=dict(type='str', choices=['READ_ONLY', 'WRITABLE', 'UNSYNCED']),
        enabled=dict(type='bool', default=True),
        evictionDay=dict(type='str'),
        evictionHour=dict(type='str'),
        evictionMinute=dict(type='str'),
        fullSyncPeriod=dict(type='int', default=-1),
        importEnabled=dict(type='bool', default=True),
        kerberosRealm=dict(type='str'),
        keyTab=dict(type='str', no_log=False),
        maxLifespan=dict(type='int'),
        pagination=dict(type='bool', default=True),
        priority=dict(type='int', default=0),
        rdnLDAPAttribute=dict(type='str'),
        readTimeout=dict(type='int'),
        referral=dict(type='str', choices=['ignore', 'follow']),
        searchScope=dict(type='str', choices=['1', '2'], default='1'),
        serverPrincipal=dict(type='str'),
        krbPrincipalAttribute=dict(type='str'),
        startTls=dict(type='bool', default=False),
        syncRegistrations=dict(type='bool', default=False),
        trustEmail=dict(type='bool', default=False),
        updateProfileFirstLogin=dict(type='bool'),
        useKerberosForPasswordAuthentication=dict(type='bool', default=False),
        usePasswordModifyExtendedOp=dict(type='bool', default=False, no_log=False),
        useTruststoreSpi=dict(type='str', choices=['always', 'ldapsOnly', 'never'], default='ldapsOnly'),
        userObjectClasses=dict(type='str'),
        usernameLDAPAttribute=dict(type='str'),
        usersDn=dict(type='str'),
        uuidLDAPAttribute=dict(type='str'),
        validatePasswordPolicy=dict(type='bool', default=False),
        vendor=dict(type='str'),
    )

    mapper_spec = dict(
        id=dict(type='str'),
        name=dict(type='str'),
        parentId=dict(type='str'),
        providerId=dict(type='str'),
        providerType=dict(type='str', default='org.keycloak.storage.ldap.mappers.LDAPStorageMapper'),
        config=dict(type='dict'),
    )

    meta_args = dict(
        config=dict(type='dict', options=config_spec),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        realm=dict(type='str', default='master'),
        id=dict(type='str'),
        name=dict(type='str'),
        provider_id=dict(type='str', aliases=['providerId']),
        provider_type=dict(type='str', aliases=['providerType'], default='org.keycloak.storage.UserStorageProvider'),
        parent_id=dict(type='str', aliases=['parentId']),
        remove_unspecified_mappers=dict(type='bool', default=True),
        bind_credential_update_mode=dict(type='str', default='always', choices=['always', 'only_indirect']),
        mappers=dict(type='list', elements='dict', options=mapper_spec),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['id', 'name'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password', 'auth_client_id', 'auth_client_secret']]),
                           required_together=([['auth_username', 'auth_password']]),
                           required_by={'refresh_token': 'auth_realm'},
                           )

    result = dict(changed=False, msg='', diff={}, proposed={}, existing={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    config = module.params.get('config')
    mappers = module.params.get('mappers')
    cid = module.params.get('id')
    name = module.params.get('name')

    # Keycloak API expects config parameters to be arrays containing a single string element
    if config is not None:
        module.params['config'] = {
            k: [str(v).lower() if not isinstance(v, str) else v]
            for k, v in config.items()
            if config[k] is not None
        }

    if mappers is not None:
        for mapper in mappers:
            if mapper.get('config') is not None:
                mapper['config'] = {
                    k: [str(v).lower() if not isinstance(v, str) else v]
                    for k, v in mapper['config'].items()
                    if mapper['config'][k] is not None
                }

    # Filter and map the parameters names that apply
    comp_params = [x for x in module.params
                   if x not in list(keycloak_argument_spec().keys())
                   + ['state', 'realm', 'mappers', 'remove_unspecified_mappers', 'bind_credential_update_mode']
                   and module.params.get(x) is not None]

    # See if it already exists in Keycloak
    if cid is None:
        found = kc.get_components(urlencode(dict(type='org.keycloak.storage.UserStorageProvider', name=name)), realm)
        if len(found) > 1:
            module.fail_json(msg='No ID given and found multiple user federations with name `{name}`. Cannot continue.'.format(name=name))
        before_comp = next(iter(found), None)
        if before_comp is not None:
            cid = before_comp['id']
    else:
        before_comp = kc.get_component(cid, realm)

    if before_comp is None:
        before_comp = {}

    # if user federation exists, get associated mappers
    if cid is not None and before_comp:
        before_comp['mappers'] = sorted(kc.get_components(urlencode(dict(parent=cid)), realm), key=lambda x: x.get('name') or '')

    normalize_kc_comp(before_comp)

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    for param in comp_params:
        new_param_value = module.params.get(param)
        old_value = before_comp[camel(param)] if camel(param) in before_comp else None
        if param == 'mappers':
            new_param_value = [{k: v for k, v in x.items() if v is not None} for x in new_param_value]
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # special handling of mappers list to allow change detection
    if module.params.get('mappers') is not None:
        if module.params['provider_id'] in ['kerberos', 'sssd']:
            module.fail_json(msg='Cannot configure mappers for {type} provider.'.format(type=module.params['provider_id']))
        for change in module.params['mappers']:
            change = {k: v for k, v in change.items() if v is not None}
            if change.get('id') is None and change.get('name') is None:
                module.fail_json(msg='Either `name` or `id` has to be specified on each mapper.')
            if cid is None:
                old_mapper = {}
            elif change.get('id') is not None:
                old_mapper = next((before_mapper for before_mapper in before_comp.get('mappers', []) if before_mapper["id"] == change['id']), None)
                if old_mapper is None:
                    old_mapper = {}
            else:
                found = [before_mapper for before_mapper in before_comp.get('mappers', []) if before_mapper['name'] == change['name']]
                if len(found) > 1:
                    module.fail_json(msg='Found multiple mappers with name `{name}`. Cannot continue.'.format(name=change['name']))
                if len(found) == 1:
                    old_mapper = found[0]
                else:
                    old_mapper = {}
            new_mapper = old_mapper.copy()
            new_mapper.update(change)
            # changeset contains all desired mappers: those existing, to update or to create
            if changeset.get('mappers') is None:
                changeset['mappers'] = list()
            changeset['mappers'].append(new_mapper)
        changeset['mappers'] = sorted(changeset['mappers'], key=lambda x: x.get('name') or '')

        # to keep unspecified existing mappers we add them to the desired mappers list, unless they're already present
        if not module.params['remove_unspecified_mappers'] and 'mappers' in before_comp:
            changeset_mapper_ids = [mapper['id'] for mapper in changeset['mappers'] if 'id' in mapper]
            changeset['mappers'].extend([mapper for mapper in before_comp['mappers'] if mapper['id'] not in changeset_mapper_ids])

    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_comp = before_comp.copy()
    desired_comp.update(changeset)

    result['proposed'] = sanitize(changeset)
    result['existing'] = sanitize(before_comp)

    # Cater for when it doesn't exist (an empty dict)
    if not before_comp:
        if state == 'absent':
            # Do nothing and exit
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = {}
            result['msg'] = 'User federation does not exist; doing nothing.'
            module.exit_json(**result)

        # Process a creation
        result['changed'] = True

        if module.check_mode:
            if module._diff:
                result['diff'] = dict(before='', after=sanitize(desired_comp))
            module.exit_json(**result)

        # create it
        desired_mappers = desired_comp.pop('mappers', [])
        after_comp = kc.create_component(desired_comp, realm)
        cid = after_comp['id']
        updated_mappers = []
        # when creating a user federation, keycloak automatically creates default mappers
        default_mappers = kc.get_components(urlencode(dict(parent=cid)), realm)

        # create new mappers or update existing default mappers
        for desired_mapper in desired_mappers:
            found = [default_mapper for default_mapper in default_mappers if default_mapper['name'] == desired_mapper['name']]
            if len(found) > 1:
                module.fail_json(msg='Found multiple mappers with name `{name}`. Cannot continue.'.format(name=desired_mapper['name']))
            if len(found) == 1:
                old_mapper = found[0]
            else:
                old_mapper = {}

            new_mapper = old_mapper.copy()
            new_mapper.update(desired_mapper)

            if new_mapper.get('id') is not None:
                kc.update_component(new_mapper, realm)
                updated_mappers.append(new_mapper)
            else:
                if new_mapper.get('parentId') is None:
                    new_mapper['parentId'] = cid
                updated_mappers.append(kc.create_component(new_mapper, realm))

        if module.params['remove_unspecified_mappers']:
            # we remove all unwanted default mappers
            # we use ids so we dont accidently remove one of the previously updated default mapper
            for default_mapper in default_mappers:
                if not default_mapper['id'] in [x['id'] for x in updated_mappers]:
                    kc.delete_component(default_mapper['id'], realm)

        after_comp['mappers'] = kc.get_components(urlencode(dict(parent=cid)), realm)
        normalize_kc_comp(after_comp)
        if module._diff:
            result['diff'] = dict(before='', after=sanitize(after_comp))
        result['end_state'] = sanitize(after_comp)
        result['msg'] = "User federation {id} has been created".format(id=cid)
        module.exit_json(**result)

    else:
        if state == 'present':
            # Process an update

            desired_copy = deepcopy(desired_comp)
            before_copy = deepcopy(before_comp)
            # exclude bindCredential when checking wether an update is required, therefore
            # updating it only if there are other changes
            if module.params['bind_credential_update_mode'] == 'only_indirect':
                desired_copy.get('config', []).pop('bindCredential', None)
                before_copy.get('config', []).pop('bindCredential', None)
            # no changes
            if desired_copy == before_copy:
                result['changed'] = False
                result['end_state'] = sanitize(desired_comp)
                result['msg'] = "No changes required to user federation {id}.".format(id=cid)
                module.exit_json(**result)

            # doing an update
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=sanitize(before_comp), after=sanitize(desired_comp))

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            desired_mappers = desired_comp.pop('mappers', [])
            kc.update_component(desired_comp, realm)

            for before_mapper in before_comp.get('mappers', []):
                # remove unwanted existing mappers that will not be updated
                if not before_mapper['id'] in [x['id'] for x in desired_mappers if 'id' in x]:
                    kc.delete_component(before_mapper['id'], realm)

            for mapper in desired_mappers:
                if mapper in before_comp.get('mappers', []):
                    continue
                if mapper.get('id') is not None:
                    kc.update_component(mapper, realm)
                else:
                    if mapper.get('parentId') is None:
                        mapper['parentId'] = desired_comp['id']
                    kc.create_component(mapper, realm)

            after_comp = kc.get_component(cid, realm)
            after_comp['mappers'] = sorted(kc.get_components(urlencode(dict(parent=cid)), realm), key=lambda x: x.get('name') or '')
            normalize_kc_comp(after_comp)
            after_comp_sanitized = sanitize(after_comp)
            before_comp_sanitized = sanitize(before_comp)
            result['end_state'] = after_comp_sanitized
            if module._diff:
                result['diff'] = dict(before=before_comp_sanitized, after=after_comp_sanitized)
            result['changed'] = before_comp_sanitized != after_comp_sanitized
            result['msg'] = "User federation {id} has been updated".format(id=cid)
            module.exit_json(**result)

        elif state == 'absent':
            # Process a deletion
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=sanitize(before_comp), after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete it
            kc.delete_component(cid, realm)

            result['end_state'] = {}

            result['msg'] = "User federation {id} has been deleted".format(id=cid)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
