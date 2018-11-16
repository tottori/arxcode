from .models import GeneratedLootFragment, Shardhaven
from typeclasses.bauble import Bauble
from typeclasses.wearable.wieldable import Wieldable
from evennia.utils import create
import random


class Trinket(Bauble):

    @property
    def type_description(self):
        return "trinket"


class AncientWeapon(Wieldable):

    @property
    def type_description(self):
        if self.recipe:
            return "ancient %s" % self.recipe.name
        return "ancient weapon"


class LootGenerator(object):

    WPN_SMALL = 0
    WPN_MEDIUM = 1
    WPN_HUGE = 2
    WPN_BOW = 3

    @classmethod
    def create_trinket(cls, haven):
        name = GeneratedLootFragment.generate_trinket_name()
        trinket = create.create_object(typeclass="world.exploration.loot.Trinket", key=name)
        trinket.db.desc = "\nAn ancient trinket, one that feels slightly warm to the touch.\n"
        trinket.db.quality_level = random.randint(4, 11)
        trinket.db.found_shardhaven = haven.name
        return trinket

    @classmethod
    def get_weapon_recipe(cls, material, wpn_type=WPN_MEDIUM):

        recipes = {
            'steel': {
                LootGenerator.WPN_SMALL: 105,
                LootGenerator.WPN_MEDIUM: 111,
                LootGenerator.WPN_HUGE: 117,
                LootGenerator.WPN_BOW: 134,
            },
            'rubicund': {
                LootGenerator.WPN_SMALL: 106,
                LootGenerator.WPN_MEDIUM: 112,
                LootGenerator.WPN_HUGE: 118,
                LootGenerator.WPN_BOW: 135,
            },
            'diamondplate': {
                LootGenerator.WPN_SMALL: 107,
                LootGenerator.WPN_MEDIUM: 113,
                LootGenerator.WPN_HUGE: 119,
                LootGenerator.WPN_BOW: 136,
            },
            'alaricite': {
                LootGenerator.WPN_SMALL: 108,
                LootGenerator.WPN_MEDIUM: 114,
                LootGenerator.WPN_HUGE: 120,
                LootGenerator.WPN_BOW: 137,
            }
        }

        return recipes[material][wpn_type]

    @classmethod
    def create_weapon(cls, haven, wpn_type=None):

        weapon_types = (LootGenerator.WPN_SMALL, LootGenerator.WPN_MEDIUM, LootGenerator.WPN_HUGE,
                        LootGenerator.WPN_BOW)

        if not wpn_type:
            wpn_type = random.choice(weapon_types)

        difficulty = haven.difficulty_rating
        if difficulty < 3:
            material = random.choice(('steel', 'steel', 'steel', 'rubicund', 'rubicund', 'diamondplate'))
        elif difficulty < 5:
            material = random.choice(('steel', 'rubicund', 'rubicund', 'diamondplate'))
        elif difficulty < 8:
            material = random.choice(('rubicund', 'diamondplate', 'diamondplate', 'alaricite'))
        else:
            material = random.choice(('diamondplate', 'diamondplate', 'alaricite'))

        should_name = material in ['diamondplate', 'alaricite']

        generator_wpn = GeneratedLootFragment.MEDIUM_WEAPON_TYPE
        if wpn_type == LootGenerator.WPN_SMALL:
            generator_wpn = GeneratedLootFragment.SMALL_WEAPON_TYPE
        elif wpn_type == LootGenerator.WPN_HUGE:
            generator_wpn = GeneratedLootFragment.HUGE_WEAPON_TYPE
        elif wpn_type == LootGenerator.WPN_BOW:
            generator_wpn = GeneratedLootFragment.BOW_WEAPON_TYPE

        name = GeneratedLootFragment.generate_weapon_name(material, include_name=should_name, wpn_type=generator_wpn)
        weapon = create.create_object(typeclass="world.exploration.loot.AncientWeapon", key=name)

        desc = "\nAn ancient {adjective} {material} weapon, with {decor} on the {element}.\n"
        if wpn_type == LootGenerator.WPN_BOW:
            desc = "\nAn ancient {adjective} {material} bow, decorated with {decor}.\n"

        adjective = GeneratedLootFragment.pick_random_fragment(GeneratedLootFragment.ADJECTIVE)
        decor = GeneratedLootFragment.pick_random_fragment(GeneratedLootFragment.WEAPON_DECORATION)
        element = GeneratedLootFragment.pick_random_fragment(GeneratedLootFragment.WEAPON_ELEMENT)

        desc = desc.replace("{material}", material)
        desc = desc.replace("{adjective}", adjective)
        desc = desc.replace("{decor}", decor)
        desc = desc.replace("{element}", element)

        weapon.db.desc = desc

        weapon.db.quality_level = random.randint(difficulty, 10)
        weapon.db.found_shardhaven = haven.name
        weapon.db.recipe = LootGenerator.get_weapon_recipe(material, wpn_type=wpn_type)

        return weapon





