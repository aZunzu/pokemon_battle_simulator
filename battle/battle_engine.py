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
            # Get effectiveness from type chart
            if move_type in TYPE_CHART and def_type in TYPE_CHART[move_type]:
                multiplier *= TYPE_CHART[move_type][def_type]
        return multiplier

    def _calculate_damage(self, attacker: Pokemon, defender: Pokemon, move_index: int) -> int:
        """Calculate damage for a move."""
        move = attacker.moves[move_index]

        # Skip damage calculation for status moves
        if move.category == "status":
            return 0

        # Base damage formula
        # ((2 * Level / 5 + 2) * Power * A/D / 50) + 2

        level = attacker.level
        power = move.power

        # Select the appropriate attack and defense stats based on move category
        if move.category == "physical":
            attack_stat = attacker.stats["attack"]
            defense_stat = defender.stats["defense"]
        else:  # Special
            attack_stat = attacker.stats["special-attack"]
            defense_stat = defender.stats["special-defense"]

        # Calculate base damage
        damage = ((2 * level / 5 + 2) * power * (attack_stat / defense_stat)) / 50 + 2
        #Calculate critico
        if random.uniform(0,100) < 4:
            damage*=1.5

        # Apply STAB (Same Type Attack Bonus)
        if move.type in attacker.types:
            damage *= 1.5

        # Apply type effectiveness
        type_effectiveness = self._calculate_type_effectiveness(move.type, defender.types)
        damage *= type_effectiveness

        # Apply random factor (85-100%)
        damage *= random.uniform(0.85, 1.0)

        # Return integer damage (minimum 1)
        return max(1, int(damage))

    def _apply_move(self, attacker: Pokemon, defender: Pokemon, move_index: int, isfainted: bool) -> Tuple[int, str, float]:
        """Apply a move from attacker to defender."""
        if isfainted:
            return 0, f"", 0.0
        else:
            move = attacker.moves[move_index]

            # Check if move hits
            accuracy_check = random.uniform(0, 100)
            if accuracy_check > move.accuracy:
                return 0, f"{attacker.name}'s {move.name} missed!", 0.0

            # Reduce PP
            move.current_pp -= 1

            # Handle different move categories
            if move.category in ["physical", "special"]:
                # Calculate and apply damage
                damage = self._calculate_damage(attacker, defender, move_index)
                defender.current_hp = max(0, defender.current_hp - damage)

                # Determine effectiveness message
                effectiveness = self._calculate_type_effectiveness(move.type, defender.types)

                if effectiveness > 1.5:
                    effect_msg = "It's super effective!"
                elif effectiveness < 0.5:
                    effect_msg = "It's not very effective..."
                elif effectiveness == 0:
                    effect_msg = "It has no effect..."
                else:
                    effect_msg = ""

                message = f"{attacker.name} used {move.name}!"
                if effect_msg:
                    message += f" {effect_msg}"

                if damage > 0:
                    message += f" {defender.name} lost {damage} HP!"

                return damage, message, effectiveness

        # Status moves could be implemented here
        # For now, just return a simple message
        return 0, f"{attacker.name} used {move.name}!", 1.0

    def _ai_select_move(self, ai_pokemon: Pokemon, player_pokemon: Pokemon) -> int:
        """AI selects the best move to use."""
        best_damage = -1
        best_move_index = 0

        # Check each move
        for i, move in enumerate(ai_pokemon.moves):
            if move.current_pp <= 0:
                continue  # Skip moves with no PP

            # For damage moves, estimate damage
            if move.category in ["physical", "special"]:
                # Simple heuristic: choose move with highest expected damage
                effectiveness = self._calculate_type_effectiveness(move.type, player_pokemon.types)
                expected_damage = move.power * effectiveness

                # Consider STAB
                if move.type in ai_pokemon.types:
                    expected_damage *= 1.5

                if expected_damage > best_damage:
                    best_damage = expected_damage
                    best_move_index = i
            else:
                # For status moves, assign a base value
                if best_damage < 20:  # Arbitrary threshold
                    best_damage = 20
                    best_move_index = i

        return best_move_index

    def _ai_decide_switch(self) -> Optional[int]:
        """AI decides whether to switch Pokemon."""
        current_pokemon = self.ai_team.get_active_pokemon()
        player_pokemon = self.player_team.get_active_pokemon()

        # Don't switch if current Pokemon is in good shape
        if current_pokemon.current_hp > current_pokemon.stats["hp"] * 0.3:
            return None

        # Check if there's a better matchup
        best_matchup_score = -1000
        best_index = None

        current_score = self._calculate_matchup_score(current_pokemon, player_pokemon)

        for i, pokemon in enumerate(self.ai_team.pokemon):
            if i == self.ai_team.active_pokemon_index or pokemon.is_fainted():
                continue

            score = self._calculate_matchup_score(pokemon, player_pokemon)

            # Only switch if significantly better
            if score > current_score + 50 and score > best_matchup_score:
                best_matchup_score = score
                best_index = i

        return best_index

    def _calculate_matchup_score(self, pokemon1: Pokemon, pokemon2: Pokemon) -> float:
        """Calculate a matchup score between two Pokemon."""
        # Higher is better for pokemon1
        score = 0

        # Consider type effectiveness
        for move in pokemon1.moves:
            if move.category in ["physical", "special"]:
                effectiveness = self._calculate_type_effectiveness(move.type, pokemon2.types)
                score += (effectiveness - 1) * 100

        # Consider defensive typing
        for move in pokemon2.moves:
            if move.category in ["physical", "special"]:
                effectiveness = self._calculate_type_effectiveness(move.type, pokemon1.types)
                score -= (effectiveness - 1) * 100

        # Consider HP percentage
        score += (pokemon1.current_hp / pokemon1.stats["hp"]) * 50

        # Consider speed (being faster is an advantage)
        if pokemon1.stats["speed"] > pokemon2.stats["speed"]:
            score += 30
        else:
            score -= 30

        return score

    def process_turn(self, player_choice: str, player_move_index: Optional[int] = None) -> List[str]:
        """Process a single turn of battle."""
        isfaintedhuman=False
        isfaintedIA=False
        self.turn_count += 1
        turn_log = []

        player_pokemon = self.player_team.get_active_pokemon()
        ai_pokemon = self.ai_team.get_active_pokemon()

        # Handle player's decision
        player_switch = None
        player_move_index = None

        # If player's current Pokémon is fainted, they must switch
        if player_pokemon.is_fainted():
            if player_choice.startswith("switch"):
                try:
                    player_switch = int(player_choice.split()[1])
                    if player_switch < 0 or player_switch >= len(self.player_team.pokemon):
                        turn_log.append("Invalid switch index!")
                        return turn_log
                    if self.player_team.pokemon[player_switch].is_fainted():
                        turn_log.append("That Pokémon has fainted! Choose another.")
                        return turn_log
                    isfaintedhuman=True
                except (IndexError, ValueError):
                    turn_log.append("Invalid switch command!")
                    return turn_log
            else:
                turn_log.append(f"{player_pokemon.name} has fainted! You must switch to another Pokémon.")
                return turn_log

        elif player_choice.startswith("switch"):
            try:
                player_switch = int(player_choice.split()[1])
                if player_switch < 0 or player_switch >= len(self.player_team.pokemon):
                    turn_log.append("Invalid switch index!")
                    return turn_log
                if self.player_team.pokemon[player_switch].is_fainted():
                    turn_log.append("That Pokémon has fainted! Choose another.")
                    return turn_log
            except (IndexError, ValueError):
                turn_log.append("Invalid switch command!")
                return turn_log
        else:
            # It's a move
            try:
                player_move_index = int(player_choice) - 1  # 1-indexed for user, 0-indexed internally
                if player_move_index < 0 or player_move_index >= len(player_pokemon.moves):
                    turn_log.append("Invalid move selection!")
                    return turn_log
                if player_pokemon.moves[player_move_index].current_pp <= 0:
                    turn_log.append("No PP left for that move!")
                    return turn_log
            except ValueError:
                turn_log.append("Invalid command! Enter a move number or 'switch X'")
                return turn_log

        # AI decision
        ai_switch_index = self._ai_decide_switch()
        ai_move_index = None
        if ai_switch_index is None:
            ai_move_index = self._ai_select_move(ai_pokemon, player_pokemon)

        # Handle switches first
        if player_switch is not None:
            if not self.player_team.switch_pokemon(player_switch):
                turn_log.append("Can't switch to that Pokemon!")
                return turn_log
            player_pokemon = self.player_team.get_active_pokemon()
            turn_log.append(f"You switched to {player_pokemon.name}!")

        if ai_switch_index is not None:
            self.ai_team.switch_pokemon(ai_switch_index)
            ai_pokemon = self.ai_team.get_active_pokemon()
            isfaintedIA=True
            turn_log.append(f"Opponent switched to {ai_pokemon.name}!")

        # If both used moves, determine order
        if player_move_index is not None and ai_move_index is not None:
            # Check who goes first (higher speed)
            if player_pokemon.stats["speed"] >= ai_pokemon.stats["speed"]:
                # Player goes first
                damage, message, _ = self._apply_move(player_pokemon, ai_pokemon, player_move_index)
                turn_log.append(message)

                # Check if AI Pokemon fainted
                if ai_pokemon.is_fainted():
                    turn_log.append(f"{ai_pokemon.name} fainted!")
                    # Skip AI's move since their Pokémon fainted
                    # AI will switch next turn automatically
                else:
                    # AI Pokemon attacks
                    damage, message, _ = self._apply_move(ai_pokemon, player_pokemon, ai_move_index)
                    turn_log.append(message)

                    # Check if player Pokemon fainted
                    if player_pokemon.is_fainted():
                        turn_log.append(f"{player_pokemon.name} fainted!")
                        # Player will be forced to switch next turn
            else:
                # AI goes first
                damage, message, _ = self._apply_move(ai_pokemon, player_pokemon, ai_move_index)
                turn_log.append(message)

                # Check if player Pokemon fainted
                if player_pokemon.is_fainted():
                    turn_log.append(f"{player_pokemon.name} fainted!")
                    # Skip player's move since their Pokémon fainted
                    # Player will be forced to switch next turn
                else:
                    # Player Pokemon attacks
                    damage, message, _ = self._apply_move(player_pokemon, ai_pokemon, player_move_index)
                    turn_log.append(message)

                    # Check if AI Pokemon fainted
                    if ai_pokemon.is_fainted():
                        turn_log.append(f"{ai_pokemon.name} fainted!")
                        # AI will switch next turn automatically

        # If only player used a move (due to AI switching earlier)
        elif player_move_index is not None:
            damage, message, _ = self._apply_move(player_pokemon, ai_pokemon, player_move_index, isfaintedIA)
            turn_log.append(message)

            # Check if AI Pokemon fainted
            if ai_pokemon.is_fainted():
                turn_log.append(f"{ai_pokemon.name} fainted!")
                # AI will switch next turn automatically

        # If only AI used a move (due to player switching earlier)
        elif ai_move_index is not None:
            damage, message, _ = self._apply_move(ai_pokemon, player_pokemon, ai_move_index, isfaintedhuman)
            turn_log.append(message)

            # Check if player Pokemon fainted
            if player_pokemon.is_fainted():
                turn_log.append(f"{player_pokemon.name} fainted!")



        # Handle fainted Pokémon at the end of turn
        if ai_pokemon.is_fainted():
            # AI sends out next Pokemon
            next_pokemon_index = self.ai_team.get_first_non_fainted()
            if next_pokemon_index >= 0:
                self.ai_team.switch_pokemon(next_pokemon_index)
                ai_pokemon = self.ai_team.get_active_pokemon()
                turn_log.append(f"Opponent sent out {ai_pokemon.name}!")
            else:
                turn_log.append("You defeated all of the opponent's Pokemon! You win!")

        if player_pokemon.is_fainted():
            # Check if player has more Pokemon
            next_pokemon_index = self.player_team.get_first_non_fainted()
            if next_pokemon_index >= 0:
                turn_log.append("Choose your next Pokemon!")
                # Player will be forced to switch next turn
            else:
                turn_log.append("All your Pokemon have fainted! You lose!")

        # Add to battle log
        self.battle_log.extend(turn_log)
        return turn_log
    def get_battle_status(self) -> Dict:
        """Get the current status of the battle."""
        return {
            "turn": self.turn_count,
            "player_pokemon": self.player_team.get_active_pokemon(),
            "ai_pokemon": self.ai_team.get_active_pokemon(),
            "player_team_status": [
                {"name": p.name, "hp": p.current_hp, "max_hp": p.stats["hp"], "fainted": p.is_fainted()}
                for p in self.player_team.pokemon
            ],
            "ai_team_status": [
                {"name": p.name, "hp": p.current_hp, "max_hp": p.stats["hp"], "fainted": p.is_fainted()}
                for p in self.ai_team.pokemon
            ]
        }

    def is_battle_over(self) -> bool:
        """Check if the battle is over."""
        return self.player_team.is_defeated() or self.ai_team.is_defeated()

    def get_winner(self) -> Optional[str]:
        """Get the winner of the battle."""
        if self.player_team.is_defeated():
            return "AI"
        elif self.ai_team.is_defeated():
            return "Player"
        return None