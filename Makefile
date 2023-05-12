venv-setup:
	python -m venv venv

venv-activate-unix:
	source venv/bin/activate

venv-activate-windows:
	venv\Scripts\activate.bat

venv-deactivate-unix:
	deactivate

venv-deactivate-windows:
	deactivate.bat

install:
	pip install -r requirements.txt

update-pip:
	pip install --user --upgrade pip && python -m pip install --upgrade pip

start:
	uvicorn src.main:app --reload

lint:
	flake8 src

freeze:
	pip freeze > requirements.txt

migrate:
	alembic upgrade head
