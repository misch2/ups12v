PYTHON ?= python
VERSION ?=
export FIRMWARE_RELEASE_VERSION := $(value VERSION)

.DEFAULT_GOAL := help
.PHONY: help publish mark-latest

help:
	@echo make publish                       Push the firmware tag for the committed HEAD
	@echo make mark-latest VERSION=20261125.12   Mark that published firmware release as Latest

publish:
	"$(PYTHON)" software/ups/tools/firmware_release_commands.py publish

mark-latest:
	"$(PYTHON)" software/ups/tools/firmware_release_commands.py mark-latest
