"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Nariyah White]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)
import random

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    """
    enemies = {
        "goblin": {"name": "Goblin", "health": 50, "strength": 8, "magic": 2, "xp_reward": 25, "gold_reward": 10},
        "orc": {"name": "Orc", "health": 80, "strength": 12, "magic": 5, "xp_reward": 50, "gold_reward": 25},
        "dragon": {"name": "Dragon", "health": 200, "strength": 25, "magic": 15, "xp_reward": 200, "gold_reward": 100}
    }
    if enemy_type not in enemies:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized.")
    enemy = enemies[enemy_type].copy()
    enemy["max_health"] = enemy["health"]
    return enemy

def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    """
    if character_level <= 2:
        enemy_type = "goblin"
    elif 3 <= character_level <= 5:
        enemy_type = "orc"
    else:
        enemy_type = "dragon"
    return create_enemy(enemy_type)


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    """
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_counter = 0

    def start_battle(self):
        if self.character["health"] <= 0:
            raise CharacterDeadError("Character is already dead.")

        display_battle_log(f"Battle started between {self.character['name']} and {self.enemy['name']}!")

        while self.combat_active:
            self.turn_counter += 1
            display_combat_stats(self.character, self.enemy)
            self.player_turn()
            if not self.combat_active:  # Escaped
                return {"winner": "escaped", "xp_gained": 0, "gold_gained": 0}

            if self.check_battle_end():
                break
            self.enemy_turn()
            if self.check_battle_end():
                break

        winner = self.check_battle_end()
        if winner == "player":
            xp = self.enemy["xp_reward"]
            gold = self.enemy["gold_reward"]
            gain_experience(self.character, xp)
            add_gold(self.character, gold)
            display_battle_log(f"{self.character['name']} defeated {self.enemy['name']} and gained {xp} XP and {gold} gold!")
            return {"winner": "player", "xp_gained": xp, "gold_gained": gold}
        elif winner == "enemy":
            display_battle_log(f"{self.character['name']} was defeated by {self.enemy['name']}.")
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}

    def player_turn(self):
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")
        # For simplicity: always basic attack
        damage = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, damage)
        display_battle_log(f"{self.character['name']} attacks {self.enemy['name']} for {damage} damage.")

    def enemy_turn(self):
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")
        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} attacks {self.character['name']} for {damage} damage.")

    def calculate_damage(self, attacker, defender):
        damage = attacker["strength"] - (defender["strength"] // 4)
        return max(damage, 1)

    def apply_damage(self, target, damage):
        target["health"] = max(target["health"] - damage, 0)

    def check_battle_end(self):
        if self.enemy["health"] <= 0:
            self.combat_active = False
            return "player"
        elif self.character["health"] <= 0:
            self.combat_active = False
            return "enemy"
        return None

    def attempt_escape(self):
        if random.random() < 0.5:
            self.combat_active = False
            display_battle_log(f"{self.character['name']} escaped the battle!")
            return True
        else:
            display_battle_log(f"{self.character['name']} failed to escape.")
            return False


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    cls = character["class"]
    if cls == "Warrior":
        return warrior_power_strike(character, enemy)
    elif cls == "Mage":
        return mage_fireball(character, enemy)
    elif cls == "Rogue":
        return rogue_critical_strike(character, enemy)
    elif cls == "Cleric":
        return cleric_heal(character)
    else:
        return f"{character['name']} has no special ability."


def warrior_power_strike(character, enemy):
    damage = character["strength"] * 2
    enemy["health"] = max(enemy["health"] - damage, 0)
    return f"{character['name']} used Power Strike! {enemy['name']} takes {damage} damage."


def mage_fireball(character, enemy):
    damage = character["magic"] * 2
    enemy["health"] = max(enemy["health"] - damage, 0)
    return f"{character['name']} casts Fireball! {enemy['name']} takes {damage} damage."


def rogue_critical_strike(character, enemy):
    if random.random() < 0.5:
        damage = character["strength"] * 3
        enemy["health"] = max(enemy["health"] - damage, 0)
        return f"{character['name']} lands a Critical Strike! {enemy['name']} takes {damage} damage."
    else:
        damage = character["strength"]
        enemy["health"] = max(enemy["health"] - damage, 0)
        return f"{character['name']} attacks normally. {enemy['name']} takes {damage} damage."


def cleric_heal(character):
    heal_amount = min(30, character["max_health"] - character["health"])
    character["health"] += heal_amount
    return f"{character['name']} heals for {heal_amount} HP."


# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    return character["health"] > 0


def get_victory_rewards(enemy):
    return {"xp": enemy["xp_reward"], "gold": enemy["gold_reward"]}


def display_combat_stats(character, enemy):
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")


def display_battle_log(message):
    print(f">>> {message}")