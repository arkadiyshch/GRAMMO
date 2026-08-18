from aiogram.fsm.state import State, StatesGroup

class DiagnosticState(StatesGroup):
    choosing_level = State()
    answering = State()


class BlitzState(StatesGroup):
    #choosing_topic_type = State()
    choosing_group = State()
    choosing_topic = State()
    choosing_level = State()
    answering = State()
    choosing_level = State()