import json
import os
import random

AGENTS = json.load(open(os.path.join(os.path.dirname(__file__), "agents.json"), "r"))


def get_random_user_agent():
    return random.choice(AGENTS)["ua"]
