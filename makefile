source_files := $(wildcard src/*.py)
bytecodes := $(patsubst %.py,%.mpy,${source_files})

src/%.mpy: src/%.py
	@echo "Precompiling micropython source"
	python -m mpy_cross $? -o $@

upload: $(bytecodes)
	@echo "Uploading to board"
	bash upload.sh

clean:
	rm -f src/*.mpy

all: upload
