Running the Wafflehaus tests
----------------------------

You will want both an installation of Python 2.6 and 2.7 
to run all configured tests

1. Fork the repo and clone your fork:
	git clone <repository link>

2. Navigate to the new repo:
	cd wafflehaus

3. Install virtualenv if you don't have it already:
	pip install virtualenv

4. Create a virtual environment in the .venv folder at the root of the repo:
	virtualenv --no-site-packages --distribute .venv --prompt="(WafflehausEnv)"

5. Activate the virtual environment:
	source .venv/bin/activate

6. Install tox in the newly activated virtual environment:
	pip install tox

7. Now simply run the tox command:
	Note: this may take a bit of time the first time you execute it

	tox

	Note: subsequent runs of tox should be much faster

8. Exit out of the context of the virtual environment when you are finished:
	deactivate


Note: For subsequent test runs, simply have the virtual environment activated
and run the tox command from within the repo




