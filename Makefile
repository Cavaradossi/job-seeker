.PHONY: help init build convert fidelity apply-dryrun test clean sync

PY ?= python

help: ## Show available targets
	@echo "job-seeker make targets:"
	@echo "  make init          scaffold LaTeX_Resume_CN/EN + experience bank + smoke compile"
	@echo "  make build         compile all resume variants (build_resumes.sh)"
	@echo "  make convert       example md->pdf (override IN= and OUT=)"
	@echo "  make fidelity      print the 4x4 format fidelity matrix"
	@echo "  make apply-dryrun  JD -> variant recommendation, no browser (override URL=)"
	@echo "  make test          run pytest"
	@echo "  make sync          re-sync .cursor/.codex/.workbuddy skill mirrors from docs/skill/job-seeker/"
	@echo "  make clean         remove build artifacts"

init: ## Scaffold private resume dirs + experience bank + smoke compile
	$(PY) -m job_seeker init

build: ## Compile all resume variants
	./build_resumes.sh

IN ?= resume_template/sample-resume-en_US-zh_CN.tex
OUT ?= outputs/sample.pdf
convert: ## Convert one file (override IN= and OUT=)
	$(PY) -m convert --input $(IN) --output $(OUT)

fidelity: ## Print the 4x4 format fidelity matrix
	$(PY) -m convert --fidelity-matrix

URL ?= https://example.com/jobs/1
apply-dryrun: ## JD -> variant recommendation, no browser (override URL=)
	$(PY) -m apply --dry-run --url $(URL)

test: ## Run the test suite
	$(PY) -m pytest -q

sync: ## Re-sync skill mirrors from the canonical source (run after any SKILL.md edit)
	./scripts/sync_skills.sh

clean: ## Remove build artifacts (PDFs/DOCX in outputs/, LaTeX aux)
	rm -f outputs/*.pdf outputs/*.docx
	rm -f resume_template/*.aux resume_template/*.log resume_template/*.out
	rm -f LaTeX_Resume_*/*.aux LaTeX_Resume_*/*.log LaTeX_Resume_*/*.out
