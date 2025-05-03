from typing import Dict
from models.pokemon import Pokemon
from models.team import PokemonTeam

class TerminalUI:
    def show_main_menu(self) -> str:
        print("\nMAIN MENU")
        print("1. Start New Battle")
        print("2. Instructions")
        print("3. Exit")
        return input("Enter your choice: ").strip()

    def show_instructions(self):
        print("\nPOKEMON BATTLE SIMULATOR INSTRUCTIONS")
        print("- Choose your team of Pokemon (up to 6)")
        print("- Battle against an AI opponent")
        print("- During battle, you can:")
        print("  - Select moves by number")
        print("  - Switch Pokemon with 'switch X' (where X is the Pokemon number)")
        print("- The battle continues until one team is defeated")

    def get_pokemon_choice(self) -> str:
        return input("\nEnter a Pokemon name (or 'done' to finish): ").strip()

    def start_battle(self, battle):
        print("\nBATTLE STARTED!")
        while not battle.is_battle_over():
            status = battle.get_battle_status()
            self._display_battle_status(status)
            player_choice = self._get_player_choice(status["player_pokemon"])
            turn_log = battle.process_turn(player_choice)

            for message in turn_log:
                print(message)
            print()

        winner = battle.get_winner()
        if winner == "Player":
            print("\nCONGRATULATIONS! You won the battle!")
        else:
            print("\nYou lost the battle. Better luck next time!")

    def _display_battle_status(self, status: Dict):
        player = status["player_pokemon"]
        opponent = status["ai_pokemon"]

        print(f"\nOpponent's {opponent.name}: HP {opponent.current_hp}/{opponent.stats['hp']}")
        print(f"Your {player.name}: HP {player.current_hp}/{player.stats['hp']}")

        print("\nAvailable moves:")
        for i, move in enumerate(player.moves, 1):
            print(f"{i}. {move.name} (PP: {move.current_pp}/{move.max_pp})")

        print("\nYour team:")
        for i, p in enumerate(status["player_team_status"], 1):
            status = "FAINTED" if p["fainted"] else f"HP {p['hp']}/{p['max_hp']}"
            print(f"{i}. {p['name']} - {status}")

    def _get_player_choice(self, pokemon) -> str:
        while True:
            choice = input("\nChoose a move (1-4) or 'switch X' to switch Pokemon: ").strip().lower()

            if choice.startswith("switch"):
                return choice

            try:
                move_num = int(choice)
                if 1 <= move_num <= len(pokemon.moves):
                    return choice
                print(f"Invalid move number. Please choose 1-{len(pokemon.moves)}.")
            except ValueError:
                print("Invalid input. Please enter a move number or 'switch X'.")