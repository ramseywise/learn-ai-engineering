include ~/.claude/Makefile.common

.PHONY: help lint test link-check

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

lint:  ## Verify top-level topic directories exist
	@echo "Checking structure..."; \
	FAIL=0; \
	for d in ai-engineering data-analytics data-engineering data-science generative-ai programming; do \
		if [ ! -d "$$d" ]; then echo "  MISSING: $$d/"; FAIL=1; fi; \
	done; \
	[ $$FAIL -eq 0 ] && echo "  OK (all topic directories present)"

test: lint link-check  ## Structure check + link verification

link-check:  ## Verify relative links in markdown files exist on disk
	@python3 scripts/link_check.py
