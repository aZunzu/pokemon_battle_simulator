from ui.pygame_ui import PyGameUI
from data.pokeapi import PokeAPIClient
from models.team import PokemonTeam
from battle.battle_engine import BattleEngine

def main():
    ui = PyGameUI()
    api_client = PokeAPIClient()

    while True:
        choice = ui.show_main_menu()

        if choice == "start":
            # Crea equipos y comienza batalla
            player_team = PokemonTeam("Player")
            player_team.add_pokemon(api_client.get_pokemon("pikachu"))

            enemy_team = PokemonTeam("Enemy")
            enemy_team.add_pokemon(api_client.get_pokemon("charmander"))

            battle = BattleEngine(player_team, enemy_team)
            run_battle(ui, battle)

def run_battle(ui: PyGameUI, battle: BattleEngine):
    while not battle.is_battle_over():
        status = battle.get_battle_status()
        move_index = ui.show_battle(status["player_pokemon"], status["ai_pokemon"])
        battle.process_turn(str(move_index + 1))  # Convertir a 1-based index

if __name__ == "__main__":
    main()