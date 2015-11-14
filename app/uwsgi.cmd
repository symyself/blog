uwsgi --socket 127.0.0.1:3031 --wsgi-file first_flask.py --callable app --processes 4 --threads 2 
