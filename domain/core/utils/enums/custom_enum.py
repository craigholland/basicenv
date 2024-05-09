from enum import EnumMeta, Enum


class CustomEnum(EnumMeta):
    def names(cls):
        return [member.name for member in cls.__members__.values()
                if isinstance(member, Enum)]

