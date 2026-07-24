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
	@ERRORS=0; \
	for f in $$(find . -name '*.md' -not -path './.git/*' -not -path './node_modules/*' -not -path '*/Context-Engineering-main/*'); do \
		dir=$$(dirname "$$f"); \
		for link in $$(grep -oE '\[([^]]*)\]\(([^)#]+)\)' "$$f" 2>/dev/null | grep -v 'http' | sed 's/.*](\(.*\))/\1/'); do \
			case "$$link" in \
				/oss/*|/use-these-docs*|/langsmith/*) continue ;; \
			esac; \
			target="$$dir/$$link"; \
			target=$$(echo "$$target" | sed 's/%20/ /g'); \
			if [ ! -e "$$target" ]; then \
				echo "BROKEN: $$f -> $$link"; \
				ERRORS=$$((ERRORS+1)); \
			fi; \
		done; \
	done; \
	if [ $$ERRORS -eq 0 ]; then echo "All links OK"; else echo "$$ERRORS broken links found"; fi
