# wc-tool

A simple `wc`-like command-line tool that counts lines, words, and characters in files or standard input.

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
| `--help` | | Show help message and exit |

When no flags are specified, all three counts (lines, words, characters) are displayed.

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

## Output Format

Counts are printed as tab-separated values followed by the filename:

```
<lines>	<words>	<chars>	<filename>
```

When processing multiple files, a `total` line is appended:

```
10	50	300	file1.txt
20	100	600	file2.txt
30	150	900	total
```

Only the requested counts are shown when individual flags are used:

```bash
$ wc-tool -w file.txt
50	file.txt
```

## Error Handling

If a file is not found, permission is denied, or a directory is passed instead of a file, an error message is printed to stderr and processing continues with the remaining files:

```
wc-tool: missing.txt: No such file or directory
```
