from flask import app


def run_flask():

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

