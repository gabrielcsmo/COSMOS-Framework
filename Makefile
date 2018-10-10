corsika_run:
	./main.py --config configs/corsika-config.json
run:
	./main.py --config configs/config-example.json
clean:
	-rm -rf *.log *.pyc output
