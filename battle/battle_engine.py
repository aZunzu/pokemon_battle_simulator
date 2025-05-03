"""
Battle Engine for Pokemon Battle Simulator
Handles battle mechanics, damage calculation, and turn processing
"""
import random
from typing import Dict, List, Optional, Tuple, Union
from battle.type_chart import TYPE_CHART
from models.pokemon import Pokemon
from models.team import PokemonTeam

class BattleEngine:
    """Engine that handles Pokemon battles."""

    def __init__(self, player_team: PokemonTeam, ai_team: PokemonTeam):
        """Initialize battle engine with player and AI teams."""
        self.player_team = player_team
        self.ai_team = ai_team
        self.turn_count = 0
        self.battle_log = []

    def _calculate_type_effectiveness(self, move_type: str, defender_types: List[str]) -> float:
        """Calculate type effectiveness multiplier."""
        multiplier = 1.0
        for def_type in defender_types:
            if move_type in TYPE_CHART and def_type in TYPE_CHART[move_type]:
                multiplier *= TYPE_CHART[move_type][def_type]
        return multiplier

    def _calculate_damage(self, attacker: Pokemon, defender: Pokemon, move_index: int) -> int:
        """Calculate damage for a move."""
        move = attacker.moves[move_index]

        if move.category == "status":
            return 0

        level = attacker.level
        power = move.power

        if move.category == "physical":
            attack_stat = attacker.stats["attack"]
            defense_stat = defender.stats["defense"]
        else:
            attack_stat = attacker.stats["special-attack"]
            defense_stat = defender.stats["special-defense"]

        damage = ((2 * level / 5 + 2) * power * (attack_stat / defense_stat)) / 50 + 2

        if move.type in attacker.types:
            damage *= 1.5

        type_effectiveness = self._calculate_type_effectiveness(move.type, defender.types)
        damage *= type_effectiveness
        damage *= random.uniform(0.85, 1.0)

        return max(1, int(damage))

    def _apply_move(self, attacker: Pokemon, defender: Pokemon, move_index: int) -> Tuple[int, str, float]:
        """Apply a move from attacker to defender."""
        move = attacker.moves[move_index]

        if random.uniform(0, 100) > move.accuracy:
            return 0, f"{attacker.name}'s {move.name} missed!", 0.0

        move.current_pp -= 1

        if move.category in ["physical", "special"]:
            damage = self._calculate_damage(attacker, defender, move_index)
            defender.current_hp = max(0, defender.current_hp - damage)

            effectiveness = self._calculate_type_effectiveness(move.type, defender.types)
            effect_msg = ""
            if effectiveness > 1.5:
                effect_msg = "It's super effective!"
            elif effectiveness < 0.5:
                effect_msg = "It's not very effective..."
            elif effectiveness == 0:
                effect_msg = "It has no effect..."

            message = f"{attacker.name} used {move.name}!"
            if effect_msg:
                message += f" {effect_msg}"
            if damage > 0:
                message += f" {defender.name} lost {damage} HP!"

            return damage, message, effectiveness

        return 0, f"{attacker.name} used {move.name}!", 1.0

    def _ai_select_move(self, ai_pokemon: Pokemon, player_pokemon: Pokemon) -> int:
        """AI selects the best move to use."""
        best_damage = -1
        best_move_index = 0

        for i, move in enumerate(ai_pokemon.moves):
            if move.current_pp <= 0:
                continue

            if move.category in ["physical", "special"]:
                effectiveness = self._calculate_type_effectiveness(move.type, player_pokemon.types)
                expected_damage = move.power * effectiveness
                if move.type in ai_pokemon.types:
                    expected_damage *= 1.5
                if expected_damage > best_damage:
                    best_damage = expected_damage
                    best_move_index = i
            else:
                if best_damage < 20:
                    best_damage = 20
                    best_move_index = i

        return best_move_index

    def _ai_decide_switch(self) -> Optional[int]:
        """AI decides whether to switch Pokemon."""
        current_pokemon = self.ai_team.get_active_pokemon()
        player_pokemon = self.player_team.get_active_pokemon()

        if current_pokemon.current_hp > current_pokemon.stats["hp"] * 0.3:
            return None

        best_matchup_score = -1000
        best_index = None
        current_score = self._calculate_matchup_score(current_pokemon, player_pokemon)

        for i, pokemon in enumerate(self.ai_team.pokemon):
            if i == self.ai_team.active_pokemon_index or pokemon.is_fainted():
                continue
            score = self._calculate_matchup_score(pokemon, player_pokemon)
            if score > current_score + 50 and score > best_matchup_score:
                best_matchup_score = score
