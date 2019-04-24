from flask import Flask, render_template
from constants import MAJORITY_POP_FILE

import pandas as pd
import json

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def index():
    df = pd.read_csv(MAJORITY_POP_FILE)
    data = {'data'   : json.dumps(df.values.tolist(), indent=2)}

    return render_template("index.html",
                           data=data)


if __name__ == "__main__":
    app.run(debug=True)
