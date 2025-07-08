from os import environ
CHANNEL_ROUTING = 'routing.channel_routing'

SESSION_CONFIGS = [

    dict(
        name='Voting_send',
        display_name="Voting_send",
        app_sequence=['A_Voting_one', 'A_Voting_two', 'A_Voting_three', 'A_Voting_four', 'A_Voting_payment'],
        num_demo_participants=3,
    ),
    dict(
        name='Voting_receive',
        display_name="Voting_receive",
        app_sequence=['A_Voting_one', 'A_Voting_two', 'A_Voting_three_receiver', 'A_Voting_four_receiver','A_Voting_payment_receiver'],
        num_demo_participants=3,
    ),
    dict(
        name='Voting',
        display_name="Voting",
        app_sequence=['Voting_Block_One_individual_nochat', 'Voting_Block_Two_nochat', 'Voting_Block_Three_partial_chat', 'Voting_Block_Four_full_chat', 'Voting_payment'],
        num_demo_participants=3,
    ),
    dict(
        name='try',
        display_name="try",
        app_sequence=['Voting_try'],
        num_demo_participants=3,
    )
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
