from __future__ import annotations
from ..models import Player, FallenFace, ActiveFace, Status, active_face_vals, fallen_face_vals 
from ..utils import InvalidPlayerActionValidator, GameStateValidator


# class ActiveFace(Enum):
#     BACKFIRE = "Backfire"
#     POWER_MOVE = "Power Move"
#     RECOVER = "Recover"
#     JAB = "Jab"
#     STRIKE = "Strike"
#     PICKPOCKET = "Pickpocket"


class Action_service:
    ...
    def __init__(self):
        ...

    def __validate_action(self, player: Player, action: FallenFace | ActiveFace) -> bool:
        """
        Docstring for __validate_action
        THIS METHOD IS NOT NEEDED AS PLAYER'S ACTOIN VALIDATIONS ARE DONE IN THE PLAYER MODEL METHODS  
        :param self: Description
        :param player: Description
        :type player: Player
        :param action: Description
        :type action: FallenFace | ActiveFace
        :return: Description
        :rtype: bool
        """
        ...

        
    
        def execute_action(self, player: Player, action: FallenFace | ActiveFace, target: Player | None = None, **kwargs) -> bool:
            
            """Apply a rolled face effect for `player`.

            Quick summary of expectations:
            - `player`: the actor performing the face.
            - `action`: an `ActiveFace` (alive) or `FallenFace` (fallen).
            - `target`: required when the face or chosen option affects another player.
            - `choice_action` (in `kwargs`): when a face offers choices — see below.

            choice_action values by face:
            - Active faces:
                - `BACKFIRE`: no `target`; actor takes 3 HP.
                - `RECOVER`: no `target`; actor heals 3 HP.
                - `POWER_MOVE`: `'damage_hp'` (requires `target`) or `'gain_vp'` (actor gains 3 VP).
                - `JAB`: requires `target`; deals 2 HP.
                - `STRIKE`: requires `target`; deals 4 HP.
                - `PICKPOCKET`: requires `target`; steals 1 VP.
            - Fallen faces:
                - `PLUS2HP_OR_PLUS1VP*`: `'heal_hp'` (target heals 2) or `'gain_vp'` (target gains 1).
                - `REMOVE2HP_OR_MINUS1VP*`: `'damage_hp'` (target takes 2) or `'steal_vp'` (fallen steals 1 VP).

            Returns `True` on success. Raises `InvalidPlayerActionValidator` or
            `GameStateValidator` for invalid inputs or missing arguments.
            """
            
            choice = kwargs.get("choice_action")

            if isinstance(action, ActiveFace):
                #  faces that do not require a target
                if target is None:
                    if action == ActiveFace.BACKFIRE:
                        player.take_damage(3)
                        return True
                    if action == ActiveFace.RECOVER:
                        player.heal(3)
                        return True
                    if action == ActiveFace.POWER_MOVE:
                        # POWER_MOVE without a target => assume VP gain unless specified otherwise
                        if choice is None or choice == "gain_vp":
                            player.gain_vp(3)
                            return True
                        # Explicit damage choice requires a target
                        if choice == "damage_hp":
                            raise InvalidPlayerActionValidator("POWER_MOVE with 'damage_hp' requires a target")
                        raise InvalidPlayerActionValidator("Invalid choice_action provided for POWER_MOVE")

                # Targeted active faces
                if target is None:
                    raise InvalidPlayerActionValidator("This action requires a target")

                if action == ActiveFace.POWER_MOVE:
                    if choice == "damage_hp":
                        target.take_damage(6)
                        # recording players targets
                        player.last_targetedto = target.name
                        target.last_targetedby = player.name
                        return True
                    if choice == "gain_vp":
                        player.gain_vp(3)
                        return True
                    raise InvalidPlayerActionValidator("Invalid choice_action provided for POWER_MOVE")
                if action == ActiveFace.JAB:
                    target.take_damage(2)
                    player.last_targetedto = target.name
                    target.last_targetedby = player.name
                    return True
                if action == ActiveFace.STRIKE:
                    target.take_damage(4)
                    player.last_targetedto = target.name
                    target.last_targetedby = player.name
                    return True
                if action == ActiveFace.PICKPOCKET:
                    player.steal_vp(target, 1)
                    player.last_targetedto = target.name
                    target.last_targetedby = player.name
                    return True

            if isinstance(action, FallenFace):
                # eat 5 star do nothing lol
                if target is None:
                    return True

                # Fallen players can only target alive players and cannot target the same player twice

                if player.last_targetedto is not None and player.last_targetedto == target.name:
                    raise InvalidPlayerActionValidator("Fallen player cannot affect the same target two rounds in a row")
                if target.status != Status.ALIVE:
                    raise InvalidPlayerActionValidator("Fallen players can only affect alive players")

                if action in (FallenFace.PLUS2HP_OR_PLUS1VP, FallenFace.PLUS2HP_OR_PLUS1VP_2):
                    if choice == "heal_hp":
                        target.heal(2)
                    elif choice == "gain_vp":
                        target.gain_vp(1)
                    else:
                        raise InvalidPlayerActionValidator("Invalid choice_action provided for PLUS2HP_OR_PLUS1VP")
                    player.last_targetedto = target.name
                    target.last_targetedby = player.name
                    return True

                if action in (FallenFace.REMOVE2HP_OR_MINUS1VP, FallenFace.REMOVE2HP_OR_MINUS1VP_2):
                    if choice == "damage_hp":
                        target.take_damage(2)
                    elif choice == "steal_vp":
                        target.reduce_vp(1)
                    else:
                        raise InvalidPlayerActionValidator("Invalid choice_action provided for REMOVE2HP_OR_MINUS1VP")
                    player.last_targetedto = target.name
                    target.last_targetedby = player.name
                    return True

            # If we fall through, action was not handled
            raise InvalidPlayerActionValidator("Unhandled action or invalid parameters")