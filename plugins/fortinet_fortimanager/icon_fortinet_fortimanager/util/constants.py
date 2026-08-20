# JSON-RPC URL Patterns
URL_LOGIN = "/sys/login/user"
URL_LOGOUT = "/sys/logout"
URL_SYSTEM_STATUS = "/sys/status"
URL_ADDRESS_OBJECTS = "/pm/config/adom/{adom}/obj/firewall/address"
URL_ADDRESS_GROUPS = "/pm/config/adom/{adom}/obj/firewall/addrgrp"
URL_ADDRESS_GROUP = "/pm/config/adom/{adom}/obj/firewall/addrgrp/{name}"
URL_POLICIES = "/pm/config/adom/{adom}/pkg/{package}/firewall/policy"
URL_INSTALL_PACKAGE = "/securityconsole/install/package"

# JSON-RPC Methods
METHOD_GET = "get"
METHOD_ADD = "add"
METHOD_SET = "set"
METHOD_UPDATE = "update"
METHOD_DELETE = "delete"
METHOD_EXEC = "exec"

# Address Object Type Encoding
# FortiManager's JSON-RPC returns the address `type` field as an integer rather than
# the string name accepted on write (confirmed in the field: an ipmask object returns 0).
# Only the three types this plugin creates and documents are mapped by ID. Any other
# integer is rendered as its numeric string rather than guessed at, so an unmapped
# type can never fail output schema validation or be silently mislabelled.
ADDRESS_TYPE_BY_ID = {
    0: "ipmask",
    1: "iprange",
    2: "fqdn",
}

# FortiManager API field name -> plugin schema field name. The API uses hyphenated
# names while the schema uses underscores, so these fields never populated before.
ADDRESS_FIELD_ALIASES = {
    "start_ip": ("start-ip", "start_ip"),
    "end_ip": ("end-ip", "end_ip"),
    "associated_interface": ("associated-interface", "associated_interface"),
}

# Error Code Constants
ERROR_CODE_SUCCESS = 0
ERROR_CODE_NO_PERMISSION = -1
ERROR_CODE_INVALID_PARAMS = -2
ERROR_CODE_OBJECT_NOT_EXIST = -3
ERROR_CODE_OBJECT_ALREADY_EXISTS = -6
ERROR_CODE_SESSION_EXPIRED = -10
# Returned when an object is still referenced by a group or policy. FortiManager's
# message for this code is just 'used', so the code is what must be matched.
ERROR_CODE_OBJECT_IN_USE = -10015

# Human-readable error code meanings (fallback when API message is empty)
ERROR_MESSAGES = {
    ERROR_CODE_SUCCESS: "Success",
    ERROR_CODE_NO_PERMISSION: "No permission",
    ERROR_CODE_INVALID_PARAMS: "Invalid parameters",
    ERROR_CODE_OBJECT_NOT_EXIST: "Object does not exist",
    ERROR_CODE_OBJECT_ALREADY_EXISTS: "Object already exists or invalid URL",
    ERROR_CODE_SESSION_EXPIRED: "Session expired",
}
