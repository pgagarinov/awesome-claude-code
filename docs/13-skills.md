# Part 13: Skills

## What Are Skills?

Skills are pre-packaged capabilities that extend Claude Code for specific file types or tasks. They provide specialised handling that goes beyond default file reading.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SKILLS                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Skills enhance Claude Code's ability to work with specific file types          │
│  or perform specialised tasks.                                                  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  Without Skill:                                                         │   │
│  │  PDF → Raw binary / basic text extraction                               │   │
│  │                                                                         │   │
│  │  With PDF Skill:                                                        │   │
│  │  PDF → Structured content + tables + images + metadata                  │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  Available Skills:                                                              │
│                                                                                 │
│  • pdf        - Enhanced PDF reading and analysis                               │
│  • xlsx       - Excel spreadsheet handling                                      │
│  • docx       - Word document processing                                        │
│  • images     - Advanced image analysis                                         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Using Skills

Skills are invoked automatically when relevant, or you can invoke them explicitly:

```
> Analyse the quarterly report at ./reports/Q4-2024.pdf

  [PDF skill activated - extracting structured content...]
```

```
> Extract all tables from ./data/financial-data.xlsx and summarise the trends

  [XLSX skill activated - parsing spreadsheet...]
```

## Skill Capabilities

### PDF Skill
- Extract text with formatting preserved
- Parse tables into structured data
- Extract embedded images
- Read metadata (author, creation date, etc.)
- Handle multi-page documents

### XLSX Skill
- Read multiple sheets
- Parse formulas and values
- Handle merged cells
- Extract charts as data
- Process large spreadsheets efficiently

### DOCX Skill
- Extract formatted text
- Parse tables and lists
- Handle images and diagrams
- Read comments and track changes
- Extract document metadata

## When Skills Activate

Skills activate automatically based on:
1. File extension (.pdf, .xlsx, .docx)
2. File content type
3. Explicit invocation

```
> Read ./docs/specification.pdf
  # PDF skill auto-activates

> What does the spreadsheet at ./data/metrics.xlsx show?
  # XLSX skill auto-activates
```

## Defining Custom Skills

Skills are markdown files in `.claude/skills/` that tell Claude how to handle specific file types or tasks.

### Structure

```
.claude/
└── skills/
    └── pdf.md      # Skill for handling PDFs
```

### Example: PDF Analysis Skill

Create `.claude/skills/pdf.md`:

````markdown
# PDF Analysis Skill

When asked to read or analyse a PDF file, follow this approach:

## For Large PDFs (over 50 pages)

Do NOT read the entire PDF into context. Instead:

1. **Write a Python script** to extract what's needed:
   ```python
   import pymupdf  # or pdfplumber

   doc = pymupdf.open("file.pdf")

   # Extract table of contents
   toc = doc.get_toc()

   # Extract text from specific pages
   for page_num in range(min(5, len(doc))):
       page = doc[page_num]
       text = page.get_text()

   # Extract tables
   # Extract images
   # etc.
   ```

2. **Run the script** and analyse the output

3. **Read specific pages** only if needed for detail

## For Tables in PDFs

Use `pdfplumber` or `camelot` to extract tables:
```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            # Process table data
```

## For Searching PDFs

Write a script to search rather than reading everything:
```python
import pymupdf

doc = pymupdf.open("file.pdf")
for page in doc:
    results = page.search_for("search term")
    if results:
        print(f"Page {page.number}: {page.get_text('text')}")
```

## Dependencies

If not installed, install with:
```bash
pip install pymupdf pdfplumber camelot-py
```
````

### Example: Log Analysis Skill

Create `.claude/skills/logs.md`:

````markdown
# Log Analysis Skill

When asked to analyse log files, especially large ones:

## Never Read Full Logs

Log files can be gigabytes. Always use tools:

1. **Get overview first**:
   ```bash
   wc -l file.log           # Line count
   head -100 file.log       # First 100 lines
   tail -100 file.log       # Last 100 lines
   ```

2. **Search for patterns**:
   ```bash
   grep -c "ERROR" file.log     # Count errors
   grep -B2 -A2 "ERROR" file.log  # Errors with context
   ```

3. **For complex analysis**, write a Python script:
   ```python
   from collections import Counter

   errors = Counter()
   with open("file.log") as f:
       for line in f:
           if "ERROR" in line:
               # Extract error type and count
               errors[error_type] += 1
   ```
````

### Skill Activation

Skills activate when:
- You reference a matching file type
- The skill's trigger conditions are met
- You explicitly invoke with the skill name
