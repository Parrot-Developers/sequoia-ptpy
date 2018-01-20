install:
	python setup.py install

test:
	python setup.py test

distribute:
	python setup.py sdist upload --identity="26B1FA94" --sign
  workon ptpy
	python setup.py bdist_wheel upload --identity="26B1FA94" --sign
  workon ptpy3
	python setup.py bdist_wheel upload --identity="26B1FA94" --sign
