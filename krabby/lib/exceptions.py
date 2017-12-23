class CustomException(Exception):
    def __init__(self, msg):
        self.err = msg

    def __str__(self):
        return self.err

# =================================================


class JiraShipmentTicketNotFound(CustomException):
    pass

# =================================================


class JiraIVTTicketNotFound(CustomException):
    pass

# =================================================


class MachineAlreadyExists(CustomException):
    pass

# =================================================


class TaskStoppedException(CustomException):
    pass

# =================================================
