from __future__ import print_function, division
import requests
import pickle
import datetime
import re
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

MatchData = namedtuple(
        'MatchData',
        ['gen_data', 'players_data']
        )

GenMatchData = namedtuple(
        'GenMatchData',
        ['date', 'h_club_name', 'a_club_name',
         'result', 'h_lineup', 'a_lineup', 'h_manager', 'h_manager_nat', 'a_manager',
         'a_manager_nat', 'h_goals', 'a_goals', 'h_poss', 'a_poss', 'h_ant', 'a_ant', 'h_aft', 'a_aft',
         'h_blocked', 'a_blocked', 'h_post', 'a_post', 'h_corners', 'a_corners', 'h_offs', 'a_offs', 'h_yc', 'a_yc',
         'h_rc', 'a_rc', 'h_fc', 'a_fc', 'h_fs', 'a_fs', 'h_yc_events', 'a_yc_events', 'h_rc_events', 'a_rc_events',
         'h_subs_events', 'a_subs_events', 'h_rgoals_events', 'a_rgoals_events',
         'h_scored_pen_events', 'a_scored_pen_events'])

PlayerMatchData = namedtuple(
        'PlayerMatchData',
        ['name', 'age', 'minutes', 'yellow_cards', 'red_card', 'goals', 'own_goals',
         'penalties_in', 'penalties_mi', 'match_stats_dict'])

def get_id_for_team(team):
    url = 'http://sofifa.com/teams?keyword={}'.format(team)
    driver.get(url)
    sleep(5)
    page_content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(page_content, 'html.parser')

    try:
        table = soup.find('table')
        potential = [my_a for my_a in table.find_all('a') if '/team/' in my_a.get('href')][0]
        team_id = int(potential.get('href').split('/')[-1])
    except:
        print("Unable to map the team {} to an id.".format(team))
        team_id = None

    return team_id


def main():
    teams = set()

    for s_end_year in range(2007, 2016):
        season_stats = pickle.load(open('../data/season_stats/season_stats_{}.p'.format(s_end_year), 'rb'))
        for i in range(5):
            n = len(season_stats[i])
            for j in range(n):
                teams.add(season_stats[i][j].gen_data.h_club_name)
                teams.add(season_stats[i][j].gen_data.a_club_name)

    teams_dict = dict()

    for team in teams:
        likely_id = get_id_for_team(team)
        teams_dict[team] = likely_id

    pickle.dump(teams_dict, open('../data/teams/teams_dict.p', 'wb'))


if __name__ == '__main__':
    main()
