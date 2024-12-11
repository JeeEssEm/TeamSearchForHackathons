from aiogram.fsm.state import StatesGroup, State


class UserForm(StatesGroup):
    achievements = State()
    about_me = State()
    avatar = State()
    user_id = State()
    email = State()
    last_name = State()
    first_name = State()
    middle_name = State()
    university = State()
    course = State()
    group = State()
    roles = State()
    technologies = State()


class RoleForm(StatesGroup):
    roles = State()
    reroute = State()


class HacksForm(StatesGroup):
    user_hacks = State()


class TechnologyForm(StatesGroup):
    selected_technologies = State()


class UserEditForm(StatesGroup):
    about_me = State()
    avatar = State()
    user_id = State()
    last_name = State()
    first_name = State()
    middle_name = State()
    university = State()
    course = State()
    group = State()
    roles = State()


class TeamForm(StatesGroup):
    role = State()
    avatar = State()
    team_name = State()
    team_description = State()
    team_achievements = State()
    current_hackathon = State()


class TeamEditForm(StatesGroup):
    role = State()
    avatar = State()
    team_name = State()
    team_description = State()
    team_achievements = State()
    current_hackathon = State()


class VacancyForm(StatesGroup):
    role = State()
    description = State()
    stack = State()


class LeaveFeedbackForm(StatesGroup):
    feedback = State()


class FiltersForm(StatesGroup):
    role = State()
    techs = State()
