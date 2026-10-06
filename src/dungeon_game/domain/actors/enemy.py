from dungeon_game.domain.actors.combatant import Combatant


class Enemy(Combatant):
    name: str
    description: str

    def get_extra_damage(self) -> int:
        return 0
