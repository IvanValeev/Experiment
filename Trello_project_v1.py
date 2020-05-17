import requests
import trello
import unittest
import key_token
from trello import TrelloClient
from trello.lists import Lists
from trello.cards import Cards
from trello.boards import Boards



key = key_token.key
token = key_token.token

def connection(url, key, token):

    params_key_and_token = {'key':key,'token':token}
    arguments = {'fields': 'name', 'lists': 'open'}

    return requests.get(url, params=params_key_and_token, data=arguments)

def my_get_boards(key, token):

    dict_of_boards_ids = {}

    url = 'https://api.trello.com/1/members/me/boards'  
    response_array_of_dict = connection(url, key, token).json()

    for board in response_array_of_dict:
        dict_of_boards_ids[board['name']] = board['id']

    return dict_of_boards_ids

def my_get_lists(board_id, key, token):

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

def add_label_to_card(key, token, card_id, color):
    client = Cards(key, token)
    client.new_label(card_id, color)



class Test(unittest.TestCase):

    def setUp(self):
        create_new_board(key, token, 'Testboard')
        board_id = my_get_boards(key, token)['Testboard']
        add_list_to_board(key,token, board_id, 'Testlist')
        add_card_to_list(key, token, my_get_lists(board_id, key, token)['Testlist'], 'Testcard')
        add_label_to_card(key, token, my_get_cards(my_get_lists(board_id, key, token)['Testlist'], key, token)['Testcard'], 'green')

    def tearDown(self):
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
        actual_result = my_get_lists('5eac513a8210603f2e657a9c', key, token)
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
        self.assertTrue('Testlist' in my_get_lists(my_get_boards(key, token)['Testboard'], key, token).keys())

    def test_add_card_to_list(self):
        self.assertTrue('Testcard' in my_get_cards(my_get_lists(my_get_boards(key, token)['Testboard'], key, token)['Testlist'], key, token).keys())

    def test_add_label_to_card(self):
        board_id = my_get_boards(key, token)['Testboard']
        self.assertTrue('green' in my_get_label(key,token, my_get_cards(my_get_lists(board_id, key, token)['Testlist'], key, token)['Testcard']).keys())

unittest.main(verbosity=2)





