from flask import Flask, render_template
from constants import MAJORITY_POP_BY_YEAR, TERRORISM_DB

import pandas as pd
import json

app = Flask(__name__)


@app.route("/terror_attacks/<year>", methods=['POST', 'GET'])
def get_past_5_years_attacks(year):
    df = pd.read_csv(TERRORISM_DB)
    year_df = df[((df.iyear > int(year) - 5) & (df.iyear <= int(year)))].reset_index()

    return json.dumps(year_df.values.tolist(), indent=2)


@app.route("/map/<year>", methods=['POST', 'GET'])
def get_religion_by_year(year):
    df = pd.read_csv(MAJORITY_POP_BY_YEAR)
    year_df = df[df.year == int(year)].reset_index()

    return json.dumps(year_df.values.tolist(), indent=2)


@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
