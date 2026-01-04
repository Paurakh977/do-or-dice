from __future__ import annotations
from ..controllers.api import Action_service
from ..models import Player, ActiveFace, FallenFace, active_face_vals, fallen_face_vals
from ..utils import GameStateValidator
from ..configs.constants import MAX_ROUNDS as CONFIG_MAX_ROUNDS


class TurnResolverService():
    """
    Docstring for services.turnresolver:
    This service is responsible for resolving player turns in the game, taking and updating actions of each event of the game cycle.
    """
    MAX_ROUNDS :int = CONFIG_MAX_ROUNDS
    CURRENT_ROUND :int = 0
    participants : list[Player] =[]

    def __init__(self, action_service: Action_service) -> None:
        self.ingame_action_service : Action_service = action_service

    @classmethod 
    def set_participants(cls, players: list[Player]) -> None:
        """
        Class method to set the participants for the turn resolver.

        :param players: List of Player instances participating in the game.
        :type players: list[Player]
        :return: None
        :rtype: None
        """
        cls.participants = players

    def target_lookup(self,player: Player , action: ActiveFace | FallenFace ) -> bool:
        """
        Method to guide of the acrtion needs a target to be chosen or not
        :return: True if needed target else False
        :rtype: bool
        """
        if isinstance(action, ActiveFace) and (action == active_face_vals[2] or action == active_face_vals[4] or action == active_face_vals[5] or action == active_face_vals[6] ):
            return True
        elif isinstance(action, FallenFace) and not (action == fallen_face_vals[1] or  action == fallen_face_vals[6] ):
            return True
        else:
            return False
    
    
    def resolve_turns(self) -> None:
        """
        Method to resolve turns for each participant using the ingame action service.

        :return: None
        """
        for player  in self.participants:
            face_value = player.roll_dice()

            # Special handling for POWER_MOVE since it can be self-VP or target-damage
            if isinstance(face_value, ActiveFace) and face_value == ActiveFace.POWER_MOVE:
                choice = input(f"{player.name} rolled POWER_MOVE. Choose 'damage_hp' or 'gain_vp': ").strip()
                if choice == "damage_hp":
                    target_player = input(f"Select target player for {player.name} action {face_value.value}: ")
                    target = next((p for p in self.participants if p.name == target_player), None)
                    if target is None:
                        raise GameStateValidator(f"Target player {target_player} not found among participants.")
                    self.ingame_action_service.execute_action(player=player, action=face_value, target=target, choice_action=choice)
                elif choice == "gain_vp":
                    self.ingame_action_service.execute_action(player=player, action=face_value, choice_action=choice)
                else:
                    raise GameStateValidator("Invalid choice for POWER_MOVE")
                continue

            if self.target_lookup(player, face_value):
                # this will be later replaced by actual py game ui button
                target_player = input(f"Select target player for {player.name} action {face_value.value}: ")

                # validator if the given target player is valid -beta taking input for now
                target = next((p for p in self.participants if p.name == target_player), None)

                if target is None:
                    raise GameStateValidator(f"Target player {target_player} not found among participants.")

                # ask for choice for fallen faces (validation handled in Action_service / Player)
                if isinstance(face_value, FallenFace):
                    if face_value in (fallen_face_vals[2], fallen_face_vals[4]):
                        choice = input("Choose 'heal_hp' or 'gain_vp': ").strip()
                    elif face_value in (fallen_face_vals[3], fallen_face_vals[5]):
                        choice = input("Choose 'damage_hp' or 'steal_vp': ").strip()
                    else:
                        choice = None

                    self.ingame_action_service.execute_action(player=player, action=face_value, target=target, choice_action=choice)
                else:
                    # Targeted active faces (JAB, STRIKE, PICKPOCKET)
                    self.ingame_action_service.execute_action(player=player, action=face_value, target=target)
            else:
                self.ingame_action_service.execute_action(player= player, action= face_value)