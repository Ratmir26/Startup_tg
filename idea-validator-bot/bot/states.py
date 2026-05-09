from aiogram.fsm.state import State, StatesGroup


class IdeaCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_argument_text = State()
    waiting_for_argument_weight = State()


class IdeaLoad(StatesGroup):
    waiting_for_number = State()


class HypothesisSurvey(StatesGroup):
    waiting_for_audience = State()
    waiting_for_frequency = State()
    waiting_for_payment = State()
    waiting_for_competitors = State()
    waiting_for_testability = State()
