.PHONY: help status push quick-pr ship link-check

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

status:  ## Show branch, unpushed commits, staged changes, open PRs
	@echo "=== learn-ai-engineering ==="
	@echo "Branch: $$(git branch --show-current)"
	@echo "Unpushed:"
	@git log origin/$$(git branch --show-current)..HEAD --oneline 2>/dev/null || echo "  (no remote tracking)"
	@echo "Staged:"
	@git diff --cached --stat 2>/dev/null || true
	@echo "Modified:"
	@git diff --stat 2>/dev/null || true
	@echo "Open PRs:"
	@gh pr list --state open --json number,title,headBranch --jq '.[] | "#\(.number) \(.title) [\(.headBranch)]"' 2>/dev/null || echo "  (none)"

push:  ## Push current branch to origin
	git push -u origin $$(git branch --show-current)

quick-pr:  ## Create PR from current branch with auto-generated body
	@BRANCH=$$(git branch --show-current); \
	COMMITS=$$(git log origin/main..HEAD --oneline 2>/dev/null); \
	if [ "$$BRANCH" = "main" ]; then echo "Error: can't PR from main"; exit 1; fi; \
	EXISTING=$$(gh pr list --head "$$BRANCH" --json number --jq '.[0].number' 2>/dev/null); \
	if [ -n "$$EXISTING" ]; then echo "PR #$$EXISTING already exists for $$BRANCH"; exit 0; fi; \
	ISSUES=$$(echo "$$COMMITS" | grep -oE '#[0-9]+' | sort -u | tr '\n' ' '); \
	BODY=$$(printf "## Summary\n%s\n\n## Issues\n%s\n\nCloses %s\n" "$$COMMITS" "$$ISSUES" "$$ISSUES"); \
	echo "Creating PR for $$BRANCH (issues: $$ISSUES)..."; \
	gh pr create --title "$$BRANCH" --body "$$BODY"

ship: push quick-pr  ## Push + create PR in one step

link-check:  ## Verify relative links in markdown files exist on disk
	@ERRORS=0; \
	for f in $$(find . -name '*.md' -not -path './.git/*' -not -path './node_modules/*'); do \
		dir=$$(dirname "$$f"); \
		for link in $$(grep -oE '\[([^]]*)\]\(([^)#]+)\)' "$$f" 2>/dev/null | grep -v 'http' | sed 's/.*](\(.*\))/\1/'); do \
			target="$$dir/$$link"; \
			target=$$(echo "$$target" | sed 's/%20/ /g'); \
			if [ ! -e "$$target" ]; then \
				echo "BROKEN: $$f -> $$link"; \
				ERRORS=$$((ERRORS+1)); \
			fi; \
		done; \
	done; \
	if [ $$ERRORS -eq 0 ]; then echo "All links OK"; else echo "$$ERRORS broken links found"; fi
