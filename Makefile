.PHONY: install data test report incidents verify
install:
	pip install -r requirements.txt --break-system-packages
data:
	python3 scripts/fetch_data.py
	python3 scripts/gen_synthetic.py
test:
	python3 -m pytest -q
report:
	python3 -m fiberlens
incidents:
	python3 scripts/incidents.py
verify:
	python3 scripts/verify_incidents.py
