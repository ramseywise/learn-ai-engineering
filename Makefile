include ~/.claude/Makefile.common

LIBRARIAN_DIR ?= $(HOME)/workspace/librarian

.PHONY: help lint test unit chapter-check chapter-check-all link-check curriculum crosswalk crosswalk-check drill-check review-findings signals learn papers papers-status papers-route papers-install papers-nightly-install papers-nightly-uninstall slides

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

lint:  ## Verify top-level topic directories exist
	@echo "Checking structure..."; \
	FAIL=0; \
	for d in ai-engineering data-analytics data-engineering data-science generative-ai programming; do \
		if [ ! -d "$$d" ]; then echo "  MISSING: $$d/"; FAIL=1; fi; \
	done; \
	[ $$FAIL -eq 0 ] && echo "  OK (all topic directories present)"

CHAPTER_GATE = ai-engineering/*/ generative-ai/*/ data-analytics/*/ data-science/*/ data-engineering/*/

test:  ## Every repo check. Runs them all, then fails if any failed. Curriculum issues are printed, not gated
	@fail=0; for t in lint link-check crosswalk-check chapter-check-all drill-check unit; do \
		echo "== $$t"; $(MAKE) --no-print-directory $$t || { echo "FAILED: $$t"; fail=1; }; \
	done; \
	echo "== curriculum (information only)"; \
	python3 scripts/curriculum_map.py build >/dev/null && python3 scripts/curriculum_map.py issues | tail -1; \
	exit $$fail

unit:  ## Run the tests for the repo's scripts
	@out=$$(python3 -m unittest discover -s scripts -p 'test_*.py' 2>&1); rc=$$?; echo "$$out" | grep -E '^(Ran |OK|FAILED|FAIL:|ERROR:)'; exit $$rc

chapter-check-all:  ## Hold the five pillared subjects to the chapter standard; programming/ is reported only
	@python3 scripts/check_chapters.py --strict $(CHAPTER_GATE) | tail -1
	@python3 scripts/check_chapters.py --strict $(CHAPTER_GATE) >/dev/null
	@python3 scripts/check_chapters.py programming/*/ | tail -1

chapter-check:  ## Check notes against the chapter standard: make chapter-check PILLAR=data-analytics/06-applied-analyses [STRICT=1]
	@test -n "$(PILLAR)" || { echo "usage: make chapter-check PILLAR=<area>/<pillar> [STRICT=1]"; exit 1; }
	@python3 scripts/check_chapters.py $(PILLAR) $(if $(STRICT),--strict)

link-check:  ## Verify relative links in markdown files exist on disk
	@python3 scripts/link_check.py

curriculum:  ## Rebuild the curriculum map and print integration issues: make curriculum [PILLAR=data-science/01-classical-ml]
	@python3 scripts/curriculum_map.py build
	@python3 scripts/curriculum_map.py issues $(if $(PILLAR),--pillar $(PILLAR))

crosswalk:  ## Validate practice/ and programming/drills/ units and links, then regenerate practice/CROSSWALK.md
	@python3 scripts/practice/crosswalk.py

crosswalk-check:  ## Validate practice/ and programming/drills/ units and links; fail if practice/CROSSWALK.md is stale
	@python3 scripts/practice/crosswalk.py --check

drill-check:  ## Check drill schema, that Python parses and that SQL seeds load: make drill-check [DRILL_PATH=programming/drills/sql]
	@python3 scripts/practice/check_drills.py $(DRILL_PATH)

review-findings:  ## Reviewer precision, open decisions and recurring faults from the findings log
	@python3 scripts/review/findings.py report

signals:  ## Weekly review signals (reviewer log, flashcards, drills, wiki searches): make signals [WRITE=1]
	@python3 scripts/review/signals.py $(if $(WRITE),--write)

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

papers:  ## Fetch new AI Papers of the Week, scan repo PDFs, triage, download into home sources/
	@python3 scripts/papers/potw.py run

papers-status:  ## Paper ledger counts by status
	@python3 scripts/papers/potw.py status

papers-route:  ## Move triaged PDFs from the scripts/papers/inbox/ to their home's sources/ [APPLY=1]
	@python3 scripts/papers/potw.py route $(if $(APPLY),--apply)

papers-install:  ## Install the weekly launchd job (Monday 11:00)
	@cp scripts/papers/com.wiseer.potw.plist ~/Library/LaunchAgents/
	@launchctl bootout gui/$$(id -u)/com.wiseer.potw 2>/dev/null || true
	@launchctl bootstrap gui/$$(id -u) ~/Library/LaunchAgents/com.wiseer.potw.plist
	@echo "Installed com.wiseer.potw — log: .claude/logs/potw.log"

papers-nightly-install:  ## Install the nightly /papers integration job (daily 02:30)
	@mkdir -p .claude/logs
	@cp scripts/papers/com.wiseer.papers-nightly.plist ~/Library/LaunchAgents/
	@launchctl bootout gui/$$(id -u)/com.wiseer.papers-nightly 2>/dev/null || true
	@launchctl bootstrap gui/$$(id -u) ~/Library/LaunchAgents/com.wiseer.papers-nightly.plist
	@echo "Installed com.wiseer.papers-nightly — log: .claude/logs/papers-nightly.log"

papers-nightly-uninstall:  ## Remove the nightly /papers job
	@launchctl bootout gui/$$(id -u)/com.wiseer.papers-nightly 2>/dev/null || true
	@rm -f ~/Library/LaunchAgents/com.wiseer.papers-nightly.plist
	@echo "Removed com.wiseer.papers-nightly"

# PILLAR is a dir under ai-engineering/ (01-prompt-engineering) or a path (generative-ai/02-rag-retrieval)
SLIDES_DIR = $(if $(findstring /,$(PILLAR)),$(PILLAR),ai-engineering/$(PILLAR))

slides:  ## Build a deck: make slides PILLAR=01-prompt-engineering|data-analytics/02-probability-and-statistics|programming/python/01-foundations [PREVIEW=1] [PDF=1] [STRICT=1]
	@test -n "$(PILLAR)" || { echo "usage: make slides PILLAR=<pillar-dir> [PREVIEW=1] [PDF=1] [STRICT=1]"; exit 1; }
	@uv run -q --with python-pptx --with pyyaml --with pillow --with resvg-py python scripts/slides/build_deck.py \
		$(SLIDES_DIR)/slides/deck.yaml \
		$(if $(PREVIEW),--preview $(SLIDES_DIR)/slides/.preview) $(if $(PDF),--pdf) $(if $(STRICT),--strict)
