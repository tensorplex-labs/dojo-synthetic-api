PRECOMMIT_VERSION="3.7.1"

.PHONY: hooks

hooks:
	if ! command -v pre-commit >/dev/null 2>&1; then \
		echo "Install pre-commit first"; \
		exit 1; \
	fi
	pre-commit clean
	pre-commit uninstall --hook-type pre-commit --hook-type pre-push
	pre-commit gc
	pre-commit install --hook-type pre-commit --hook-type pre-push
