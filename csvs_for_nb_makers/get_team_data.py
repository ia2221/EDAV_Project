import requests
from bs4 import BeautifulSoup

def write_clubs_performance_by_year_csv():
    page = requests.get('https://en.wikipedia.org/wiki/UEFA_Champions_League_clubs_performance_comparison')
    soup = BeautifulSoup(page.content, 'html.parser')

    t = soup.find_all('table')[1]

    open('club_performance_by_year.csv', 'w').close()

    for row in t.find_all('tr'):
        current_row = ''
        for col in row.find_all('td'):
            if col.get_text().encode('utf8') == b'\xe2\x80\xa2':
                current_row += 'NP,'
            elif col.get_text() == '':
                current_row += 'TDB,'
            else:
                current_row += col.get_text() + ','
        with open('club_performance_by_year.csv', 'a') as f:
            f.write(current_row[:-1] + '\n')


def write_country_participiation_by_year_csv():
    page = requests.get('https://en.wikipedia.org/wiki/UEFA_Champions_League_clubs_performance_comparison')
    soup = BeautifulSoup(page.content, 'html.parser')

    t = soup.find_all('table')[1]

    open('country_participation_by_year.csv', 'w').close()

    for row in t.find_all('tr'):
        current_row = ''

        if 'flagicon' in str(row) and '(' in row.find_all('td')[1].get_text():
            current_row += row.find_all('td')[0].get_text().split()[0] + ','
            for col in row.find_all('td')[1:]:
                current_row += col.get_text().replace('(','').replace(')','') + ','

        with open('country_participation_by_year.csv', 'a') as f:
            f.write(current_row[:-1] + '\n')



def get_club_links():
    page = requests.get('https://en.wikipedia.org/wiki/UEFA_Champions_League_clubs_performance_comparison')
    soup = BeautifulSoup(page.content, 'html.parser')

    t = soup.find_all('table')[1]

    links = []

    for row in t.find_all('tr'):
        if 'flagicon' in str(row.find('td').contents[0]) and '(' not in row.find_all('td')[1].get_text():
            links.append("https://en.wikipedia.org" + row.find('td').contents[-2].get('href'))

    return links

def get_player_age(player_link):
    page = requests.get(player_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    for row in soup.find('table').find_all('tr'):
        if 'age' in str(row):
            age = row.find('td').contents[2].get_text()[-3:-1]
    return age

def get_player_dob(player_link):
    page = requests.get(player_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    for row in soup.find('table').find_all('tr'):
        if 'age' in str(row):
            dob = soup.find('table').find_all('tr')[2].find('td').contents[0].get_text()[1:-1]
    dob = soup.find('table').find_all('tr')[2].find('td').contents[0].get_text()[1:-1]
    return dob

def get_current_squad(team_link):
    page = requests.get(team_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    open('players.csv', 'w').close()

    table_num = sorted([(i, len(table.find_all('tr'))) for i, table in enumerate(soup.find_all('table'))], key=lambda x: x[1], reverse=True)[0][0]

    team = soup.find('title').get_text().replace(' - Wikipedia', '')

    table = soup.find_all('table')[table_num]

    for row in table.find_all('tr')[0].find_all('tr'):
        if len(row.find_all('td')) > 0:
            nationality = row.find_all('td')[1].contents[0].contents[0].get('title')
            position = row.find_all('td')[2].contents[0].get_text()
            name = row.find_all('td')[3].contents[0].contents[0].get_text()
            player_link = "https://en.wikipedia.org" + row.find_all('td')[3].contents[0].contents[0].get('href')
            age = get_player_age(player_link)
            dob = get_player_dob(player_link)
            player_line = ','.join([team, name, str(age), dob, nationality, position])

            with open('players.csv', 'a') as f:
                f.write(player_line + '\n')
