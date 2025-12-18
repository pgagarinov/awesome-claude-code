# Part 9: Working with Large Files

## The Problem

Large files (500+ lines) consume significant context. Reading them entirely is often unnecessary.

## Strategies

### 1. Targeted Reading

```
# BAD: Read entire file
> Read src/legacy/monolith.py

# GOOD: Read specific sections
> Show me lines 1-50 of src/legacy/monolith.py (the imports)

> Read the UserService class in src/legacy/monolith.py

> Find and show me the process_payment function in src/legacy/monolith.py
```

### 2. Structural Overview First

```
> Give me an outline of src/legacy/monolith.py - list all classes,
  functions, and their line numbers without reading the full content
```

### 3. Search Before Reading

```
> Search for 'validate_user' in src/legacy/monolith.py and show
  me just that function with 10 lines of context
```

### 4. Write a Script to Analyse

Instead of reading a large file into context, ask Claude to write a script that processes it:

```
# BAD: Reading a 500-page PDF directly
> Read reports/annual-report-2024.pdf and summarise it

# GOOD: Write a script to extract what you need
> Write a Python script that extracts all tables from
  reports/annual-report-2024.pdf and saves them as CSVs

> Write a script to count word frequency in docs/specification.pdf
  and output the top 50 terms
```

This approach:
- Keeps the large file out of context entirely
- Produces reusable tooling
- Works especially well for PDFs, spreadsheets, and log files

### 5. Use Subagents for Analysis

```
> Analyse src/legacy/monolith.py and create a summary of:
  - All exported functions and their purposes
  - Dependencies and imports
  - Potential issues or code smells
  Don't show me the full file, just the analysis.
```

### 6. Chunked Refactoring

```
# Step 1: Understand structure
> Outline the structure of src/legacy/giant_module.py

# Step 2: Identify extraction candidates
> Identify functions that could be extracted into separate modules

# Step 3: Extract incrementally
> Extract the validation logic (lines 150-220) into src/utils/validation.py
```
