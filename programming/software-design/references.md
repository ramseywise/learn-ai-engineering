---
origin: curated
sources:
  - https://abseil.io/resources/swe-book
  - https://google.github.io/eng-practices/review/
  - https://martinfowler.com/
confidence: high
cleaned: 2026-11-02
---
# References: software design

Every row here was read for this track, and the "Read" column says how much. "Parts" means the sections a chapter relies on, not the whole work. Don't take a row as a claim about anything beyond those parts. Links were checked on 2026-11-02; the three ACM DOIs refused automated requests, so those weren't confirmed that way.

## Books not accessed

These are the standard books on the subject. They weren't available to read, so no chapter cites their contents. Where a chapter mentions them, it relies on the author's own free writing listed below.

| Book | Instead, this track read | Would add |
|---|---|---|
| Martin Fowler, *Refactoring*, 2nd ed. | His bliki and the online catalogue sketches | The full catalogue of moves with mechanics |
| John Ousterhout, *A Philosophy of Software Design* | The debate with Martin, and his [Stanford page](https://web.stanford.edu/~ouster/cgi-bin/aposd.php) | The full argument on deep modules and complexity |
| Gamma, Helm, Johnson, Vlissides, *Design Patterns* | Rhodes's guide, and Norvig's slides | The original pattern descriptions |

## Books and long works read online

| Source | Read | Maps to |
|---|---|---|
| Winters, Manshreck, Wright (eds.), [*Software Engineering at Google*](https://abseil.io/resources/swe-book), free edition | Ch 9 flow, approvals, benefits, best practices. Ch 11 sizes, scope, flakes, pyramid, coverage. Ch 12 brittle tests, public APIs, behaviours. Ch 13 fidelity, doubles, state vs interaction. Ch 14 fidelity, why larger tests | 05, 07 |
| Chacon and Straub, [*Pro Git*](https://git-scm.com/book/en/v2) | [Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) and [Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing), the perils section; [Debugging with Git](https://git-scm.com/book/en/v2/Git-Tools-Debugging-with-Git), blame only | 07 |
| Beyer et al., [*Site Reliability Engineering*, ch 12](https://sre.google/sre-book/effective-troubleshooting/), written by Chris Jones | Theory, common pitfalls, triage, examine, simplify, what touched it last | 06 |
| Brandon Rhodes, [Python Design Patterns](https://python-patterns.guide/) | Composition Over Inheritance, Decorator, Abstract Factory, Singleton, Global Object | 04 |
| ★ Ben Wilson, *Machine Learning Engineering in Action* (Manning, 2022). Chapter PDFs in [data-engineering/sources/ml-engineering-in-action/](../../data-engineering/sources/ml-engineering-in-action/); the book's home is [data-engineering 06](../../data-engineering/06-ml-platform/references.md) | Ch. 4 experimental code ("a little janky", never extended into the final solution) and the 4x feature-to-model code rule of thumb, ch. 9 Listing 9.4 (a unit test of a private method), ch. 10 Table 10.1 (ML code smells) and the nested-logic example (821,570 lines for eight models). Folded in as: ch. 4 → [01](notes/01-readable-code-and-smells.md#smells-that-show-up-in-ml-code), [02](notes/02-refactoring.md); ch. 9 → [05](notes/05-testing-strategy.md); ch. 10 → [01](notes/01-readable-code-and-smells.md#smells-that-show-up-in-ml-code) (Table 10.1, nested logic). Notes cite it as `(*Machine Learning Engineering in Action*, ch. N)` | 01, 02, 05 |
| ★ Jake VanderPlas, *Python Data Science Handbook* (O'Reilly, 2016, first edition, inferred from the library versions in its output). Chapter PDFs in [data-analytics/sources/python-data-science-handbook/](../../data-analytics/sources/python-data-science-handbook/); no whole-book PDF | Ch. 1 IPython help, `%timeit` against `%time`, `%prun`, `%lprun`, `%memit`, `%mprun`, `%xmode` and `%debug`. Folded in as: ch. 1 → [06](notes/06-debugging-and-profiling.md#the-same-tools-inside-ipython). Notes cite it as `(*Python Data Science Handbook*, ch. 1)` | 06 |

## Core papers

| Paper | Read | Why | Maps to |
|---|---|---|---|
| Parnas, [On the Criteria To Be Used in Decomposing Systems into Modules](https://doi.org/10.1145/361598.361623), CACM 1972 | Abstract, criteria, circular-shift discussion | The origin of information hiding | 03 |
| Liskov and Wing, [A Behavioral Notion of Subtyping](https://doi.org/10.1145/197320.197383), TOPLAS 1994 | Abstract, subtype requirement | What substitutability precisely asks | 03 |
| Brooks, [No Silver Bullet](https://doi.org/10.1109/MC.1987.1663532), 1986 | Abstract | Essential vs accidental difficulty | 03 |
| Moseley and Marks, [Out of the Tar Pit](https://curtclifton.net/papers/MoseleyMarks06a.pdf), 2006 ⚑ ([PDF](../sources/moseley-2006-out-tar-pit.pdf)) | Sec. 4.1.2 (state), 7 (avoid, separate), 9 (FRP, hypothetical) | State as the main source of accidental complexity; a position paper with no experiments | 03 |
| Sjøberg, Yamashita, Anda, Mockus, Dybå, [Quantifying the Effect of Code Smells on Maintenance Effort](https://doi.org/10.1109/TSE.2012.89), IEEE TSE 2013 | Abstract and findings as cited in 01 | Evidence on how much smells matter | 01 |
| Kim, Zimmermann, Nagappan, [A Field Study of Refactoring Challenges and Benefits](https://doi.org/10.1145/2393596.2393655), FSE 2012 | Abstract, intro, §3.1, conclusions | What practitioners mean by refactoring, and what it costs | 02 |
| Petrović, Ivanković, Fraser, Just, [Practical Mutation Testing at Scale](https://arxiv.org/abs/2102.11378), 2021 (arXiv) | Abstract, intro, parts of §2, conclusions; not the full evaluation | Why mutation is run at diff level, not as a score | 05 |

## Essays and articles

| Source | Read | Maps to |
|---|---|---|
| Ousterhout and Martin, [*A Philosophy of Software Design* vs *Clean Code*](https://github.com/johnousterhout/aposd-vs-clean-code) | Intro, method length, comments, TDD summary, closing | 01, 03 |
| Fowler, [Code Smell](https://martinfowler.com/bliki/CodeSmell.html), [Flag Argument](https://martinfowler.com/bliki/FlagArgument.html) (first part) | As noted | 01 |
| Fowler, [Definition of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html), [Opportunistic Refactoring](https://martinfowler.com/bliki/OpportunisticRefactoring.html), [preparatory refactoring example](https://martinfowler.com/articles/preparatory-refactoring-example.html) (intro and two hats), [refactoring.com](https://refactoring.com/) catalogue sketches | As noted | 02 |
| Feathers, [Characterization Testing](https://michaelfeathers.silvrback.com/characterization-testing) | Main text | 02 |
| Sato, [Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) (first part); Fowler, [Branch by Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html), [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) | As noted | 02, 07 |
| Martin, [The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html), [Solid Relevance](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html) | Main text | 03 |
| North, [CUPID: for joyful coding](https://dannorth.net/blog/cupid-for-joyful-coding/) | Most | 03, 04 |
| Metz, [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction); Abramov, [Goodbye, Clean Code](https://overreacted.io/goodbye-clean-code/) | Main text | 03 |
| Muratori, ['Clean' Code, Horrible Performance](https://www.computerenhance.com/p/clean-code-horrible-performance) | Numbers and ending | 03 |
| Fowler, [Yagni](https://martinfowler.com/bliki/Yagni.html), [BeckDesignRules](https://martinfowler.com/bliki/BeckDesignRules.html) | Main text | 03 |
| Norvig, [Design Patterns in Dynamic Programming](https://norvig.com/design-patterns/design-patterns.pdf), 1996 | Slides 9 and 10, about Lisp and Dylan | 04 |
| Fowler, [Gateway](https://martinfowler.com/articles/gateway-pattern.html) (first sections); Hieatt and Mee, [Repository](https://martinfowler.com/eaaCatalog/repository.html) (catalogue entry) | As noted | 04 |
| Fowler, [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html), [Test Coverage](https://martinfowler.com/bliki/TestCoverage.html) | Whole | 05 |
| Fowler, [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) | Intro, state vs behaviour, classical vs mockist, conclusion | 05 |
| Vocke, [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) | Contract tests section | 05 |
| Gregg, [Flame Graphs](https://www.brendangregg.com/flamegraphs.html) | Description, flame chart distinction, off-CPU mention | 06 |
| Ubl, [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) | Most: purpose, anatomy, when not to write one, lifecycle | 07 |
| Nygard, [Documenting Architecture Decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions), 2011 | Most | 07 |
| Beams, [How to Write a Git Commit Message](https://cbea.ms/git-commit/) | The seven rules; rule 5 in detail | 07 |
| DORA, [Trunk-based development](https://dora.dev/capabilities/trunk-based-development/) | Most of the page; not the underlying 2016 and 2017 reports | 07 |

## Style guides and practice docs

| Source | Read | Maps to |
|---|---|---|
| [PEP 8](https://peps.python.org/pep-0008/); [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) §3.16 and §3.18; [Ruff C901](https://docs.astral.sh/ruff/rules/complex-structure/) | As noted | 01 |
| Google Engineering Practices: [Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html), [What to Look For](https://google.github.io/eng-practices/review/reviewer/looking-for.html), [Speed](https://google.github.io/eng-practices/review/reviewer/speed.html), [Comments](https://google.github.io/eng-practices/review/reviewer/comments.html), [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html), [CL Descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html) | Standard in full; the others in the parts cited | 07 |

## Reference documentation

| Source | Read | Maps to |
|---|---|---|
| Python 3.14: [unittest.mock](https://docs.python.org/3.14/library/unittest.mock.html) | Autospec parts | 05 |
| Python 3.14: [pdb](https://docs.python.org/3.14/library/pdb.html), [profilers](https://docs.python.org/3.14/library/profile.html), [faulthandler](https://docs.python.org/3.14/library/faulthandler.html), [perf support](https://docs.python.org/3.14/howto/perf_profiling.html), [breakpoint](https://docs.python.org/3.14/library/functions.html#breakpoint), [sys](https://docs.python.org/3.14/library/sys.html) | Parts each chapter uses; perf support only its top | 06 |
| [PEP 768](https://peps.python.org/pep-0768/), safe external debugger interface | Abstract, motivation, rationale, controls, permissions | 06 |
| [py-spy README](https://github.com/benfred/py-spy) | Intro, commands, permissions | 06 |
| [Hypothesis docs](https://hypothesis.readthedocs.io/en/latest/) | Quickstart, parts of the tutorial, glossary | 05 |
| Git manual: [bisect](https://git-scm.com/docs/git-bisect), [rebase](https://git-scm.com/docs/git-rebase) (autosquash), [reflog](https://git-scm.com/docs/git-reflog), [worktree](https://git-scm.com/docs/git-worktree), [range-diff](https://git-scm.com/docs/git-range-diff) | Description and the options used | 07 |
