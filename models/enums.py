from enum import Enum


class RoleType(Enum):
    approver = "approver"
    complainer = "complainer"
    admin = "admin"
    