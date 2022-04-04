import enum
from app import Genre
class GenreEnum(enum.Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Country = 'Country'
    Classical = 'Classical'
    Electroni = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Hip-Hop = 'Hip-Hop'
    Heavy Metal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical Theatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    R&B = 'R&B'
    Reggae = 'Reggae'
    Rock n Roll = 'Rock n Roll'
    Soul = 'Soul'),
    Other = 'Other'
    # add all fields
    ...
    @classmethod
    def choices(cls):
        """ Methods decorated with @classmethod can be called statically without having an instance of the class."""
        return [(choice.name, choice.value) for choice in cls]
class State(enum.Enum):
    AL = 'AL'
    AK = 'AK'
    # add all fields
    ...
    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cl