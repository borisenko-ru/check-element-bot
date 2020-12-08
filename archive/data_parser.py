import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

"""Collect data from a website

Create function for website parsing of chemical elements basic information.
"""


def elements():
    url = 'https://images-of-elements.com/element-properties.php'
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    table = soup.find_all('table')[1]
    rows = table.find_all('tr')
    field_list = []

    for i in range(12):
        col = []
        # add header
        col.append(rows[0].find_all('th')[i].get_text().strip())
        # start with second row as first one was taken earlier
        for row in rows[1:]:
            try:
                # find all tags td in a row
                r = row.find_all('td')
                # save data to a list
                col.append(r[i].get_text().strip())
            except:
                pass
        field_list.append(col)
    d = dict()
    for i in range(12):
        d[field_list[i][0]] = field_list[i][1:]
    df = pd.DataFrame(d)
    df = df.rename(columns={'Valence el.': 'Valence',
                            'Stable isotopes': 'StableIsotopes',
                            'Melting point': 'MeltingPoint',
                            'Boiling point': 'BoilingPoint'})
    df = df.replace('', np.nan)

    radius_note = 'Unknown'
    valence_note = 'This number is meaningless \
                    and therefore omitted'
    melting_point_note = 'Unknown, helium has no solid state, \
                         arsenic has no liquid state'
    stable_isotopes_note = 'Does not have any stable nuclides'
    boiling_point_note = 'Unknown'
    density_note = 'Unknown'
    df['Radius'].fillna(radius_note, inplace=True)
    df['Valence'].fillna(valence_note, inplace=True)
    df['MeltingPoint'].fillna(melting_point_note, inplace=True)
    df['StableIsotopes'].fillna(stable_isotopes_note, inplace=True)
    df['BoilingPoint'].fillna(boiling_point_note, inplace=True)
    df['Density'].fillna(density_note, inplace=True)

    return df
