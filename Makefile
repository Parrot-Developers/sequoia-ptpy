install:
	python setup.py install

test:
	python setup.py test

distribute:
	python setup.py sdist bdist_wheel upload --identity="26B1FA94" --sign
