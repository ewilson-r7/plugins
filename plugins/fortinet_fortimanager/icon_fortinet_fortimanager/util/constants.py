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

# Error Code Constants
ERROR_CODE_SUCCESS = 0
ERROR_CODE_NO_PERMISSION = -1
ERROR_CODE_INVALID_PARAMS = -2
ERROR_CODE_OBJECT_NOT_EXIST = -3
ERROR_CODE_OBJECT_ALREADY_EXISTS = -6
ERROR_CODE_SESSION_EXPIRED = -10

# Human-readable error code meanings
ERROR_MESSAGES = {
    ERROR_CODE_SUCCESS: "Success",
    ERROR_CODE_NO_PERMISSION: "No permission",
    ERROR_CODE_INVALID_PARAMS: "Invalid parameters",
    ERROR_CODE_OBJECT_NOT_EXIST: "Object does not exist",
    ERROR_CODE_OBJECT_ALREADY_EXISTS: "Object already exists (naming conflict)",
    ERROR_CODE_SESSION_EXPIRED: "Session expired",
}
