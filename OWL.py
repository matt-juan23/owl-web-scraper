#!/usr/bin/env python3

# OVERWATCH LEAGUE WEBSITE WEB SCRAPER THING
import requests, os, time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# starting urls
player_api_url = 'https://api.overwatchleague.com/players?locale=en_US'
stat_api_url = 'https://api.overwatchleague.com/stats/players?stage_id=regular_season&season=2019'
base_url = 'https://overwatchleague.com/en-us/'
player_url = base_url +'players/'

# Class that holds all information about the players
class Players():
    def __init__(self):
        self.info = {}
        self.stats = []

    # store all the players from the api url into a dictionary
    def store_player(self, data, name):
        # get the player's info 
        player_info = {}
        for player in data['content']:
            if name == player['name']:
                player_info = {'gamertag': name,
                                'full_name': ' '.join([player['givenName'], player['familyName']]), 
                                'image': player['headshot'], 
                                'role': player['attributes']['role'],
                                'team': player['teams'][0]['team']['name'],
                                 'region': player['nationality']}
                if 'heroes' in player['attributes']:
                    player_info['heroes'] = map(lambda x: x.capitalize(), player['attributes']['heroes'])
                else:
                    player_info['heroes'] = ['None']

                if 'homeLocation' in player:
                    player_info['hometown'] = player['homeLocation']
                else:
                    player_info['hometown'] = 'Unknown'
                break
        return player_info

    def find_player(self, search_name):
        # wait until the filter search field loads into the website
        elem = WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.NAME, 'filter')))
        # type into the search field for the player
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
            for row in rows:
                name = row.find_element_by_class_name('u-text-gray')
                if name.text.lower() == search_name.lower():
                    return name.text
            print('Too many players found. Try again') # maybe extend this later
            elem.clear()
            return 2

    def get_player(self, name):
        # get the results from the search and click on the link
        link = browser.find_element_by_link_text(name)
        link.click()

    def show_player_info(self):
        print('Gamertag: ' + self.info['gamertag'])
        print('Name: ' + self.info['full_name'])
        print('Region: ' + self.info['region'])
        print('Hometown: ' + self.info['hometown'])
        print('Team: ' + self.info['team'])
        print('Role: ' + self.info['role'].capitalize())
        print('Favourite Heroes: ' + ', '.join(self.info['heroes']))
        print()

    def stat_overview(self):
        # get the table rows for player stats
        for stat in self.stats:
            # print the data
            print('%s: %s' % (stat[0].title(), stat[1]))
            print('Rank: %s' % stat[2])
            print()

    def get_stats(self):
        # get the overall stats for each player and return an array of it
        # wait until the table loads into the page
        _ = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'Table-row')))
        rows = browser.find_elements_by_class_name('Table-row')

        # go through the rows and add the relevent detail to the stats array
        stats = []
        for elem in rows:
            data = self.get_data(elem)
            stats.append(data)
        return stats

    def get_data(self, web_elem, offset=0):
        attributes = web_elem.find_elements_by_tag_name('td')

        if (len(attributes) == 0):
            print('No data available')

        # create an array and store the text of the HTML tag
        data = []
        data.append(attributes[0+offset].text)
        data.append(attributes[1+offset].text)
        data.append(attributes[2+offset].text)
        return data

    def hero_info(self):
        # find all the heroes that the player plays
        heroes = browser.find_elements_by_xpath('//*[@id="player-detail"]/section[2]/div/div/div[1]/table/tbody/*')
        stats = []
        for hero in heroes:
            hero_data = self.get_data(hero, 1)
            stats.append(hero_data)

        # print the data
        for i, stat in enumerate(stats, 1):
            print('%d. %s' % (i, stat[0]))
            print('Time played: %s' % stat[1])
            print('Percentage: %s' % stat[2])
            print()

    def compare(self, p1_name):
        # store the first player's data in one array
        p1 = self.get_stats()

        # store the other player's data in another array
        browser.back()

        # shortened version of one in 'main'
        while True:
            found = False
            cmp_name = input('Which player do you want to compare to? ')
            p2_name = self.find_player(cmp_name)

            if type(p2_name) != int:
                found = True

            if found:
                self.get_player(p2_name)
                break

        # get the second players stats
        p2 = self.get_stats()
        
        # offset for the printing
        offset = 21
        print(p1_name.ljust(offset) + p2_name)
        for i in range(len(p1)):
            # print the stats
            p1_stat = ('%s: %s' % (p1[i][0].title(), p1[i][1])).ljust(offset)
            p2_stat = '%s: %s' % (p2[i][0].title(), p2[i][1])
            print(p1_stat + p2_stat)

            p1_rank = ('Rank: %s' % p1[i][2]).ljust(offset)
            p2_rank = 'Rank: %s' % p2[i][2]
            print(p1_rank + p2_rank)
            print()


# function that downloads all the images
def download_all_images(data):
    images = [{'name': player['name'],
               'img': player['headshot']} for player in data['content']]
    # make the directory
    dir_name = 'player_headshots'
    if os.path.exists(dir_name):
        print("This folder already exists")
    else:
        os.makedirs(dir_name)
        for player in images:
            print("Downloading image for %s" % player['name'])
            res = requests.get(player['img'])
            res.raise_for_status()

            img_file = open(os.path.join(dir_name, player['name'] + '.png'), 'wb')
            for chunk in res.iter_content(10000):
                img_file.write(chunk)
            img_file.close()
        print('Successfully downloaded all images')

def run_command(owl, name):
    print('What do you want to search for? ')
    print('Type ? for a list of available commands')
    cmd = input()
    if cmd == '?':
        help_command()
    elif cmd == 'i':
        owl.show_player_info()
    elif cmd == 'h':
        owl.hero_info()
    elif cmd == 'o':
        owl.stat_overview()
    elif cmd == 'c':
        owl.compare(name)
    elif cmd == 's':
        browser.back()
    elif cmd == 'q':
        pass
    else:
        print('Invalid Command. Try again')

    return cmd if cmd == 'q' else cmd != 's'

def help_command():
    print("'i' for the general player information")
    print("'h' for hero stats")
    print("'o' for overall player stats")
    print("'c' to compare 2 players stats")
    print("'s' to search for another player")
    print("'q' to quit the program")

# Quit the program
def quit():
    print('Goodbye')
    browser.close()
    exit()

'''
WILL USE THIS LATER MAYBE
# store all the players from the api url into a dictionary
def store_players(self):
    # get the players and info
    # request to get the api link
    r = requests.get(player_api_url)
    # this is a dictionary that stores all the player information
    data = r.json() 
    players = {}
    for player in data['content']:
        name = player['name']
        players[name] = {'full_name': ' '.join([player['givenName'], player['familyName']]), 
                         'image': player['headshot'], 
                         'role': player['attributes']['role'],
                         'team': player['teams'][0]['team']['name'],
                         'region': player['nationality']}
        if 'heroes' in player['attributes']:
            players[name]['heroes'] = map(lambda x: x.capitalize(), player['attributes']['heroes'])
        else:
            players[name]['heroes'] = ['None']

        if 'homeLocation' in players:
            players[name]['hometown'] = players['homeLocation']
        else:
            players[name]['hometown'] = 'Unknown'
    return players
'''
if __name__ == '__main__':
    # create a Players object
    owl = Players()

    # get the mode from the user
    mode = int(input('Enter mode: '))

    # get the api url for the players
    r = requests.get(player_api_url)
    # this is a dictionary that stores all the player information
    data = r.json()
    if mode == 1:
        download_all_images(data)
    elif mode == 2:
        # full name player search
        browser = webdriver.Chrome()
        browser.get(player_url)
        while True:
            found = False
            search_name = input('Which player do you want to search for? ')
            if search_name == 'q':
                quit()

            # get the name of the player
            name = owl.find_player(search_name)
            # check if the name is valid
            if type(name) != int:
                found = True

            if found:
                owl.info = owl.store_player(data, name)
                # locate the link to the player profile and click it
                owl.get_player(name)
                owl.stats = owl.get_stats()

                cmd = True
                while cmd and cmd != 'q':
                    # only care about running the run_command function
                    cmd = run_command(owl, name)

                # quit
                if cmd == 'q':
                    quit()

    else: 
        print('Invalid mode. Quitting program')
        exit()