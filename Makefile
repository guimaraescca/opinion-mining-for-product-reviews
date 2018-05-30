.PHONY: clean help

.DEFAULT: help

help:
	@echo "clean"
	@echo "	Remove temporary data stored at data/interim"

clean:
	rm data/interim/liwc-object.pickle
