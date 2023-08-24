import enum


class SkillLevel(str, enum.Enum):
    EMPTY = "EMPTY"
    INTERN = "INTERN"
    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    EXPERT = "EXPERT"


class SkillDesirability(str, enum.Enum):
    REQUIRED = "REQUIRED"
    DESIRED = "DESIRED"
    EMPTY = "EMPTY"
