import tcod as libtcod
import math

from game_messages import Message
from components.ai import ConfusedMonster
from fighter_types import FighterTypes


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', libtcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better!', libtcod.green)})

    return results


def heal_stamina(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.unit_type == FighterTypes.PLAYER:
        if entity.fighter.stamina == entity.fighter.max_stamina:
            results.append({'consumed': False, 'message': Message('You are already at full stamina', libtcod.yellow)})
        else:
            entity.fighter.restore_stamina(amount)
            results.append({'consumed': True, 'message': Message('You feel energetic!', libtcod.green)})
    else:
        results.append({'consumed': False,
                        'message': Message('The {0} attempts to open a bottle and fails.'.format(entity.name),
                                           libtcod.white)})

    return results


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []
    target = None

    closest_distance = maximum_range + 1

    if caster.fighter.unit_type == FighterTypes.PLAYER and not caster.fighter.consume_stamina(15):
        results.append({'consumed': False,
                        'message': Message('You lack the stamina to cast spells.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True, 'target': target, 'message': Message(
            'A lighting bolt strikes the {0} with a loud thunder! The damage is {1}'.format(target.name, damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append(
            {'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike.', libtcod.red)})

    return results


def cast_fireball(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    if caster.fighter.unit_type == FighterTypes.PLAYER and not caster.fighter.consume_stamina(15):
        results.append({'consumed': False,
                        'message': Message('You lack the stamina to cast spells.', libtcod.yellow)})
        return results

    results.append({'consumed': True,
        'message': Message('The fireball explodes, burning everything within {0} tiles!'.format(radius),
            libtcod.orange)})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} hit points.'.format(entity.name, damage),
                                                   libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    if caster.fighter.unit_type == FighterTypes.PLAYER and not caster.fighter.consume_stamina(15):
        results.append({'consumed': False,
                        'message': Message('You lack the stamina to cast spells.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({'consumed': True, 'message': Message(
                'The eyes of the {0} look vacant, as he starts to stumble around!'.format(entity.name),
                libtcod.light_green)})

            break
    else:
        results.append(
            {'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results


def cast_force(*args, **kwargs):
    caster = args[0]
    game_map = kwargs.get('game_map')
    entities = kwargs.get('entities')
    distance = kwargs.get('distance')  # Distance enemies get sent flying.
    damage = kwargs.get('damage')  # Damage dealt for each tile remaining.
    target = None  # If any target was hit.

    results = []

    if caster.fighter.unit_type == FighterTypes.PLAYER and not caster.fighter.consume_stamina(15):
        results.append({'consumed': False,
                        'message': Message('You lack the stamina to cast spells.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.distance_to(caster) <= math.sqrt(2) and caster != entity:  # Only hit targets adjacent to caster.
            target = True
            results.append(
                {'consumed': True, 'message': Message('The {0} gets sent flying.'.format(entity.name), libtcod.orange)})
            move_x = entity.x - caster.x
            move_y = entity.y - caster.y
            for i in range(distance):
                prev_x = entity.x
                prev_y = entity.y
                entity.move_check_walls(move_x, move_y, game_map, entities)
                # Deal wallbang damage if position was blocked.
                if entity.fighter and prev_x == entity.x and prev_y == entity.y:
                    wallbang_damage = damage * (distance - i)
                    entity.fighter.take_damage(wallbang_damage)
                    results.append(
                        {'message': Message(
                            'The {0} slams into a wall and takes {1} damage.'.format(entity.name, wallbang_damage),
                            libtcod.orange)})
                    results.extend(entity.fighter.take_damage(wallbang_damage))
                    break  # Stop trying to move entity into walls after a wallbang.

    if not target:
        results.append({'consumed': False, 'message': Message('Nothing is close enough to be affected.', libtcod.red)})

    return results
