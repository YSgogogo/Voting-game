from otree.api import *
import re
import random
import json

doc = """
reflect the payment in the end
"""


class C(BaseConstants):
    NAME_IN_URL = 'Voting_payment_receiver'
    PLAYERS_PER_GROUP = 1
    NUM_ROUNDS = 1



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    round_to_pay_block_one = models.StringField()
    money_to_pay_block_one = models.IntegerField()
    round_to_pay_block_two = models.IntegerField()
    money_to_pay_block_two = models.IntegerField()
    round_to_pay_block_three = models.IntegerField()
    money_to_pay_block_three = models.IntegerField()
    round_to_pay_block_four = models.IntegerField()
    money_to_pay_block_four = models.IntegerField()
    total_to_pay = models.IntegerField()

    Gender =  models.IntegerField(
        widget=widgets.RadioSelect,
        choices=[
            [0, 'Male'],
            [1, 'Female'],
            [2, 'Others'],
            [3, 'Prefer not to say'],
        ]
    )
    How_choose_info = models.StringField()
    How_choose_state = models.StringField()
    Email_address = models.StringField()

    Major = models.StringField()
    Age = models.StringField()
    Education =  models.IntegerField(
        widget=widgets.RadioSelect,
        choices=[
            [0, 'High school diploma'],
            [1, 'Bachelor’s degree'],
            [2, 'Postgraduate degree'],
            [3, 'Prefer not to say'],
        ]
    )
    Bayes =  models.IntegerField(
        widget=widgets.RadioSelect,
        choices=[
            [0, 'Very familiar'],
            [1, 'Somewhat familiar'],
            [2, 'Not familiar'],
        ]
    )

class Instruction(Page):
    pass



class Survey(Page):
    form_model = 'player'
    form_fields = ['Gender', 'Major', 'Age', 'Education', 'Bayes', 'How_choose_state', 'How_choose_info']
    @staticmethod

    def before_next_page(player: Player, timeout_happened):
        part = player.participant

        # ---------- block 1 ----------
        pay1, rnds1 = part.vars['Voting_Block_One_individual_nochat']
        player.money_to_pay_block_one = pay1
        player.round_to_pay_block_one = json.dumps(rnds1)

        # ---------- block 2 ----------
        pay2, rnd2 = part.vars['Voting_Block_Two_nochat']
        player.money_to_pay_block_two = pay2
        player.round_to_pay_block_two = rnd2

        # ---------- block 3 ----------
        pay3, rnd3 = part.vars['Voting_Block_Three_partial_chat_receiver']
        player.money_to_pay_block_three = pay3
        player.round_to_pay_block_three = rnd3

        pay4, rnd4 = part.vars['Voting_Block_Four_full_chat_receiver']
        player.money_to_pay_block_four = pay4
        player.round_to_pay_block_four = rnd4

        player.total_to_pay = pay1 + pay2 + pay3 + pay4 + 5

        part.payoff = player.total_to_pay


class Email(Page):
    form_model = 'player'
    form_fields = ['Email_address']



class Payment(Page):
    pass


page_sequence = [Instruction, Survey, Email, Payment]