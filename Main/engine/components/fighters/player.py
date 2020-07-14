import tcod as libtcod

from game_messages import Message
from fighter import Fighter
from fighter_types import FighterTypes


class Player(Fighter):
    def __init__(self, max_stamina, stamina, max_hp, hp, defense, power, xp=0):
        Fighter.__init__(self, max_hp, hp, defense, power, xp)
        self.unit_type = FighterTypes.PLAYER
        self.base_max_stamina = max_stamina
        self.stamina = stamina

    def consume_stamina(self, amount):
        if self.stamina > 0:
            self.stamina -= amount
            return True
        return False

    def restore_stamina(self, amount):
        self.stamina = min(self.max_stamina, self.stamina + amount)

    @property
    def max_stamina(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_stamina_bonus
        else:
            bonus = 0

        return self.base_max_stamina + bonus

    def attack(self, target):
        results = []

        if self.consume_stamina(10):
            damage = self.power - target.fighter.defense

            if damage > 0:
                results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
                    self.owner.name.capitalize(), target.name, str(damage)), libtcod.white)})
                results.extend(target.fighter.take_damage(damage))
            else:
                results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                    self.owner.name.capitalize(), target.name), libtcod.white)})
        else:
            results.append({'message': Message('You attempt to attack, but lack the stamina to do so.'.format(
                    self.owner.name.capitalize(), target.name), libtcod.red)})

        return results
