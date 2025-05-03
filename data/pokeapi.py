from typing import Optional
import requests
from models.pokemon import Pokemon
from models.move import Move

class PokeAPIClient:
    BASE_URL = "https://pokeapi.co/api/v2/"

    def get_pokemon(self, name: str) -> Optional[Pokemon]:
        try:
            response = requests.get(f"{self.BASE_URL}pokemon/{name.lower()}", timeout=10)
            response.raise_for_status()
            data = response.json()

            moves = []
            for move_data in data["moves"][:4]:  # Limitar a 4 movimientos
                move_name = move_data["move"]["name"]
                move = self.get_move(move_name)
                if move:
                    moves.append(move)

            if not moves:
                return None

            return Pokemon(
                id=data["id"],
                name=data["name"],
                types=[t["type"]["name"] for t in data["types"]],
                stats={s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
                moves=moves,
                sprite_url=data["sprites"]["front_default"]
            )
        except Exception as e:
            print(f"Error getting Pokemon {name}: {str(e)}")
            return None

    def get_move(self, name: str) -> Optional[Move]:
        try:
            response = requests.get(f"{self.BASE_URL}move/{name.lower()}", timeout=5)
            response.raise_for_status()
            data = response.json()

            return Move(
                id=data["id"],
                name=data["name"],
                type_=data["type"]["name"],
                category=data["damage_class"]["name"],
                power=data["power"] if data["power"] else 0,
                accuracy=data["accuracy"] if data["accuracy"] else 100,
                pp=data["pp"]
            )
        except Exception as e:
            print(f"Error getting move {name}: {str(e)}")
            return None