from os import environ
CHANNEL_ROUTING = 'routing.channel_routing'

SESSION_CONFIGS = [


    dict(
        name='Voting',
        display_name="Voting",
        app_sequence=['Voting_Block_One_individual_nochat', 'Voting_Block_Two_nochat', 'Voting_Block_Three_partial_chat', 'Voting_Block_Four_full_chat', 'Voting_payment'],
        num_demo_participants=3,
    ),

    dict(
        name='Voting_receiver',
        display_name="Voting_receiver",
        app_sequence=[
                      'Voting_Block_Three_partial_chat_receiver', 'Voting_Block_Four_full_chat_receiver', 'Voting_payment_receiver'],
        num_demo_participants=3,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
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
