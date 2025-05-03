"""
Terminal UI for the Pokemon Battle Simulator
"""
from typing import List
from battle.battle_engine import BattleEngine
from models.team import PokemonTeam
from models.pokemon import Pokemon

class TerminalUI:
    """User interface for terminal-based Pokemon battles."""

    def show_main_menu(self) -> str:
        """Show the main menu and get user choice."""
        print("\nMAIN MENU")
        print("1. Start New Battle")
        print("2. Instructions")
        print("3. Exit")
        return input("Enter your choice: ").strip()

    def show_instructions(self):
        """Show game instructions."""
        print("\nPOKEMON BATTLE SIMULATOR INSTRUCTIONS")
        print("- Choose your team of Pokemon (up to 6)")
        print("- Battle against an AI opponent")
        print("- During battle, you can:")
        print("  - Select moves by number")
        print("  - Switch Pokemon with 'switch X' (where X is the Pokemon number)")
        print("- The battle continues until one team is defeated")

    def get_pokemon_choice(self) -> str:
        """Get a Pokemon choice from the user."""
        return input("\nEnter a Pokemon name (or 'done' to finish): ").strip()

    def start_battle(self, battle: BattleEngine):
        """Start and manage a battle."""
        print("\nBATTLE STARTED!")

        while not battle.is_battle_over():
            status = battle.get_battle_status()
            self._display_battle_status(status)

            # Player's turn
            player_choice = self._get_player_choice(status["player_pokemon"])
            turn_log = battle.process_turn(player_choice)

            # Display turn results
            for message in turn_log:
                print(message)

            print()  # Empty line for spacing

        # Battle over
        winner = battle.get_winner()
        if winner == "Player":
            print("\nCONGRATULATIONS! You won the battle!")
        else:
            print("\nYou lost the battle. Better luck next time!")

    def _display_battle_status(self, status: dict):
        """Display the current battle status."""
        player = status["player_pokemon"]
        opponent = status["ai_pokemon"]

        print(f"\nOpponent's {opponent.name}: HP {opponent.current_hp}/{opponent.stats['hp']}")
        print(f"Your {player.name}: HP {player.current_hp}/{player.stats['hp']}")

        # Show available moves
        print("\nAvailable moves:")
        for i, move in enumerate(player.moves, 1):
            print(f"{i}. {move.name} (PP: {move.current_pp}/{move.pp})")

        # Show team status
        print("\nYour team:")
        for i, p in enumerate(status["player_team_status"], 1):
            status = "FAINTED" if p["fainted"] else f"HP {p['hp']}/{p['max_hp']}"
            print(f"{i}. {p['name']} - {status}")

    def _get_player_choice(self, pokemon) -> str:
        """Get the player's battle choice."""
        while True:
            choice = input("\nChoose a move (1-4) or 'switch X' to switch Pokemon: ").strip().lower()

            if choice.startswith("switch"):
                return choice

            try:
                move_num = int(choice)
                if 1 <= move_num <= len(pokemon.moves):
                    return choice
                print("Invalid move number. Please choose 1-4.")
            except ValueError:
                print("Invalid input. Please enter a move number or 'switch X'.")