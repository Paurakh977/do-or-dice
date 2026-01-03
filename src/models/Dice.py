from enum import Enum

class ActiveFace(Enum):
    BACKFIRE = "Backfire"
    POWER_MOVE = "Power Move"
    RECOVER = "Recover"
    JAB = "Jab"
    STRIKE = "Strike"
    PICKPOCKET = "Pickpocket"


class Status(Enum):
    FALLEN = "fallen"
    ALIVE = "alive"


class FallenFace(Enum):
    NOTHING_1 = "Nothing"
    PLUS2HP_OR_PLUS1VP = "+2 HP OR +1 VP to any alive player"
    REMOVE2HP_OR_MINUS1VP = "Remove −2 HP OR −1 VP from any alive player"
    PLUS2HP_OR_PLUS1VP_2 = "+2 HP OR +1 VP to any alive player"
    REMOVE2HP_OR_MINUS1VP_2 = "Remove −2 HP OR −1 VP from any alive player"
    NOTHING_2 = "Nothing"


active_face_vals = {
        1: ActiveFace.BACKFIRE,
        2: ActiveFace.POWER_MOVE,
        3: ActiveFace.RECOVER,
        4: ActiveFace.JAB,
        5: ActiveFace.STRIKE,
        6: ActiveFace.PICKPOCKET,
    }

fallen_face_vals = {
        1: FallenFace.NOTHING_1,
        2: FallenFace.PLUS2HP_OR_PLUS1VP,
        3: FallenFace.REMOVE2HP_OR_MINUS1VP,
        4: FallenFace.PLUS2HP_OR_PLUS1VP_2,
        5: FallenFace.REMOVE2HP_OR_MINUS1VP_2,
        6: FallenFace.NOTHING_2,
    }