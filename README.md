## List of changes inside repo

# 1. ERD
 It represented in already generated `ERD.png` file or `db.vuerd.json` file for further implemnetation. See details about `db.vuerd.json` in next [repo](https://github.com/vuerd/vuerd-vscode)

# 2. Test system
 All tests are written with pytest core and factoryboy factories and allocated inside `tests/` dicrectory. They use [pytest-flask-sqlalchemy](https://github.com/jeancochrane/pytest-flask-sqlalchemy) with its transactional behavior, [pytest-factoryboy](https://github.com/pytest-dev/pytest-factoryboy) with its fixture factory support, and [pytest-cov](https://github.com/pytest-dev/pytest-cov) with [pytest-spec](https://github.com/pchomik/pytest-spec) for `tox.ini` configuration.

 # 3. Configuration changes
 Flask configurations has been extended with Production, Testing and Development configuration classes. SQLite for testing runs in RAM. SQLite for development now have fixed Flask-Migration support.