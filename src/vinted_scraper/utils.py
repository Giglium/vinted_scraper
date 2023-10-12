import json
import os
import random


def get_random_user_agent():
    with open(os.path.join(os.path.dirname(__file__), "agents.json"), "r") as file:
        data = json.load(file)
        random_agent = random.choice(data)
        return random_agent["ua"]
