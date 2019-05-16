import json

import pandas as pd
from flask import Flask, render_template

from constants import (TERRORISM_DB,
                       PF_RELIGIOUS_FREEDOM, HAPPINESS_DB,
                       MAJ_INT_RELIGIOUS_POPULATION,
                       GROWTH_DATA, POPULATION_BY_RELIGION)

app = Flask(__name__)


@app.route("/growth_data/<year>", methods=['POST', 'GET'])
def get_growth_data(year):
    df = pd.read_csv(GROWTH_DATA)
    rel_df = pd.read_csv(PF_RELIGIOUS_FREEDOM)
    religions = rel_df.religion.values.tolist()[:-1]
    religion_dict = {rel: idx for idx, rel in enumerate(religions)}
    df = df[(df.year == int(year))]

    res = []
    for key, tbl in df.groupby('majority_religion'):
        for val in tbl.growth.values:
            res.append({'x': float(religion_dict[key]), 'y': float(val)})

    return json.dumps(res, indent=2)


@app.route("/all_religions")
def all_religions():
    df = pd.read_csv(PF_RELIGIOUS_FREEDOM)

    return json.dumps(df.religion.values.tolist(), indent=2)


@app.route("/religious_freedom", methods=['POST', 'GET'])
def get_religious_freedom():
    df = pd.read_csv(PF_RELIGIOUS_FREEDOM)
    res = list()

    for val in df.values:
        res.append({'religion': val[1], 'pf_religion': val[2], 'pf_religion_estop': val[3],
                    'pf_religion_harrasment': val[4], 'pf_religion_restrictions': val[5]})

    return json.dumps(res, indent=2)


@app.route("/terror_attacks/<year>", methods=['POST', 'GET'])
def get_past_5_years_attacks(year):
    df = pd.read_csv(TERRORISM_DB)
    year_df = df[((df.iyear > int(year) - 5) & (df.iyear <= int(year)))].reset_index()
    year_df = year_df[['country_txt', 'latitude', 'longitude']]
    year_df = year_df[year_df['latitude'].notnull()]
    # TODO: Adaptive sampling by country
    year_df = year_df.sample(n=500)
    return json.dumps(year_df.values.tolist(), indent=2)


@app.route("/map/<year>", methods=['POST', 'GET'])
def get_religion_by_year(year):
    df = pd.read_csv(MAJ_INT_RELIGIOUS_POPULATION)
    year_df = df[df.year == int(year)].reset_index()
    year_df = year_df[['state', 'majority_religion', 'majority_population']]
    return json.dumps(year_df.values.tolist(), indent=2)


@app.route("/happiness_score/<year>", methods=['POST', 'GET'])
def get_happiness_score(year):  # making it generic for now
    df = pd.read_csv(HAPPINESS_DB)
    df = df[['Country', 'Happiness Score']]
    df = df.round(3)
    # TODO: Adaptive sampling by country
    return json.dumps(df.values.tolist(), indent=2)


@app.route("/population_by_religion_dict/", methods=['POST', 'GET'])
def get_world_population_by_religion_dict():
    df = pd.read_csv(POPULATION_BY_RELIGION)
    df = df[['year', 'christianity_all', 'judaism_all', 'islam_all',
             'buddhism_all', 'hinduism_all', 'shinto_all',
             'syncretism_all', 'animism_all', 'noreligion_all', 'world_population']]

    df.columns = ['year', "christianity", "judaism", "islam", "buddhism", "hinduism", "shinto",
                  "syncretism", "animism", "noreligion", "world_population"]

    pop_list = list(df.T.to_dict().values())

    res = []
    for row in pop_list:
        print(row)
        for key in df.columns[1:-1]:
            res.append({'series': key, 'year': row['year'], 'count': row[key]})

    # TODO: Adaptive sampling by country
    return json.dumps(res, indent=2)


@app.route("/population_by_religion/", methods=['POST', 'GET'])
def get_world_population_by_religion():
    df = pd.read_csv(POPULATION_BY_RELIGION)
    df = df[['year', 'christianity_all', 'judaism_all', 'islam_all', 'buddhism_all', 'hinduism_all', 'shinto_all',
             'syncretism_all', 'animism_all', 'noreligion_all', 'world_population']]

    # TODO: Adaptive sampling by country
    return json.dumps(df.values.tolist(), indent=2)


@app.route("/religion-growth", methods=['POST', 'GET'])
def religion_growth():
    return render_template("religion-growth.html")


@app.route("/religion", methods=['POST', 'GET'])
def religion():
    return render_template("religion.html")


@app.route("/happiness", methods=['POST', 'GET'])
def happiness():
    return render_template("happiness.html")


@app.route("/religion_population", methods=['POST', 'GET'])
def streamgraph():
    return render_template("streamgraph.html")


@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


# @app.route("/", methods=['POST', 'GET'])
# def index():
#     return render_template("temp.html")


if __name__ == "__main__":
    app.run(debug=True)
