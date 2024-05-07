from enum import Enum


class SystemEnvironment(Enum):
    LOCAL = 0
    TEST = 1
    STAGING = 2
    UAT = 3
    PRODUCTION = 4


    staticmethod
    def names():
        return [x.name for x in SystemEnvironment]
