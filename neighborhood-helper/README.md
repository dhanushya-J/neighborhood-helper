# Neighborhood Helper

A local services platform that helps residents connect with nearby service providers.

## About

Neighborhood Helper is a college project built with Flask and MySQL. Residents can find service providers, request bookings, and follow booking progress. Providers can manage requests and update job status.

## Features

- Search for local service providers by service and location
- View provider profiles and ratings
- Create and track service bookings
- Provider workflow for accepting requests and updating job progress
- Simulated payment and review flow
- Separate areas for residents, providers, and administrators

## Built with

- Python and Flask
- MySQL and PyMySQL
- HTML, CSS, and JavaScript

## Requirements

- Python 3.10 or later
- MySQL Server running locally on port `3306`

## Run locally on Windows

The application files are inside the `neighborhood-helper` folder in this repository. Open a terminal at the repository folder, then run:

```bash
cd neighborhood-helper
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
Set the MySQL connection details in the same terminal. Replace the password placeholder with your local MySQL root password. Do not commit your password to GitHub.
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD='REPLACE_WITH_YOUR_LOCAL_MYSQL_PASSWORD'
export MYSQL_DB=neighborhood_helper
If your local MySQL account has no password, use export MYSQL_PASSWORD=''.

## Initialize the database and start the app:
python init_db.py
python app.py
Open http://127.0.0.1:5000 in your browser. Keep the terminal open while using the app. Press Ctrl+C in the terminal to stop it.
python init_db.py --force rebuilds the database and reloads its seed data. Use it only if you intend to reset the project database.

## Project structure
neighborhood-helper/
├── app.py
├── config.py
├── requirements.txt
├── init_db.py
├── database/
├── routes/
├── static/
├── templates/
└── utils/
## Security
- Never commit database passwords, API keys, or private user information.
- This project is for learning and demonstration. Payment options are simulated; no real payment is processed.
