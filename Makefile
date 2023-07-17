# ====================================================================================
# Setup Project
ROOT := $(shell pwd)
PROJECT_FOLDER := $(ROOT)/src
BUILD_TOOLS_FOLDER := $(ROOT)/build-tools
TECHNOLOGY := python

include $(BUILD_TOOLS_FOLDER)/common.mk
include $(BUILD_TOOLS_FOLDER)/common_linters.mk
include $(BUILD_TOOLS_FOLDER)/$(TECHNOLOGY)/python.mk
include $(BUILD_TOOLS_FOLDER)/git.mk
include $(BUILD_TOOLS_FOLDER)/image/docker.mk

AUTOGENERATED_FILE_REGEX := .*/(docs|htmlcov)/.* # This exclude these folder from the linter

# ====================================================================================
# Actions

.PHONY: all
all: update fmt lint coverage

.PHONY: test
test: test.local

.PHONY: test.local
test.local:
	export FROM_ROOT=true && $(MAKE) py.test

.PHONY: build
build: py.build

.PHONY: init
init: py.init git.hooks.setup

.PHONY: update
update: py.update git.submodules

.PHONY: coverage
coverage:
	export FROM_ROOT=true && $(MAKE) py.coverage

.PHONY: docs
docs: py.docs

.PHONY: fmt
fmt: py.fmt

.PHONY: lint
lint: lint.checkmake lint.superlinter

.PHONY: clean
clean: py.clean lint.clean