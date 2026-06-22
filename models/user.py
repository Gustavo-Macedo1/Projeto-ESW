from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    username: str
    senha: str
