from dungeon_game.domain.actors.combatant import Combatant


class Enemy(Combatant):
    name: str
    weapon: str
    damage_die_sides: int = 6
    damage_bonus: int = 0

    @property
    def offensive_weapon(self) -> str:
        return self.weapon

    @property
    def damage_die(self) -> int:
        return self.damage_die_sides

    @property
    def additional_offensive_weapon_damage(self) -> int:
        return self.damage_bonus
