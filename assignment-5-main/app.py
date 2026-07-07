"""Flask application for receiving and displaying air quality measurements"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database import Database


app = Flask(__name__)
CORS(app)
db = Database()


@app.route('/')
def index():
    """Render front page with latest, minimum, and maximum measurements"""
    latest = db.get_latest()
    min_max = db.get_min_max()

    if latest is None:
        return render_template('front.html',
                               latest=None,
                               min_vals=None,
                               max_vals=None)

    min_vals = {
        'co2': min_max['min_co2'],
        'co2_timestamp': min_max['min_co2_timestamp'],
        'tvoc': min_max['min_tvoc'],
        'tvoc_timestamp': min_max['min_tvoc_timestamp']
    }
    max_vals = {
        'co2': min_max['max_co2'],
        'co2_timestamp': min_max['max_co2_timestamp'],
        'tvoc': min_max['max_tvoc'],
        'tvoc_timestamp': min_max['max_tvoc_timestamp']
    }

    return render_template('front.html',
                           latest=dict(latest),
                           min_vals=min_vals,
                           max_vals=max_vals)


@app.route('/measurements')
def measurements():
    """Render the measurements page with paginated records"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    rows, total = db.get_page(page, per_page)
    total_pages = (total + per_page - 1) // per_page
    return render_template('measurements.html',
                           measurements=rows,
                           page=page,
                           total_pages=total_pages)


@app.route('/data', methods=['POST'])
def receive_data():
    """Receive CO2 and TVOC measurements via POST from the M5Stack device."""
    data = request.get_json()

    if not data:
        return jsonify({'status': 'No data received'}), 400

    try:
        co2 = float(data['co2'])
        tvoc = float(data['tvoc'])
    except (KeyError, ValueError, TypeError):
        return jsonify({'status': 'Invalid data'}), 400

    db.insert(co2, tvoc)
    return jsonify({'status': 'Data inserted'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)