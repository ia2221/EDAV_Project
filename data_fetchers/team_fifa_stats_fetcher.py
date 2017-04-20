from __future__ import print_function, division
import requests
import pickle
import datetime
import re
import csv
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
                ['gen_data', 'players_data'])

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

DetailedMatchData = namedtuple(
        'DetailedMatchData',
        ['gen_data', 'players_data', 'team_skills'])

def get_updated_teams_dict(teams_dict):
    csv_reader = csv.reader(open('../data/teams/manual_id_mapping.csv', 'r'))
    
    for row in csv_reader:
        team, team_id = row
        teams_dict[team] = int(team_id) if team_id != '-999' else None

    return teams_dict

def get_team_skills(team_id, date):
    url = 'http://sofifa.com/team/{}'.format(team_id)
    driver.get(url)
    sleep(5)
    page_content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(page_content, 'html.parser')

    team_skills = dict()

    return team_skills


def get_all_team_skills(gen_data, teams_dict):
    date = gen_data.date
    team_skills = dict()
    
    for i, team_name in enumerate([gen_data.h_club_name, gen_data.a_club_name]):
        team_id = teams_dict[team_name]
        if team_id is not None:
            team_skills[team_name] = get_team_skills(teams_id, date)
        else:
            team_skills[team_name] = None

    return team_skills


def main():
    teams_dict = get_updated_teams_dict(pickle.load(open('../data/teams/teams_dict.p', 'rb')))

    for s_end_year in range(2007, 2016):
        season_stats = pickle.load(open('../data/season_stats/season_stats_{}.p'.format(s_end_year),'rb'))
        for i in range(5):
            n = len(season_stats[i])
            for j in range(n):
                gen_data = season_stats[i][j].gen_data
                players_data = season_stats[i][j].players_data
                team_skills = get_team_stats(gen_data)
                season_stats[i][j] = DetailedMatchData(gen_data, players_data, team_skills)

        # delete old pickle
        # write new pickle



