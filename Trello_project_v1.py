import requests
import trello
import unittest
import key_token
from trello import TrelloClient
from trello.lists import Lists
from trello.cards import Cards
from trello.boards import Boards
from trello.board import Board



key = key_token.key
token = key_token.token

def connection(url, key, token, filter=None):

    params_key_and_token = {'key':key,'token':token, 'filter':filter}
    arguments = {'fields': 'name', 'lists': 'open'}

    return requests.get(url, params=params_key_and_token, data=arguments)


def my_get_boards(key, token):

    dict_of_boards_ids = {}

    url = 'https://api.trello.com/1/members/me/boards'  
    response_array_of_dict = connection(url, key, token).json()

    for board in response_array_of_dict:
        dict_of_boards_ids[board['name']] = board['id']

    return dict_of_boards_ids


def my_get_columns(board_id, key, token):

    result={}

    url = f"https://api.trello.com/1/boards/{board_id}/lists"  
    answer = connection(url, key, token).json()

    for list in answer:
        result[list['name']] = list['id']

    return result

def my_get_cards(list_id, key, token):

    dict_of_cards_ids = {}    

    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    response = connection(url, key, token).json()

    for card in response:
        dict_of_cards_ids[card['name']] = card['id']

    return dict_of_cards_ids


def my_get_label(key,token, card_id):

    labels = {}

    url = f"https://api.trello.com/1/cards/{card_id}"
    response = connection(url, key, token).json()

    for label in response['labels']:
        labels[label['color']] = label['id']

    return labels


def my_get_members(key, token, board_id):
    """
    Return dictionary of board member's ({'username':'id'})
    """

    members = {}

    client = Boards(key, token)
    list_of_members = client.get_member(board_id)

    for member in list_of_members:
        members[member['username']] = member['id']

    return members


def create_new_board(key,token, name_of_board):

    client = TrelloClient(key, token)
    client.add_board(name_of_board)


def add_list_to_board(key,token, board_id, name_of_list):

    client = Lists(key, token)
    client.new(name_of_list, board_id)


def add_card_to_list(key, token, list_id, name_of_card):

    client = Cards(key, token)
    client.new(name_of_card, list_id)


def add_label_to_card(key, token, card_id, color, name=None):

    client = Cards(key, token)
    client.new_label(card_id, color, name)

def is_legend_absent(board_id, key, token):

    '''
    This method checks if there is a legend column in the table, if it is absent, it creates it with a list of board members.
    '''
    members = my_get_members(key, token, board_id)

    if 'Legend' not in my_get_columns(board_id, key, token):
        add_list_to_board(key,token, board_id, 'Legend')
        for member in members.keys():
            add_card_to_list(key, token, my_get_columns(board_id, key, token)['Legend'], member)
 
    elif 'Legend' in my_get_columns(board_id, key, token) and my_get_cards(my_get_columns(board_id, key, token)['Legend'], key, token).keys() != my_get_members(key, token, board_id).keys():

        id = my_get_columns(board_id, key, token)['Legend']
        params_key_and_token = {'key':key,'token':token}
        url = f"https://api.trello.com/1/lists/{id}/archiveAllCards"

        response = requests.request(
        "POST",
        url,
        params = params_key_and_token
        )
    
        for member in members.keys():
            add_card_to_list(key, token, my_get_columns(board_id, key, token)['Legend'], member)


def unique_legend_labels(key, token, board_id):
    """
    Adds unique labels for all cards in Legend
    """
    colors = ['green', 'orange', 'purple', 'blue', 'lime', 'pink', 'sky', 'black']
    legend_id = my_get_columns(board_id, key, token)['Legend']
    members = my_get_cards(legend_id, key, token)
    members_names = list(members.keys())

    for i in range(len(members_names)):
        if i < len(colors):
            j = i
            add_label_to_card(key, token, members[members_names[i]], colors[j], name=members_names[i])
        elif i >= len(colors):
            j = i - len(colors)
            add_label_to_card(key, token, members[members_names[i]], colors[j], name=members_names[i])


def labels_according_to_legend(key, token, board_id):
    """
    Coloring of existed cards according to legend
    """

    client = TrelloClient(key, token)
    board = Board(client= client, board_id=board_id)
    list_of_lists = board.list_lists(list_filter='open')
    creators = my_get_members(key, token, board_id)
    legend_id =''
    legend_labels = {}
    list_of_cards = []

    for list in range(len(list_of_lists)):

        if list_of_lists[list].name == 'Legend':
            legend_id = list_of_lists[list].id
            list_of_lists.pop(list)
            break
    
    get_cards = my_get_cards(legend_id, key, token)

    for card in get_cards.keys():
        for label in my_get_label(key,token, get_cards[card]):
            legend_labels[creators[card]] = my_get_label(key,token, get_cards[card])[label]

    for list in list_of_lists:
        for card in list.list_cards():
            list_of_cards.append(card)

    for card in list_of_cards:
        id = card.id
        url = f"https://api.trello.com/1/cards/{id}/actions"
        response = connection(url, key, token, filter=['updateCard', 'createCard'])
        client = Cards(key,token)

        try:
            client.new_idLabel(id, legend_labels[response.json()[0]['idMemberCreator']])
        except:
            pass

def unlim_labeling(key, token, board_id):

    while True:
        print('Working...')
        labels_according_to_legend(key, token, board_id)

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_new_board(key, token, 'Testboard')
        board_id = my_get_boards(key, token)['Testboard']
        add_list_to_board(key,token, board_id, 'Testlist')
        add_card_to_list(key, token, my_get_columns(board_id, key, token)['Testlist'], 'Testcard')
        add_label_to_card(key, token, my_get_cards(my_get_columns(board_id, key, token)['Testlist'], key, token)['Testcard'], 'green')
    
    @classmethod
    def tearDownClass(cls):
        del_id = my_get_boards(key, token)['Testboard']
        params_key_and_token = {'key':key,'token':token}

        del_url = f"https://api.trello.com/1/boards/{del_id}"

        response = requests.request(
           "DELETE",
           del_url,
           params = params_key_and_token
        )

    def test_connection(self):
        url = 'https://api.trello.com/1/members/me/boards'
        actual_result = connection(url, key, token).status_code
        excepted_result = 200
        self.assertEqual(excepted_result, actual_result)


    def test_len_dict_boards(self):
        client = TrelloClient(key, token)
        actual_result = len(my_get_boards(key, token))
        excepted_result = len(client.list_boards())
        self.assertEqual(excepted_result, actual_result)


    def test_dict_of_boards_ids(self):
        actual_result = my_get_boards(key, token)
        excepted_result = {
            'Create via API': '5ead770bdaa73f45e9cb0968', 
            'Rest API': '5eb2d68cd8514f85c9f94240', 
            'Vanya Tasks': '5ead2bd3c7b1a704c70c48b6', 
            'Тестовая доска': '5eac513a8210603f2e657a9c',
            'Testboard': ''
            }
        self.assertEqual(excepted_result.keys(), actual_result.keys())


    def test_dict_of_lists_ids(self):
        actual_result = my_get_columns('5eac513a8210603f2e657a9c', key, token)
        excepted_result = {
            'Проверка для работы с трелло': '5eac529b3259392b2fbf4017', 
            'Тестовая колонка': '5eac55179f121b6db36d5ae0', 
            'Legend': '5eac52fc783f8513d2415008', 
            'Я тут': '5ead67a15746b524fcfe50e4'
            }
        self.assertEqual(excepted_result, actual_result)


    def test_dict_of_cards_ids(self):
        actual_result = my_get_cards('5ead67a15746b524fcfe50e4', key, token)
        excepted_result = {
            'TTTTTest': '5eb1a2b9b064cf25f2732a36'
            }
        self.assertEqual(excepted_result, actual_result)


    def test_create_board(self):
        self.assertTrue('Testboard' in my_get_boards(key, token).keys())


    def test_add_list_to_board(self):
        self.assertTrue('Testlist' in my_get_columns(my_get_boards(key, token)['Testboard'], key, token).keys())


    def test_add_card_to_list(self):
        self.assertTrue('Testcard' in my_get_cards(my_get_columns(my_get_boards(key, token)['Testboard'], key, token)['Testlist'], key, token).keys())


    def test_add_label_to_card(self):
        board_id = my_get_boards(key, token)['Testboard']
        self.assertTrue('green' in my_get_label(key,token, my_get_cards(my_get_columns(board_id, key, token)['Testlist'], key, token)['Testcard']).keys())


    def test_is_legend_absent(self):
        is_legend_absent(my_get_boards(key, token)['Testboard'], key, token)
        self.assertTrue('Legend' in my_get_columns(my_get_boards(key, token)['Testboard'], key, token))


    def test_legend_content(self):
        is_legend_absent(my_get_boards(key, token)['Testboard'], key, token)
        lists_of_board = my_get_columns(my_get_boards(key, token)['Testboard'], key, token)
        actual_result = my_get_cards(lists_of_board['Legend'], key, token).keys()
        excepted_result = my_get_members(key, token, my_get_boards(key, token)['Testboard']).keys()
        self.assertEqual(excepted_result, actual_result)


    def test_unique_legend_labels(self):
        is_legend_absent(my_get_boards(key, token)['Testboard'], key, token)

        try:
            unique_legend_labels(key, token, my_get_boards(key, token)['Testboard'])
        except:
            pass

        card_ids = my_get_cards(my_get_columns(my_get_boards(key, token)['Testboard'], key, token)['Legend'], key, token)
        actual_result = []

        for id in card_ids.keys():
            id = card_ids[id]
            url = f'https://trello.com/1/cards/{id}/labels'
            response = connection(url, key, token)
            actual_result.append(response.json()[0]['name'])

        excepted_result = list(my_get_members(key, token, my_get_boards(key, token)['Testboard']).keys())
        self.assertEqual(excepted_result, actual_result)

    def test_labels_according_to_legend(self):

        board_id = my_get_boards(key, token)['Testboard']
        is_legend_absent(board_id, key, token)

        unique_legend_labels(key, token, my_get_boards(key, token)['Testboard'])
        lists = my_get_columns(board_id, key, token)
        labels_according_to_legend(key, token, board_id)
        legend_card = my_get_cards(lists['Legend'], key, token)
        cards = my_get_cards(lists['Testlist'], key, token)

        self.assertTrue(my_get_label(key,token, legend_card['ivan_valeev'])['green'] in my_get_label(key,token, cards['Testcard']).values())

unittest.main(verbosity=2)




