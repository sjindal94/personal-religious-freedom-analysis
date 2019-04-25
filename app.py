from flask import Flask, render_template
from constants import MAJORITY_POP_BY_YEAR

import pandas as pd
import json

app = Flask(__name__)


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
