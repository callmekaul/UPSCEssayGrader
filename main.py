from dotenv import load_dotenv
load_dotenv()

from utils import pretty_print
from schemas import EssayState
from build_graph import workflow

topic = "It's best to see Life as a journey, not a destination."
essay = """<essay_text>"""
initial_state: EssayState = {
    "topic": topic,
    "essay": essay
}

result = workflow.invoke(initial_state)
pretty_print(result)