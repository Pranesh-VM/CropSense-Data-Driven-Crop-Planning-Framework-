# CropSense Research Paper — Overleaf Setup Guide

## Quick Start (5 minutes)

### Step 1: Create a New Project on Overleaf
1. Go to [Overleaf.com](https://www.overleaf.com) and log in
2. Click **New Project** → **Blank Project**
3. Name it: `CropSense-MainPaper`
4. Click **Create**

---

## Step 2: Upload Files to Overleaf

### 2A. Upload Main LaTeX File
1. In the left sidebar, click **Files** (folder icon)
2. Click **Upload** button
3. Upload local file: **`main.tex`** from this folder
4. The file will appear in your project root

### 2B. Upload Bibliography
1. Click **Upload** again
2. Upload: **`references.bib`** from this folder
3. This will be in the project root (same level as `main.tex`)

### 2C. Create Figures Folder and Upload Images
1. In the left sidebar, click **New Folder** (+ icon)
2. Name it exactly: **`figures`** (no capital letters)
3. Click into the `figures` folder
4. Click **Upload**
5. Select **all 42 PNG files** from your local folder:
   ```
   evaluation_metrics/plots/*.png
   ```
   Upload them to the `figures/` folder

**Expected structure in Overleaf:**
```
CropSense-MainPaper/
├── main.tex              ← Root document
├── references.bib        ← Bibliography database
└── figures/              ← Image folder
    ├── 01_metrics_comparison.png
    ├── 02_confusion_matrix_ensemble.png
    ├── 03_roc_curves.png
    ├── ... (all 42 PNG files)
    └── 42_qlearning_epsilon_decay.png
```

---

## Step 3: Set Overleaf Compiler and Main Document

1. Click **Menu** (top-left, three horizontal lines)
2. Under **Settings**, find **Compiler** dropdown
3. Select **pdfLaTeX** (recommended for IEEE papers)
4. Under **Main document**, click dropdown and select **main.tex**
5. Click **Recompile** button (or enable auto-compile)

---

## Step 4: Compile and View PDF

1. Click the **Recompile** button (or top-right blue button)
2. Once compilation finishes (30-60 seconds), your PDF appears in the right panel
3. Use **Full screen** button to view full page

**Expected result:** A properly formatted two-column IEEE conference paper with title, abstract, all sections, figures, and bibliography.

---

## Troubleshooting

### Issue: "Cannot find file `figures/xxx.png`"
**Solution:** 
- Verify the `figures/` folder exists (exact name, lowercase)
- Confirm all PNG files are inside `figures/` folder
- Check that folder structure in the left sidebar matches the expected layout

### Issue: Bibliography doesn't appear
**Solution:**
- Ensure `references.bib` is in the **root** (same folder as `main.tex`)
- Verify `\bibliographystyle{IEEEtran}` is present in main.tex
- Verify `\bibliography{references}` is present (without `.bib` extension)
- Recompile twice: once with **Recompile**, and once more if needed

### Issue: "Undefined control sequence" or package warnings
**Solution:**
- These are normal if you see warnings like "empty bibliography"
- The main.tex preamble includes all necessary packages:
  - `\usepackage{cite}` — Citation management
  - `\usepackage{graphicx}` — Image insertion
  - `\usepackage{booktabs}` — Professional tables
  - `\usepackage{amsmath,amssymb,amsfonts}` — Math support
  - All other required packages are included

### Issue: Figures appear in wrong size or overflow
**Solution:**
- Figures are set to `[width=\columnwidth]` for single-column and `[width=\textwidth]` for double-column
- If overflow occurs, reduce the width value in the corresponding `\includegraphics` command

### Issue: PDF build fails or takes >2 minutes
**Solution:**
- Click **Menu** → **Logs and output files**
- Review error messages
- Check that png files are <5 MB each
- Try switching compiler briefly to **XeLaTeX**, then back to **pdfLaTeX**

---

## File Summary

| File Name | What It Is | Where to Upload |
|-----------|-----------|-----------------|
| `main.tex` | Main LaTeX document with all sections | Overleaf Root |
| `references.bib` | BibTeX bibliography database | Overleaf Root |
| 42 PNG files | Evaluation metrics and results figures | `figures/` subfolder |

---

## Writing and Editing Tips

### Modifying Content
- The `main.tex` file is divided into clear sections with comments:
  ```latex
  % ── 1. Introduction ──────────────────────
  \section{Introduction}
  % ── 2. Related Work ──────────────────────
  \section{Related Work}
  ```
- Edit section content between `\section{}` and the next section marker
- Do NOT edit section numbers (LaTeX handles them automatically)

### Adding Figures
- To add a new figure in a section:
  ```latex
  \begin{figure}[htbp]
  \centering
  \includegraphics[width=\columnwidth]{figures/new_image.png}
  \caption{Description of your figure.}
  \label{fig:new_image}
  \end{figure}
  ```
- Reference it in text: `Fig.~\ref{fig:new_image}`

### Adding Citations
- Use format: `\cite{BibTeXKey}` e.g., `\cite{Alam2025}`
- Add new citations to `references.bib` following existing format
- Citation numbering is automatic

### Equation References
- Equations use `\label{eq:name}` and are cited as `\eqref{eq:name}`
- Example: "As shown in~\eqref{eq:zscore}, Z-score normalisation..."

---

## IEEE Standards Compliance

This template follows **IEEE Transactions** guidelines:
- ✅ Two-column conference format (`\documentclass[conference]{IEEEtran}`)
- ✅ Professional typography with `microtype` package
- ✅ No vertical lines in tables (IEEE style)
- ✅ Proper citation style (numeric `[1], [2]`)
- ✅ Correct bibliography format (IEEEtran style)
- ✅ Drop caps support for article opening (optional)

---

## Exporting and Submission

### Download PDF
1. Click **PDF** button (top-right)
2. Click **Download PDF** button

### Download Source (for submission)
1. Click **Menu** → **Download Source**
2. Downloads a `.zip` file with all project files

### Submit to Conference
- Most IEEE conferences accept `.zip` of Overleaf source
- Or submit the PDF directly for review
- Check conference submission guidelines

---

## Recommended Next Steps

1. **Proofread:** Read through the PDF for typos and clarity
2. **Update Author Affiliations:** Edit author block with real institution names
3. **Adjust Figures:** If needed, resize figures or rearrange sections
4. **Create Full Appendix:** Add appendix with implementation details
5. **Share for Collaboration:** Use Overleaf's "Share" button to invite colleagues

---

## Support

- **Overleaf Help:** Click **Help** (?) icon in Overleaf for live chat
- **LaTeX Error Help:** Error messages appear in the "Logs and output files" section
- **IEEE Guidelines:** See [IEEE Author Center](https://authorservices.ieee.org/)

---

**Status:** ✅ Production-Ready  
**Last Updated:** March 28, 2026  
**Total Pages (Expected):** 12–14 pages
