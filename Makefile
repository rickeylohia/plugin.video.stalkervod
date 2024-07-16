export KODI_PROFILE = $(CURDIR)/tests/userdata
export CURR_PROJECT_DIR = `basename $(CURDIR)`
name = $(shell xmllint --xpath 'string(/addon/@id)' addon.xml)
version = $(shell xmllint --xpath 'string(/addon/@version)' addon.xml)
zip_name = $(name)-$(version).zip
PYTHON = python
include_files = addon.xml LICENSE README.md *.py resources lib
build_dir = build

check: check-pylint

check-pylint: clean
	@echo "Running pylint"
	$(PYTHON) -m pylint *.py lib/ tests/

test: check
	@echo "Running tests"
	@mkdir $(KODI_PROFILE)/addon_data
	@mkdir $(KODI_PROFILE)/addon_data/$(CURR_PROJECT_DIR)
	@cp $(KODI_PROFILE)/settings.xml $(KODI_PROFILE)/addon_data/$(CURR_PROJECT_DIR)
	@mkdir test-results
	coverage run -m pytest -v tests --junitxml=test-results/junit.xml
	@coverage xml

build: test
	@echo "Building new package"
	@rm -rf $(build_dir)
	@rm -rf resources/tokens
	@find . -name '*.py[cod]' -type f -delete
	@find . -name '__pycache__' -type d -delete
	@mkdir -p $(build_dir)/$(name)
	@cp -r $(include_files) ./build/$(name)
	@cd $(build_dir); zip -r $(zip_name) $(name)/
	@rm -rf $(build_dir)/$(name)
	@echo "Successfully wrote package as: $(CURR_PROJECT_DIR)/$(build_dir)/$(zip_name)"

clean:
	@echo "Cleaning up"
	@find . -name '*.py[cod]' -type f -delete
	@find . -name '__pycache__' -type d -delete
	@rm -rf .pytest_cache build resources/tokens htmlcov test-results tests/userdata/addon_data
	@rm -f .coverage coverage.xml
