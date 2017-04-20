from __future__ import print_function, division
import requests
import pickle
import datetime
import re
import csv
import numpy as np
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


def get_href_to_use(soup, date):
    v_cal = soup.find('div', {'id': 'version-calendar'})
    years = v_cal.find_all('section')

    avail = list()
    hrefs = list()
    for year in years:
        for li in year.find_all('li'):
            try:
                a_date_str = li.find('strong').get_text()
                a_date = datetime.datetime.strptime(a_date_str, '%b %Y')
                avail.append(a_date)
                href = li.find('a').get('href')
                base = 'http://sofifa.com'
                hrefs.append(base + href)
            except:
                pass

    my_date = datetime.datetime.strptime(date, '%d/%m/%Y')

    diff = my_date - np.array(avail)
    valid_indices = np.where(diff >= datetime.timedelta(0))
    index_to_choose = valid_indices[diff[valid_indices].argmin()][0]

    return hrefs[index_to_choose]


def get_team_skills(team_id, date):
    url = 'http://sofifa.com/team/{}'.format(team_id)
    driver.get(url)
    sleep(5)
    page_content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(page_content, 'html.parser')

    href = get_href_to_use(soup, date)
    driver.get(href)
    sleep(5)
    page_content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(page_content, 'html.parser')

    keys = ['Overall', 'Attack', 'Midfield', 'Defense']
    stats = soup.find('div', {'class': 'stats'})
    vals = [int(stat.find('span').get_text().strip()) for stat in stats.find_all('td')]

    team_skills = OrderedDict(zip(keys, vals))

    return team_skills


def get_all_team_skills(gen_data, teams_dict):
    date = gen_data.date
    team_skills = OrderedDict()

    for team_name in [gen_data.h_club_name, gen_data.a_club_name]:
        team_id = teams_dict[team_name]
        if team_id is not None:
            team_skills[team_name] = get_team_skills(team_id, date)
        else:
            keys = ['Overall', 'Attack', 'Midfield', 'Defense']
            vals = [None, None, None, None]
            team_skills[team_name] = OrderedDict(zip(keys, vals))

    return team_skills


def main():
    teams_dict = get_updated_teams_dict(pickle.load(open('../data/teams/teams_dict.p', 'rb')))

    for s_end_year in [2016]:
        print("Getting FIFA stats for year {}...".format(s_end_year))
        season_stats = pickle.load(open('../data/season_stats/season_stats_{}.p'.format(s_end_year),'rb'))
        for i in range(5):
            n = len(season_stats[i])
            for j in range(n):
                print("\t- getting stats for match {}/{} of stage {}/{}".format(j+1,n,i+1,5))
                gen_data = season_stats[i][j].gen_data
                players_data = season_stats[i][j].players_data
                team_skills = get_all_team_skills(gen_data, teams_dict)
                season_stats[i][j] = DetailedMatchData(gen_data, players_data, team_skills)

        # write new pickle
        pickle.dump(season_stats, open('../data/season_stats/c_season_stats_{}.p'.format(s_end_year), 'wb'))


if __name__ == '__main__':
    main()
