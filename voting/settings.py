from os import environ
CHANNEL_ROUTING = 'routing.channel_routing'

SESSION_CONFIGS = [
    dict(
        name='Voting_treatment_1',
        display_name="Voting_treatment_1",
        app_sequence=['Voting_practice_treatment_1', 'Voting_real_treatment_1', 'Voting_payment_treatment_1'],
        num_demo_participants=5,
    ),
    dict(
        name='Voting_treatment_2',
        display_name="Voting_treatment_2",
        app_sequence=['Voting_practice_treatment_2', 'Voting_real_treatment_2', 'Voting_payment_treatment_2'],
        num_demo_participants=5,
    )
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=5.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []


LANGUAGE_CODE = 'en'


REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'Pounds'

ROOMS = [
    dict(
        name='EssexLab',
        display_name='EssexLab',
        participant_label_file='EssexLab.txt',
        #use_secure_urls=True
    ),
]

ADMIN_USERNAME = 'admin'

ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '3323413753712'

INSTALLED_APPS = ['otree', 'otreechat']
