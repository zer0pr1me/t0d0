from typing import List
from dataclasses import dataclass

@dataclass
class TodolistConfig:
    name: str
    dir: str

@dataclass
class Config:
    todolists: List[TodolistConfig]
