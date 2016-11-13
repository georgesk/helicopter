all: install

install:
	sudo chown :www-data .
	sudo chmod 2775 .
	sudo setfacl -m u:www-data:rw ./db.sqlite3
	python3 manage.py compilemessages
	python3 manage.py collectstatic --noinput
clean:
	find . -name "*~" | xargs rm -f
	find . -name __pycache__ | xargs rm -rf

.PHONY : all install clean


