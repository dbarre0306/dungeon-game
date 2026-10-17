from dungeon_game.domain.actors.combatant import Combatant


class Enemy(Combatant):
    name: str
    weapon: str

    @property
    def offensive_weapon(self) -> str:
        return self.weapon

    def get_extra_damage(self) -> int:
        return 0
