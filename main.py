import sys
from ui.terminal_ui import TerminalUI
from models.team import PokemonTeam
from battle.battle_engine import BattleEngine
from data.pokeapi import PokeAPIClient
from data.championship_teams import ChampionshipTeams

def main():
    print("====================================")
    print("    POKEMON BATTLE SIMULATOR")
    print("====================================")
    print("Loading PokeAPI data...")

    api_client = PokeAPIClient()
    teams_data = ChampionshipTeams(api_client)
    ui = TerminalUI()

    while True:
        choice = ui.show_main_menu()

        if choice == '1':
            player_team = create_player_team(ui, api_client)
            ai_team = teams_data.get_random_team()
            battle = BattleEngine(player_team, ai_team)
            ui.start_battle(battle)
        elif choice == '2':
            ui.show_instructions()
        elif choice == '3':
            print("Thank you for playing Pokemon Battle Simulator!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

def create_player_team(ui, api_client):
    team = PokemonTeam("Player's Team")
    print("\nLet's build your team!")
    print("You can have up to 6 Pokemon in your team.")
    print("Available Pokemon examples: Pikachu, Charmander, Bulbasaur, Squirtle, Eevee")

    while len(team.pokemon) < 6:
        pokemon_name = ui.get_pokemon_choice()

        if pokemon_name.lower() == 'done':
            if len(team.pokemon) > 0:
                break
            print("You need at least one Pokemon in your team!")
            continue

        try:
            pokemon = api_client.get_pokemon(pokemon_name.lower())
            if pokemon:
                team.add_pokemon(pokemon)
                print(f"{pokemon.name} added to your team!")
                print(f"Current team: {', '.join(p.name for p in team.pokemon)}")
            else:
                print("That Pokemon couldn't be loaded. Try another one.")
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please try a different Pokemon name.")

        print(f"Team size: {len(team.pokemon)}/6")

    return team

if __name__ == "__main__":
    main()