from dungeon_game.domain.actors.combatant import Combatant


class Enemy(Combatant):
    name: str
    weapon: str

    def get_weapon(self) -> str:
        return self.weapon

    def get_extra_damage(self) -> int:
        return 0
