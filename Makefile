install:
	pip3 install -r requirements.txt --target src/lib

release: install
	$(eval VERSION := $(shell defaults read $(PWD)/src/info.plist version))
	cd src && zip -r ../fakeum-v$(VERSION).alfredworkflow . \
		--exclude "*.pyc" --exclude "*__pycache__*" --exclude "*.dist-info*"
