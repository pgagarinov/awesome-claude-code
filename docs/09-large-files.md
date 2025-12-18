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

### 4. Use Subagents for Analysis

```
> Analyse src/legacy/monolith.py and create a summary of:
  - All exported functions and their purposes
  - Dependencies and imports
  - Potential issues or code smells
  Don't show me the full file, just the analysis.
```

### 5. Chunked Refactoring

```
# Step 1: Understand structure
> Outline the structure of src/legacy/giant_module.py

# Step 2: Identify extraction candidates
> Identify functions that could be extracted into separate modules

# Step 3: Extract incrementally
> Extract the validation logic (lines 150-220) into src/utils/validation.py
```
