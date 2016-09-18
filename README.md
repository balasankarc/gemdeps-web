# Gemdeps Web Service

Gemdeps is a Python library ot find out the packaging status of dependency
chain of a Ruby (on Rails) app, based on its Gemfile/gemspec. Gemdeps Web
Service is a web frontend for Gemdeps that enables users to generate packaging
status bars using a Web UX. It uses Django/Python/Celery/SQLite3 in backend and
Twitter Bootstrap in Frontend.

## Installation
 1. Clone the repository and cd to it - `git clone https://gitlab.com/balasankarc/gemdeps-web && cd gemdeps-web`
 2. Install necessary libraries (Using virtualenv is recommended) - `pip install -r requirements.txt`

## Copyright and License
Gemdeps Web Service is released under [GNU AGPL-3.0+](https://www.gnu.org/licenses/agpl.txt)

Copyright: 2016 Balasankar C \<balasankarc@autistici.org\>
