import json

import pandas as pd
from flask import Flask, render_template

from constants import MAJORITY_RELIGIOUS_POPULATION_DB, TERRORISM_DB, PF_RELIGIOUS_FREEDOM

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


@app.route("/religion", methods=['POST', 'GET'])
def religion():
    return render_template("religion.html")


@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
