import sys

import click


def count_content(content):
    lines = content.count("\n")
    words = len(content.split())
    chars = len(content)
    byte_count = len(content.encode("utf-8"))
    max_line_len = max((len(line) for line in content.splitlines()), default=0)
    return lines, words, chars, byte_count, max_line_len


def format_counts(
    lines, words, chars, byte_count, max_line_len,
    show_lines, show_words, show_chars, show_bytes, show_max_line_length, name,
):
    parts = []
    if show_lines:
        parts.append(str(lines))
    if show_words:
        parts.append(str(words))
    if show_chars:
        parts.append(str(chars))
    if show_bytes:
        parts.append(str(byte_count))
    if show_max_line_length:
        parts.append(str(max_line_len))
    parts.append(name)
    return "\t".join(parts)


@click.command()
@click.argument("files", nargs=-1, type=click.Path(allow_dash=True))
@click.option("--lines", "-l", is_flag=True, help="Count lines.")
@click.option("--words", "-w", is_flag=True, help="Count words.")
@click.option("--chars", "-c", is_flag=True, help="Count characters.")
@click.option("--bytes", "-b", "bytes_", is_flag=True, help="Count bytes.")
@click.option("--max-line-length", "-L", is_flag=True, help="Display the length of the longest line.")
@click.version_option("0.1.0", "-V", "--version", prog_name="wc-tool")
def main(files, lines, words, chars, bytes_, max_line_length):
    """A simple wc-like tool that counts lines, words, and characters."""
    show_all = not (lines or words or chars or bytes_ or max_line_length)
    show_lines = lines or show_all
    show_words = words or show_all
    show_chars = chars or show_all
    show_bytes = bytes_
    show_max_line_length = max_line_length

    if not files:
        files = ("-",)

    total_lines = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0
    max_max_line_len = 0
    file_count = 0

    for filepath in files:
        try:
            if filepath == "-":
                content = click.get_text_stream("stdin").read()
                name = "-"
            else:
                with open(filepath) as f:
                    content = f.read()
                name = filepath

            l, w, c, b, mll = count_content(content)
            total_lines += l
            total_words += w
            total_chars += c
            total_bytes += b
            max_max_line_len = max(max_max_line_len, mll)
            file_count += 1

            click.echo(
                format_counts(
                    l, w, c, b, mll,
                    show_lines, show_words, show_chars, show_bytes, show_max_line_length,
                    name,
                )
            )
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            click.echo(f"wc-tool: {filepath}: {e.strerror}", err=True)

    if file_count > 1:
        click.echo(
            format_counts(
                total_lines,
                total_words,
                total_chars,
                total_bytes,
                max_max_line_len,
                show_lines,
                show_words,
                show_chars,
                show_bytes,
                show_max_line_length,
                "total",
            )
        )
