#!/usr/bin/env python3

# OVERWATCH LEAGUE WEBSITE WEB SCRAPER THING
import requests, os
from selenium import webdriver
from bs4 import BeautifulSoup

api_url = 'https://api.overwatchleague.com/players?locale=en_US'
base_url = 'https://overwatchleague.com/en-us/'
player_url = base_url +'players/'
#browser = webdriver.Chrome()

# Players
#soup = BeautifulSoup(browser.page_source, features='lxml')
r = requests.get(api_url)
# this is a dictionary that stores all the player information
data = r.json()

def store_players():
    # get the players and info 
    players = {}
    for player in data['content']:
        players[player['name']] = {'full_name': ' '.join([player['givenName'], player['familyName']]), 
                                    'image': player['headshot'], 
                                    'role': player['attributes']['role'],
                                    'team': player['teams'][0]['team']['name'],
                                    'region': player['nationality']}
        if 'heroes' in player['attributes']:
            players[player['name']]['heroes'] = player['attributes']['heroes']
        else:
            players[player['name']]['heroes'] = []
    return players

def download_all_images(players):
    # make the directory
    dir_name = 'player_headshots'
    if os.path.exists(dir_name):
        print("This folder already exists")
    else:
        os.makedirs(dir_name)
        for player in players:
            print("Downloading image for %s" % player)
            res = requests.get(players[player]['image'])
            res.raise_for_status()

            img_file = open(os.path.join(dir_name, player + '.png'), 'wb')
            for chunk in res.iter_content(10000):
                img_file.write(chunk)
            img_file.close()

def find_player(search_name, players):
    # type into the search field for the player
    elem = browser.find_element_by_name('filter')
    elem.send_keys(search_name)

    # check if the number of rows found is empty
    rows = browser.find_elements_by_class_name('Table-row')
    if len(rows) == 0:
        print('No player with that name. Try again')
        elem.clear() # clear the search field
        return 0
    elif len(rows) == 1:
        name = browser.find_element_by_class_name('u-text-gray')
        return name.text
    else:
        print('Too many players found. Try again') # maybe extend this later
        elem.clear()
        return 2

def get_player(name):
    link = browser.find_element_by_link_text(name)
    link.click()

def show_player_info(player):
    print('Name: ' + player['full_name'])
    print('Region: ' + player['region'])
    print('Team: ' + player['team'])
    print('Role: ' + player['role'])
    print('Favourite Hero: ' + player['fav_hero'])

def run_command(players):
    print('What do you want to search for? ')
    print('Type ? for a list of available commands')
    cmd = input()
    if cmd == '?':
        print("'i' for the general player information")
        print("'h' for hero stats")
        print("'o' for overall player stats")
        print("'q' to quit the program")
    elif cmd == 'i':
        show_player_info(players[name])
    elif cmd == 'h':
        pass
    else:
        print('Invalid Command. Try again')

    return cmd != 'q'

if __name__ == '__main__':
    players = store_players()
    exit()
    mode = int(input('Enter mode: '))
    if mode == 1:
        download_all_images(players)
    elif mode == 2:
        # full name player search
        browser.get(player_url)
        found = False
        while not found:
            search_name = input('Which player do you want to search for? ')
            name = find_player(search_name, players)
            if type(name) != int:
                found = True

        # locate the link to the player profile and click it
        get_player(name)

        player_mode = get_command()
        while run_command(players):
            pass

    print('Goodbye')
    browser.close()
