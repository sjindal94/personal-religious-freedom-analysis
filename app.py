import json

import pandas as pd
from flask import Flask, render_template

from constants import MAJORITY_RELIGIOUS_POPULATION_DB, TERRORISM_DB, PF_RELIGIOUS_FREEDOM, HAPPINESS_DB

app = Flask(__name__)


@app.route("/all_religions", methods=['POST', 'GET'])
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
    df = pd.read_csv(MAJORITY_RELIGIOUS_POPULATION_DB)
    year_df = df[df.year == int(year)].reset_index()
    year_df = year_df[['state', 'majority_religion', 'majority_population']]
    return json.dumps(year_df.values.tolist(), indent=2)


@app.route("/map/interpolated/<year>", methods=['POST', 'GET'])
def get_interpolated_religion_by_year(year):
    year = 2010
    df = pd.read_csv(MAJORITY_RELIGIOUS_POPULATION_DB)
    # TODO: Interpolate here
    # print(df.iloc[:10])
    # df['year'] = pd.to_datetime(df['year']).dt.strftime('%Y')
    # idx = pd.date_range('09-01-1945', '09-30-2017', freq='5A')
    # idx = idx.strftime('%Y')
    # print(idx)
    # df = df.groupby(['year'], as_index=True).apply(
    #     lambda x: x.reindex(idx,
    #                         method='nearest')).reset_index(level=0, drop=True).sort_index()
    # # for i in df['state']:
    # #     df = df.append({'A': i}, ignore_index=True)
    # print(df.iloc[:10])
    df['majority_population'] = df.groupby(['state', 'majority_religion'])['majority_population'].apply(
        lambda x: x.interpolate(method="spline", order=1, limit_direction="both"))
    year_df = df[df.year == int(year)].reset_index()
    year_df = year_df[['state', 'majority_religion', 'majority_population']]
    return json.dumps(year_df.values.tolist(), indent=2)


@app.route("/happiness_score/<year>", methods=['POST', 'GET'])
def get_happiness_score(year):
    df = pd.read_csv(HAPPINESS_DB)
    df = df[['Country', 'Happiness Score']]
    df = df.round(3)
    # TODO: Adaptive sampling by country
    return json.dumps(df.values.tolist(), indent=2)


@app.route("/religion", methods=['POST', 'GET'])
def religion():
    return render_template("religion.html")


@app.route("/happiness", methods=['POST', 'GET'])
def happiness():
    return render_template("happiness.html")


@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
