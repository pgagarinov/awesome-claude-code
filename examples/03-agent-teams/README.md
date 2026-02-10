# wc-tool

A simple `wc`-like command-line tool that counts lines, words, characters, and bytes in files or standard input.

## Installation

```bash
pixi install
```

This installs the package in editable mode and makes the `wc-tool` command available.

## Usage

```
wc-tool [OPTIONS] [FILES]...
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--lines` | `-l` | Count lines |
| `--words` | `-w` | Count words |
| `--chars` | `-c` | Count characters |
| `--bytes` | `-b` | Count bytes |
| `--max-line-length` | `-L` | Display the length of the longest line |
| `--version` | `-V` | Show version and exit |
| `--help` | | Show help message and exit |

When no flags are specified, the three default counts (lines, words, characters) are displayed. The `--bytes` and `--max-line-length` flags are opt-in and only shown when explicitly requested.

## Examples

Count all stats for a single file:

```bash
wc-tool README.md
```

Count only lines:

```bash
wc-tool -l README.md
```

Combine flags to show lines and words:

```bash
wc-tool -l -w README.md
```

Multiple files (displays per-file counts and a total):

```bash
wc-tool file1.txt file2.txt file3.txt
```

Read from stdin:

```bash
echo "hello world" | wc-tool
cat README.md | wc-tool -w
```

Use `-` explicitly for stdin:

```bash
wc-tool - < input.txt
```

Count bytes (useful for files with multibyte characters):

```bash
wc-tool -b file.txt
```

Find the longest line length:

```bash
wc-tool -L file.txt
```

Combine new and existing flags:

```bash
wc-tool -l -w -b file.txt
wc-tool -c -L file.txt
```

Check the version:

```bash
wc-tool --version
```

## Output Format

Counts are printed as tab-separated values followed by the filename. When all flags are specified, the column order is:

```
<lines>	<words>	<chars>	<bytes>	<max-line-length>	<filename>
```

With default flags (no flags specified), only lines, words, and chars are shown:

```
<lines>	<words>	<chars>	<filename>
```

When processing multiple files, a `total` line is appended:

```
10	50	300	file1.txt
20	100	600	file2.txt
30	150	900	total
```

For `--max-line-length`, the total row shows the maximum across all files.

Only the requested counts are shown when individual flags are used:

```bash
$ wc-tool -w file.txt
50	file.txt

$ wc-tool -b -L file.txt
512	78	file.txt
```

## Error Handling

If a file is not found, permission is denied, or a directory is passed instead of a file, an error message is printed to stderr and processing continues with the remaining files:

```
wc-tool: missing.txt: No such file or directory
```

## Development

### Installation

Install the project in editable (development) mode:

```bash
pixi install
```

### Running Tests

```bash
pixi run pytest tests/ -v
```

### Project Structure

```
├── src/agent_teams/
│   ├── __init__.py
│   └── cli.py          # CLI entry point and core logic
├── tests/
│   └── test_cli.py     # Test suite
├── pyproject.toml       # Project metadata and dependencies
└── README.md
```
