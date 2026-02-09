import sys

import click


def count_content(content):
    lines = content.count("\n")
    words = len(content.split())
    chars = len(content)
    return lines, words, chars


def format_counts(lines, words, chars, show_lines, show_words, show_chars, name):
    parts = []
    if show_lines:
        parts.append(str(lines))
    if show_words:
        parts.append(str(words))
    if show_chars:
        parts.append(str(chars))
    parts.append(name)
    return "\t".join(parts)


@click.command()
@click.argument("files", nargs=-1, type=click.Path(allow_dash=True))
@click.option("--lines", "-l", is_flag=True, help="Count lines.")
@click.option("--words", "-w", is_flag=True, help="Count words.")
@click.option("--chars", "-c", is_flag=True, help="Count characters.")
def main(files, lines, words, chars):
    """A simple wc-like tool that counts lines, words, and characters."""
    show_all = not (lines or words or chars)
    show_lines = lines or show_all
    show_words = words or show_all
    show_chars = chars or show_all

    if not files:
        files = ("-",)

    total_lines = 0
    total_words = 0
    total_chars = 0
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

            l, w, c = count_content(content)
            total_lines += l
            total_words += w
            total_chars += c
            file_count += 1

            click.echo(format_counts(l, w, c, show_lines, show_words, show_chars, name))
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            click.echo(f"wc-tool: {filepath}: {e.strerror}", err=True)

    if file_count > 1:
        click.echo(
            format_counts(
                total_lines,
                total_words,
                total_chars,
                show_lines,
                show_words,
                show_chars,
                "total",
            )
        )
