include ~/.claude/Makefile.common

LIBRARIAN_DIR ?= $(HOME)/workspace/librarian

.PHONY: help lint test link-check learn

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

learn:  ## Process arXiv paper queue in librarian and surface top picks (cd librarian, then /learn)
	@echo "Switch to the librarian repo and run /learn to process the arXiv queue."
	@echo ""
	@echo "  cd $(LIBRARIAN_DIR)"
	@echo "  /learn                    # process all queued papers"
	@echo "  /learn RL alignment       # filter to RL/alignment topics"
	@echo ""
	@echo "To fetch fresh papers first:"
	@echo "  ARXIV_FETCH_ENABLED=true uv run cartographer --cron"
	@echo "  (run from $(LIBRARIAN_DIR))"
