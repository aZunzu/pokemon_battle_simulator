"""
PokeAPI client for the Pokemon Battle Simulator
"""
from typing import Optional
import requests
from models.pokemon import Pokemon
from models.move import Move

class PokeAPIClient:
    """Client for fetching Pokemon data from PokeAPI."""

    BASE_URL = "https://pokeapi.co/api/v2/"

    def get_pokemon(self, name: str) -> Optional[Pokemon]:
        """Get a Pokemon by name."""
        try:
            response = requests.get(f"{self.BASE_URL}pokemon/{name.lower()}")
            response.raise_for_status()
            data = response.json()

            # Get moves (limit to 4)
            moves = []
            for move_data in data["moves"][:4]:
                move_name = move_data["move"]["name"]
                move = self.get_move(move_name)
                if move:
                    moves.append(move)

            if not moves:
                print(f"Warning: No valid moves found for {name}")
                return None

            # Create Pokemon
            return Pokemon(
                id=data["id"],
                name=data["name"],
                types=[t["type"]["name"] for t in data["types"]],
                stats={s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
                moves=moves,
                sprite_url=data["sprites"]["front_default"]
            )
        except Exception as e:
            print(f"Error fetching Pokemon {name}: {str(e)}")
            return None

    def get_move(self, name: str) -> Optional[Move]:
        """Get a move by name."""
        try:
            response = requests.get(f"{self.BASE_URL}move/{name.lower()}")
            response.raise_for_status()
            data = response.json()

            # Verifica que los datos esenciales existan
            if not all(key in data for key in ['type', 'damage_class', 'power', 'accuracy', 'pp']):
                return None

            return Move(
                id=data["id"],
                name=data["name"],
                type_=data["type"]["name"],
                category=data["damage_class"]["name"],
                power=data["power"] if data["power"] is not None else 0,
                accuracy=data["accuracy"] if data["accuracy"] is not None else 100,
                pp=data["pp"]
            )
        except Exception as e:
            print(f"Error fetching move {name}: {str(e)}")
            return None