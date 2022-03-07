class HA9Exception(Exception):
    pass

class SelfTestError(HA9Exception):
    pass

class ServiceRequest(HA9Exception):
    pass

class SyntaxError(HA9Exception):
    pass

class MessageAvailableException(HA9Exception):
    pass

class ParameterError(HA9Exception):
    pass
