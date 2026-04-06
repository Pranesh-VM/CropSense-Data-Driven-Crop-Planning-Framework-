---
description: 'Guidelines for creating high-quality IEEE research papers in LaTeX'
applyTo: '**/research_paper/**/*.tex'
---

# Research Paper LaTeX Guidelines

Instructions for creating effective, maintainable, and publication-ready IEEE research papers in LaTeX format.

## Scope and Principles
- Target audience: students and researchers authoring academic papers.
- Goals: consistent formatting, correct IEEE compliance, clear structure, and professional presentation.
- Primary references: IEEE Transactions style guide, IEEEtran documentation, and academic best practices.

## File Structure and Organization

### Document Class and Packages
- Use `\documentclass[conference]{IEEEtran}` for conference papers
- Organize packages logically with comments separating sections
- Load essential packages: `cite`, `amsmath`, `amssymb`, `graphicx`, `hyperref`, `algorithm`, `algpseudocode`
- Include `microtype` for improved typography
- Set `colorlinks=true` for better PDF readability

### Directory Layout
```
research_paper/
├── main.tex                 # Main document with structure
├── references.bib           # Bibliography in BibTeX format
├── figures/                 # All figures and diagrams
│   ├── Archi.png
│   ├── results_chart.pdf
│   └── comparison_table.png
└── .claude/
    └── rules/
        ├── prompt.instructions.md
        └── research-paper.instructions.md
```

## Paper Structure

### Section Hierarchy and Naming
Follow standard IEEE paper organization:
1. **Title and Authors** — Concise, descriptive title; clear author affiliations
2. **Abstract** — 150–250 words; problem statement, solution, results, impact
3. **Keywords** — 5–8 keywords for indexing (comma-separated, capitalized)
4. **Introduction** — Context, motivation, research gap, contributions (enumerated)
5. **Related Work** — Comprehensive literature review organized by theme, gap analysis
6. **System Architecture / Methodology** — Clear description and diagrams
7. **Modules / Detailed Sections** — One section per major component
8. **Experiments and Results** — Methodology, metrics, results with statistics
9. **Conclusion** — Summary, limitations, future work
10. **References** — IEEE numeric citations [1], [2], etc.

### Section Commands
- Use `\section{}` with `\label{sec:sectionname}` for top-level sections
- Use `\subsection{}` and `\subsubsection{}` for hierarchy
- Include descriptive comments above major sections (e.g., `% ── 3. Related Work ────────────────────`)

## Citations and Bibliography

### Citation Format
- **IEEE numeric style**: [1], [2], etc., in square brackets
- Place citations **after** the statement, **before** punctuation: `... studied crops~\cite{Author2025}.`
- Use `~\cite{}` for non-breaking space before citation
- Multiple citations: `\cite{Author1,Author2}` → [1], [2]
- Author-year references in text: `Author et al.~\cite{Author2025}` → `Author et al. [1]`

### BibTeX Entry Standards
- Organize `references.bib` by entry key (e.g., `Author2025`)
- Use consistent formatting:
  ```bibtex
  @article{Author2025,
    author = {First, A. and Second, B.},
    title = {Title with {Capitalization} for {Important} {Words}},
    journal = {Journal Name},
    volume = {10},
    number = {5},
    pages = {100--110},
    year = {2025},
    doi = {10.xxxx/xxxxxx}
  }
  ```
- Protect proper nouns and acronyms with braces: `{AI}`, `{LSTM}`, `{IEEE}`
- Include DOI when available

## Tables and Figures

### Table Conventions
- Use `table*` environment for full-page width tables (avoid single-column overflow)
- Include descriptive captions above tables: `\caption{Dataset Summary}`
- Use `\label{tab:name}` for references: `Table~\ref{tab:dataset}`
- Apply `\renewcommand{\arraystretch}{1.1}` for readability
- Use `booktabs` package for professional horizontal rules (`\toprule`, `\midrule`, `\bottomrule`)
- Specify column widths for text-heavy tables: `p{2.5cm}p{3.5cm}` instead of `ll`

### Figure Conventions
- Use `figure*` for full-width figures in two-column layout
- Include `\label{fig:name}` for cross-references: `Figure~\ref{fig:arch}`
- Place figures in `figures/` directory; reference with `\graphicspath{{figures/}}`
- Use `\centering` and `[htbp]` placement specifier
- Provide detailed, informative captions: `\caption{System Architecture. The framework integrates six modules...}`
- Support formats: `.pdf`, `.png`, `.jpg` (vector preferred over raster)

## Equations and Mathematics

### Equation Formatting
- Use `equation` environment for numbered equations with `\label{eq:name}`
- Reference equations: `Equation~\ref{eq:zscore}` or `Eq.~\eqref{eq:zscore}`
- Use `align*` for multi-line equations without numbering
- Use `align` for multi-line numbered equations
- Define notation clearly before use (e.g., "where $X \in \mathbb{R}^{n \times m}$")
- Use `\textbf{}` for vector/matrix names if needed for clarity

### Mathematical Notation
- Vectors and matrices: `$X$`, `$\mathbf{X}$` for bold matrices
- Calligraphic sets: `$\mathcal{S}$` for state spaces
- Probability: `$P(X)$`, `$\mathbb{E}[X]$` for expectation
- Products and summation: `$\prod_{i=1}^{n}$`, `$\sum_{j}$`

## Algorithms and Pseudocode

### Algorithm Block Formatting
- Use `algorithm` package with `algpseudocode`
- Include `\caption{Algorithm Name}` and `\label{alg:name}`
- Define inputs/outputs: `\Require` and `\Ensure`
- Use clear control structures: `\For{...} ... \EndFor`, `\If{...} ... \EndIf`
- Comment important steps: `\Comment{Purpose of this step}`

### Example Algorithm Structure
```latex
\begin{algorithm}[htbp]
\caption{Feature Standardisation}
\label{alg:standardize}
\begin{algorithmic}[1]
\Require Raw feature matrix $X$
\Ensure Standardised matrix $X_s$, parameters $\mu$, $\sigma$
\State $\mu \gets \mathrm{Mean}(X)$
\State $X_s \gets (X - \mu) / \sigma$
\State \Return $X_s, \mu, \sigma$
\end{algorithmic}
\end{algorithm}
```

## Writing Style and Conventions

### Formal Academic Tone
- Use third person (avoid "I" or "we" unless reporting team effort)
- Use past tense for methods and results: "We developed...", "The dataset contained..."
- Use present tense for general truths: "LSTM networks capture temporal patterns"
- Use active voice where possible: "The model learns..." vs. "Learning occurs..."

### Technical Language
- Define acronyms at first use: "Long Short-Term Memory (LSTM) networks"
- Use consistent terminology throughout the paper
- Bold important concepts when first introduced: `\textbf{Rainfall-Induced Nutrient Depletion Model (RINDM)}`
- Use proper mathematical notation, not words: $X$ not "X", $\alpha$ not "alpha"

### Formatting Best Practices
- Use non-breaking spaces: `Author~et al.`, `Section~\ref{sec:intro}`, `Table~\ref{tab:1}`
- Use en-dashes for ranges: `10--20 pages`, `2020--2025`
- Use em-dashes for emphasis: `The results---surprisingly---showed...(rarely used)`
- Avoid abbreviations in text; spell out: "Figure 1" not "Fig. 1" (unless space-constrained)

## Cross-References and Navigation

### Consistent Referencing
- Sections: `Section~\ref{sec:intro}`, `Section~\ref{sec:related}`
- Figures: `Figure~\ref{fig:arch}`
- Tables: `Table~\ref{tab:dataset}`
- Equations: `Equation~\ref{eq:loss}` or `Eq.~\eqref{eq:loss}`
- Algorithms: `Algorithm~\ref{alg:lstm}`

### Label Naming Convention
- Use descriptive, lowercase labels
- Prefixes: `sec:`, `fig:`, `tab:`, `eq:`, `alg:`
- Example: `\label{sec:related}`, `\label{fig:system_arch}`

## Quality Assurance Checklist

- [ ] **Structure**: All required sections present (abstract, intro, related work, methodology, results, conclusion)
- [ ] **Citations**: All claims supported by citations; no orphaned statements
- [ ] **References**: BibTeX entries complete (author, title, journal, year, volume/pages, DOI)
- [ ] **Cross-references**: All figures, tables, equations, and sections properly labeled and referenced
- [ ] **Formatting**: Consistent capitalization, spacing, and punctuation throughout
- [ ] **Tables**: Full-width tables use `table*`; columns properly aligned; captions descriptive
- [ ] **Figures**: High-quality images; captions are informative; referenced in text before appearance
- [ ] **Equations**: Numbered and defined; notation explained; proper spacing
- [ ] **Algorithms**: Clear pseudocode; inputs/outputs declared; controls properly formatted
- [ ] **Writing**: Grammar checked; active voice preferred; technical terms defined; consistent tense
- [ ] **IEEE Compliance**: Numeric citations [1], [2]; correct document class; proper keyword panel
- [ ] **PDF Output**: Compiles without errors/warnings; hyperlinks functional; line breaks natural
- [ ] **Originality**: Proper attribution for all referenced work; no plagiarism
- [ ] **Completeness**: Abstract captures all key contributions; conclusion summarizes findings

## Maintenance and Version Control

- Keep `main.tex` at the document root; modularize only if document exceeds 50 pages
- Update `references.bib` whenever new citations are added
- Use descriptive commit messages: "Add related work section" or "Update RINDM equations"
- Review generated PDF before committing to catch formatting issues
- Track large binary files (figures) separately; prefer vector formats (.pdf, .eps) over raster (.png)

## Compilation and Troubleshooting

### Standard LaTeX Compilation Steps
```bash
pdflatex main.tex          # First pass: generate .aux file
bibtex main                # Generate bibliography
pdflatex main.tex          # Second pass: resolve citations
pdflatex main.tex          # Third pass: resolve cross-references
```

### Common Issues and Solutions
| Issue | Cause | Solution |
|-------|-------|----------|
| Citation shows `[?]` | BibTeX entry missing or misspelled | Run `bibtex main` and recompile |
| Labels undefined | `\label{}` and `\ref{}` mismatch | Check label names and scoping |
| Overfull hbox | Text exceeds column width | Use `p{width}` columns or `\linewidth` |
| Figure overflow | Figure too wide for column | Use `\includegraphics[width=\columnwidth]{figure.pdf}` |
| Package conflict | Multiple packages incompatible | Check documentation; load in standard order |

## References and Resources
- IEEE Transactions Style Guide: https://journals.ieeeauthorcenter.ieee.org/
- IEEEtran Documentation: https://ctan.org/pkg/ieeetran
- LaTeX Wikibook: https://en.wikibooks.org/wiki/LaTeX/
- Overleaf Templates: https://www.overleaf.com/latex/templates/

