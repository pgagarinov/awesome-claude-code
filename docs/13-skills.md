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
