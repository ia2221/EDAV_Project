
from __future__ import print_function, division
import requests
import pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import namedtuple, OrderedDict
from time import sleep

driver = webdriver.PhantomJS()
SeasonData = namedtuple(
        'SeasonData',
        ['season_code', 'rounds_data'])

RoundData = namedtuple(
        'RoundData',
        ['round_code', 'match_codes', 'matches_data'])


def get_soup_from_url(url):
    page = requests.get(url)
    try:
        assert page.status_code == 200
    except AssertionError:
        print("Error: Page not found\n{}".format(url))

    return BeautifulSoup(page.content, 'html.parser')


def get_season_code_for_season_end_year(season_end_year):
    if season_end_year > 2007:
        return season_end_year
    else:
        return season_end_year - 1


def get_round_codes_for_season(season_code):
    print("\t...fetching round codes from season {}".format(season_code))
    url = "https://www.uefa.com/uefachampionsleague/season={}/matches/index.html".format(
            season_code)
    pre_soup = get_soup_from_url(url)

    ko_url = "https://www.uefa.com" + pre_soup.find('a', {'title': 'Knockout phase'}).get('href')
    soup = get_soup_from_url(ko_url)

    round_codes = []

    for round_name in ['Group stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']:
        hyperlink = soup.find('a', {'title': round_name}).get('href')
        round_codes.append((round_name, int(hyperlink.split('/')[-2].split('=')[-1])))

    return round_codes


def get_match_codes_for_season_round(season_code, round_code):
    print("\t...fetching match codes from season {}, round {}".format(season_code, round_code))
    url = "https://www.uefa.com/uefachampionsleague/season={}/matches/round={}/index.html".format(
            season_code,
            round_code)
    driver.get(url)
    sleep(5)
    page_content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(page_content, 'html.parser')

    match_codes = []

    matchday_divs = soup.find_all("div", {"class": "mdsession matchBox innGrid_8 forappnode"})
    for matchday_div in matchday_divs:
        tables = matchday_div.find_all('table')
        for table in tables:
            tbodies = table.find_all('tbody')
            for tbody in tbodies:
                try:
                    match_url = tbody.find('tr', {'class': 'sup'}).find(
                            'span', {'class':'report'}).find('a').get('href')
                    match_code = int(match_url.split('/')[-2].split('=')[-1])
                except:
                    match_tr = tbody.find('tr', {'class': 'sup'})
                    match_code = int([a for a in match_tr.find_all('a') if 'match=' in
                        a.get('href')][0].get('href').split('/')[-2].split('=')[-1])

                match_codes.append(match_code)

    return match_codes


def get_round_data_for_season_round(season_code, round_tuple):
    round_code = round_tuple[1]
    match_codes = get_match_codes_for_season_round(season_code, round_code)
    round_data = RoundData(round_code, match_codes, dict())
    return round_data

def get_all_rounds_data_for_season(season_code):
    all_rounds_data = OrderedDict()

    round_codes = get_round_codes_for_season(season_code)
    for round_tuple in round_codes:
        round_data = get_round_data_for_season_round(season_code, round_tuple)
        all_rounds_data[round_tuple[0]] = round_data

    return all_rounds_data


def get_data_for_season_end_year(season_end_year):
    print("Fetching data for season ending in year {}".format(season_end_year))
    season_code = get_season_code_for_season_end_year(season_end_year)
    rounds_data = get_all_rounds_data_for_season(season_code)
    data = SeasonData(season_code, rounds_data)
    return data


def main():
    codes_data = dict()
    for s_end_year in range(2007, 2017):
        codes_data[s_end_year] = get_data_for_season_end_year(s_end_year)

    pickle.dump(codes_data, open('../data/codes_data.p', 'wb'))


if __name__ == '__main__':
    main()
