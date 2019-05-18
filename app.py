import json

import numpy as np
import pandas as pd
from flask import Flask, render_template, request

from constants import (TERRORISM_DB,
                       PF_RELIGIOUS_FREEDOM, HAPPINESS_DB,
                       MAJ_INT_RELIGIOUS_POPULATION,
                       GROWTH_DATA, POPULATION_BY_RELIGION,
                       HEATMAP_DATA)

app = Flask(__name__)


@app.route("/heat_map_data/<religion>", methods=['POST', 'GET'])
def get_heatmap_data(religion):
    religions = json.loads(request.args.get('religions'))
    df = pd.read_csv(HEATMAP_DATA)
    df = df[df.majority_religion.isin(religions)]
    if religion != 'all':
        if religion in ['shinto', 'noreligion', 'animism', 'judaism']:
            df = df[(df['majority_religion'] == 'shinto') |
                    (df['majority_religion'] == 'noreligion') |
                    (df['majority_religion'] == 'judaism') |
                    (df['majority_religion'] == 'animism')]
        else:
            df = df[df['majority_religion'] == religion]

    df = df.drop('Unnamed: 0', axis=1)
    columns = ['Majority Religion Pop', 'PF Religion', 'PF Expression', 'EF Trade', 'EF Legal',
               'PF Movement', 'PF Law', 'PF Security & Safety', 'PF Associate & Assemble',
               'PF Identity & Relationships', 'EF Money', 'EF Regulation', 'Growth',
               'Happiness Score']

    # data = np.column_stack((np.array(columns).reshape(14, 1), df.corr().values))

    df = df.drop('majority_religion', axis=1)
    df_corr = df.corr().replace(np.nan, 0)
    return json.dumps({'data': df_corr.values.tolist(), 'columns': columns}, indent=2)


@app.route("/growth_data1/<year>", methods=['POST', 'GET'])
def get_growth_data2(year):
    df = pd.read_csv(GROWTH_DATA)
    color = {
        "christianity": "#9f5afd", "noreligion": "#dadfe1", "islam": "#00b16a",
        "animism": "#999900", "hinduism": "#e67e22", "judaism": "#0000FF",
        "syncretism": "#7CFC00", "buddhism": "#96281b", "shinto": "#FF0000"
    }
    df = df[(df.year == int(year))]

    res = []
    for key, tbl in df.groupby('majority_religion'):
        for val in tbl.growth.values:
            res.append({'group': key, 'y': float(val), 'color': color[key], 'label': float(val)})

    return json.dumps(res, indent=2)


@app.route("/growth_data/<year>", methods=['POST', 'GET'])
def get_growth_data(year):
    religions = json.loads(request.args.get('religions'))
    religion_dict = {rel: idx for idx, rel in enumerate(religions)}
    df = pd.read_csv(GROWTH_DATA)
    df = df[(df.year == int(year))]
    df = df[df.majority_religion.isin(religions)]

    res = []
    for key, tbl in df.groupby('majority_religion'):
        for val in tbl.growth.values:
            res.append({'x': float(religion_dict[key]), 'y': float(val)})

    return json.dumps(res, indent=2)


@app.route("/all_religions")
def all_religions():
    religions = json.loads(request.args.get('religions'))
    df = pd.read_csv(PF_RELIGIOUS_FREEDOM)
    df = df[df.religion.isin(religions + ['total_average'])]

    return json.dumps(df.religion.values.tolist(), indent=2)


@app.route("/religious_freedom", methods=['POST', 'GET'])
def get_religious_freedom():
    religions = json.loads(request.args.get('religions'))
    df = pd.read_csv(PF_RELIGIOUS_FREEDOM)
    df = df[df.religion.isin(religions + ['total_average'])]
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
    year_df = year_df.sample(n=643)
    return json.dumps(year_df.values.tolist(), indent=2)


@app.route("/map/<year>", methods=['POST', 'GET'])
def get_religion_by_year(year):
    religions = json.loads(request.args.get('religions'))
    df = pd.read_csv(MAJ_INT_RELIGIOUS_POPULATION)
    df = df[df.majority_religion.isin(religions)]
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
    religions = json.loads(request.args.get('religions'))
    df = pd.read_csv(POPULATION_BY_RELIGION)
    columns = ['year'] + [rel + '_all' for rel in religions] + ["world_population"]
    df = df[columns]

    df.columns = ['year'] + religions + ["world_population"]

    pop_list = list(df.T.to_dict().values())

    res = []
    for row in pop_list:
        for key in df.columns[1:-1]:
            res.append({'series': key, 'year': row['year'], 'count': row[key]})

    return json.dumps(res, indent=2)


@app.route("/population_by_religion/<year>", methods=['POST', 'GET'])
def get_world_population_by_religion(year):
    religions = json.loads(request.args.get('religions'))
    df = pd.read_csv(POPULATION_BY_RELIGION)
    df = df[['year', 'christianity_all', 'judaism_all', 'islam_all', 'buddhism_all', 'hinduism_all', 'shinto_all',
             'syncretism_all', 'animism_all', 'noreligion_all', 'world_population']]
    df.columns = ['year', "christianity", "judaism", "islam", "buddhism", "hinduism", "shinto",
                  "syncretism", "animism", "noreligion", "world_population"]
    df = df[df.year == int(year)].reset_index()
    religions.extend(['year', 'world_population'])
    df = df[religions]
    pop_list = list(df.T.to_dict().values())

    return json.dumps(pop_list[0], indent=2)


@app.route("/religion-growth", methods=['POST', 'GET'])
def religion_growth():
    return render_template("religion-growth1.html")


@app.route("/religion", methods=['POST', 'GET'])
def religion():
    return render_template("religion.html")


@app.route("/happiness", methods=['POST', 'GET'])
def happiness():
    return render_template("happiness.html")


@app.route("/religion_population", methods=['POST', 'GET'])
def stacked_area_chart():
    return render_template("stacked_area_chart.html")


@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


@app.route("/coordinated_view1", methods=['POST', 'GET'])
def coordinated_view1():
    return render_template("coordinated_view1.html")


@app.route("/coordinated_view2", methods=['POST', 'GET'])
def coordinated_view2():
    return render_template("coordinated_view2.html")


@app.route("/heatmap", methods=['POST', 'GET'])
def heatmap():
    return render_template("heatmap.html")


@app.route("/donuts", methods=['POST', 'GET'])
def donut_chart():
    return render_template("donutchart.html")


@app.route("/home", methods=['POST', 'GET'])
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
