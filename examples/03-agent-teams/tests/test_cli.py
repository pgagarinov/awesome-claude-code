import os

import pytest
from click.testing import CliRunner

from agent_teams.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample file with known content."""
    f = tmp_path / "sample.txt"
    f.write_text("hello world\nfoo bar baz\n")
    return f


@pytest.fixture
def empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    return f


class TestSingleFile:
    def test_default_all_counts(self, runner, sample_file):
        """With no flags, show lines, words, and chars."""
        result = runner.invoke(main, [str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"   # lines
        assert parts[1] == "5"   # words
        assert parts[2] == "24"  # chars
        assert parts[3] == str(sample_file)

    def test_lines_only(self, runner, sample_file):
        result = runner.invoke(main, ["--lines", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"
        assert parts[1] == str(sample_file)
        assert len(parts) == 2

    def test_words_only(self, runner, sample_file):
        result = runner.invoke(main, ["--words", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "5"
        assert parts[1] == str(sample_file)
        assert len(parts) == 2

    def test_chars_only(self, runner, sample_file):
        result = runner.invoke(main, ["--chars", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "24"
        assert parts[1] == str(sample_file)
        assert len(parts) == 2

    def test_short_flags(self, runner, sample_file):
        """Short flags -l, -w, -c should work."""
        result = runner.invoke(main, ["-l", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"

        result = runner.invoke(main, ["-w", str(sample_file)])
        parts = result.output.strip().split("\t")
        assert parts[0] == "5"

        result = runner.invoke(main, ["-c", str(sample_file)])
        parts = result.output.strip().split("\t")
        assert parts[0] == "24"


class TestFlagCombinations:
    def test_lines_and_words(self, runner, sample_file):
        result = runner.invoke(main, ["--lines", "--words", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"
        assert parts[1] == "5"
        assert parts[2] == str(sample_file)
        assert len(parts) == 3

    def test_lines_and_chars(self, runner, sample_file):
        result = runner.invoke(main, ["--lines", "--chars", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"
        assert parts[1] == "24"
        assert parts[2] == str(sample_file)
        assert len(parts) == 3

    def test_words_and_chars(self, runner, sample_file):
        result = runner.invoke(main, ["--words", "--chars", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "5"
        assert parts[1] == "24"
        assert parts[2] == str(sample_file)
        assert len(parts) == 3

    def test_all_flags_explicit(self, runner, sample_file):
        result = runner.invoke(main, ["-l", "-w", "-c", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"
        assert parts[1] == "5"
        assert parts[2] == "24"
        assert parts[3] == str(sample_file)


class TestMultipleFiles:
    def test_two_files_with_totals(self, runner, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello\n")
        f2.write_text("world foo\n")

        result = runner.invoke(main, [str(f1), str(f2)])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert len(lines) == 3  # two files + total

        # File 1: 1 line, 1 word, 6 chars
        p1 = lines[0].split("\t")
        assert p1[0] == "1"
        assert p1[1] == "1"
        assert p1[2] == "6"
        assert p1[3] == str(f1)

        # File 2: 1 line, 2 words, 10 chars
        p2 = lines[1].split("\t")
        assert p2[0] == "1"
        assert p2[1] == "2"
        assert p2[2] == "10"
        assert p2[3] == str(f2)

        # Total
        pt = lines[2].split("\t")
        assert pt[0] == "2"   # 1 + 1
        assert pt[1] == "3"   # 1 + 2
        assert pt[2] == "16"  # 6 + 10
        assert pt[3] == "total"

    def test_single_file_no_total(self, runner, sample_file):
        """With one file, no total row should appear."""
        result = runner.invoke(main, [str(sample_file)])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert len(lines) == 1


class TestEmptyFile:
    def test_empty_file_counts(self, runner, empty_file):
        result = runner.invoke(main, [str(empty_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "0"  # lines
        assert parts[1] == "0"  # words
        assert parts[2] == "0"  # chars
        assert parts[3] == str(empty_file)


class TestFileNotFound:
    def test_nonexistent_file(self, runner):
        result = runner.invoke(main, ["/nonexistent/file.txt"])
        assert result.exit_code == 0  # wc doesn't fail, it prints errors to stderr
        assert "wc-tool: /nonexistent/file.txt:" in result.output or \
               "wc-tool: /nonexistent/file.txt:" in (result.output + (result.output or ""))

    def test_nonexistent_file_stderr(self, runner):
        """Error message should go to stderr."""
        result = runner.invoke(main, ["/nonexistent/file.txt"])
        assert "wc-tool: /nonexistent/file.txt:" in result.stderr
        assert result.stdout == ""

    def test_mix_valid_and_invalid(self, runner, sample_file):
        """Should still count valid files even when some are invalid."""
        result = runner.invoke(main, [str(sample_file), "/no/such/file"])
        assert result.exit_code == 0
        # The valid file output should be in stdout
        assert str(sample_file) in result.stdout
        # Error for the invalid file should be in stderr
        assert "wc-tool: /no/such/file:" in result.stderr


class TestStdin:
    def test_read_from_stdin_with_dash(self, runner):
        result = runner.invoke(main, ["-"], input="hello world\n")
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "1"   # lines
        assert parts[1] == "2"   # words
        assert parts[2] == "12"  # chars
        assert parts[3] == "-"

    def test_read_from_stdin_no_args(self, runner):
        """With no file arguments, should read from stdin."""
        result = runner.invoke(main, [], input="one two three\n")
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "1"
        assert parts[1] == "3"
        assert parts[2] == "14"
        assert parts[3] == "-"

    def test_stdin_multiline(self, runner):
        result = runner.invoke(main, ["-"], input="line1\nline2\nline3\n")
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "3"   # lines
        assert parts[1] == "3"   # words
        assert parts[2] == "18"  # chars


class TestEdgeCases:
    def test_file_no_trailing_newline(self, runner, tmp_path):
        f = tmp_path / "no_newline.txt"
        f.write_text("hello world")
        result = runner.invoke(main, [str(f)])
        parts = result.output.strip().split("\t")
        assert parts[0] == "0"   # no newline = 0 lines
        assert parts[1] == "2"   # 2 words
        assert parts[2] == "11"  # 11 chars

    def test_file_with_multiple_spaces(self, runner, tmp_path):
        f = tmp_path / "spaces.txt"
        f.write_text("hello   world\n")
        result = runner.invoke(main, [str(f)])
        parts = result.output.strip().split("\t")
        assert parts[1] == "2"  # still 2 words despite multiple spaces

    def test_file_only_newlines(self, runner, tmp_path):
        f = tmp_path / "newlines.txt"
        f.write_text("\n\n\n")
        result = runner.invoke(main, [str(f)])
        parts = result.output.strip().split("\t")
        assert parts[0] == "3"  # 3 lines
        assert parts[1] == "0"  # 0 words
        assert parts[2] == "3"  # 3 chars


class TestBytes:
    def test_bytes_ascii(self, runner, sample_file):
        """For ASCII content, bytes should equal chars."""
        result = runner.invoke(main, ["--bytes", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "24"  # bytes (same as chars for ASCII)
        assert parts[1] == str(sample_file)
        assert len(parts) == 2

    def test_bytes_multibyte_utf8(self, runner, tmp_path):
        """For multi-byte UTF-8 content, bytes should differ from chars."""
        f = tmp_path / "utf8.txt"
        f.write_text("café\n", encoding="utf-8")
        # chars: 5 (c, a, f, é, \n)
        # bytes: 6 (é is 2 bytes in UTF-8)
        result_bytes = runner.invoke(main, ["--bytes", str(f)])
        parts_bytes = result_bytes.output.strip().split("\t")
        assert parts_bytes[0] == "6"

        result_chars = runner.invoke(main, ["--chars", str(f)])
        parts_chars = result_chars.output.strip().split("\t")
        assert parts_chars[0] == "5"

    def test_bytes_short_flag(self, runner, sample_file):
        """-b should work as short form of --bytes."""
        result = runner.invoke(main, ["-b", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "24"

    def test_bytes_not_in_default(self, runner, sample_file):
        """Bytes should not be shown in default output (no flags)."""
        result = runner.invoke(main, [str(sample_file)])
        parts = result.output.strip().split("\t")
        # Default: lines, words, chars, name = 4 parts
        assert len(parts) == 4


class TestMaxLineLength:
    def test_max_line_length_varying(self, runner, tmp_path):
        """Max line length should report the longest line."""
        f = tmp_path / "varying.txt"
        f.write_text("a\nbb\nccc\n")
        result = runner.invoke(main, ["--max-line-length", str(f)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "3"  # longest line is "ccc"
        assert parts[1] == str(f)

    def test_max_line_length_single_line(self, runner, tmp_path):
        f = tmp_path / "single.txt"
        f.write_text("hello world\n")
        result = runner.invoke(main, ["-L", str(f)])
        parts = result.output.strip().split("\t")
        assert parts[0] == "11"  # len("hello world")

    def test_max_line_length_empty_file(self, runner, empty_file):
        result = runner.invoke(main, ["--max-line-length", str(empty_file)])
        parts = result.output.strip().split("\t")
        assert parts[0] == "0"

    def test_max_line_length_not_in_default(self, runner, sample_file):
        """Max line length should not be shown in default output."""
        result = runner.invoke(main, [str(sample_file)])
        parts = result.output.strip().split("\t")
        assert len(parts) == 4  # lines, words, chars, name

    def test_max_line_length_multi_file_totals(self, runner, tmp_path):
        """Total row should show max of all file max-line-lengths."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("short\n")          # max line len: 5
        f2.write_text("a longer line\n")  # max line len: 13
        result = runner.invoke(main, ["-L", str(f1), str(f2)])
        lines = result.output.strip().split("\n")
        assert len(lines) == 3  # two files + total
        # Total should have max of 5 and 13 = 13
        total_parts = lines[2].split("\t")
        assert total_parts[0] == "13"
        assert total_parts[1] == "total"


class TestVersion:
    def test_version_long_flag(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "wc-tool" in result.output
        assert "0.1.0" in result.output

    def test_version_short_flag(self, runner):
        result = runner.invoke(main, ["-V"])
        assert result.exit_code == 0
        assert "wc-tool" in result.output
        assert "0.1.0" in result.output


class TestDirectoryError:
    def test_directory_path_error(self, runner, tmp_path):
        """Passing a directory should produce an error on stderr."""
        result = runner.invoke(main, [str(tmp_path)])
        assert f"wc-tool: {tmp_path}:" in result.stderr
        assert result.stdout == ""


class TestPermissionError:
    def test_no_read_permission(self, runner, tmp_path):
        """File with no read permission should produce error on stderr."""
        f = tmp_path / "noperm.txt"
        f.write_text("secret\n")
        os.chmod(f, 0o000)
        try:
            result = runner.invoke(main, [str(f)])
            # Click validates readability at the argument level
            assert result.exit_code != 0
            assert "not readable" in result.stderr or f"wc-tool: {f}:" in result.stderr
        finally:
            os.chmod(f, 0o644)  # restore for cleanup


class TestUnicodeContent:
    def test_emoji_all_counts(self, runner, tmp_path):
        """Test with emoji content across all count types."""
        f = tmp_path / "emoji.txt"
        f.write_text("hello 🌍\n", encoding="utf-8")
        # chars: 8 (h,e,l,l,o,' ',🌍,'\n')
        # bytes: 11 (🌍 is 4 bytes in UTF-8)
        # lines: 1, words: 2, max line length: 7
        result = runner.invoke(main, ["-l", "-w", "-c", "-b", "-L", str(f)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "1"   # lines
        assert parts[1] == "2"   # words
        assert parts[2] == "8"   # chars
        assert parts[3] == "11"  # bytes
        assert parts[4] == "7"   # max line length
        assert parts[5] == str(f)

    def test_multibyte_bytes_greater_than_chars(self, runner, tmp_path):
        """Verify bytes > chars for multi-byte content."""
        f = tmp_path / "multi.txt"
        f.write_text("café ☕ naïve\n", encoding="utf-8")
        result_chars = runner.invoke(main, ["-c", str(f)])
        result_bytes = runner.invoke(main, ["-b", str(f)])
        chars = int(result_chars.output.strip().split("\t")[0])
        bytes_ = int(result_bytes.output.strip().split("\t")[0])
        assert bytes_ > chars


class TestHelpFlag:
    def test_help_output(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        output_lower = result.output.lower()
        assert "lines" in output_lower
        assert "words" in output_lower
        assert "bytes" in output_lower
        assert "longest line" in output_lower or "max-line-length" in output_lower


class TestNewFlagCombinations:
    def test_bytes_and_lines(self, runner, sample_file):
        """--bytes with --lines should show lines then bytes."""
        result = runner.invoke(main, ["--lines", "--bytes", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"   # lines
        assert parts[1] == "24"  # bytes (ASCII, same as chars)
        assert parts[2] == str(sample_file)
        assert len(parts) == 3

    def test_max_line_length_and_words(self, runner, sample_file):
        """--max-line-length with --words should show words then max-line-length."""
        result = runner.invoke(main, ["--words", "--max-line-length", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "5"   # words
        assert parts[1] == "11"  # max line length (both lines are 11 chars)
        assert parts[2] == str(sample_file)
        assert len(parts) == 3

    def test_all_flags_together(self, runner, sample_file):
        """All flags should show lines, words, chars, bytes, max-line-length, name."""
        result = runner.invoke(main, ["-l", "-w", "-c", "-b", "-L", str(sample_file)])
        assert result.exit_code == 0
        parts = result.output.strip().split("\t")
        assert parts[0] == "2"   # lines
        assert parts[1] == "5"   # words
        assert parts[2] == "24"  # chars
        assert parts[3] == "24"  # bytes (ASCII)
        assert parts[4] == "11"  # max line length
        assert parts[5] == str(sample_file)
        assert len(parts) == 6

    def test_bytes_with_multi_file_totals(self, runner, tmp_path):
        """--bytes with multiple files should sum bytes in total row."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello\n")       # 6 bytes
        f2.write_text("café\n")        # 6 bytes (é = 2 bytes)
        result = runner.invoke(main, ["-b", str(f1), str(f2)])
        lines = result.output.strip().split("\n")
        assert len(lines) == 3  # two files + total
        p1 = lines[0].split("\t")
        assert p1[0] == "6"   # hello\n = 6 bytes
        p2 = lines[1].split("\t")
        assert p2[0] == "6"   # café\n = 6 bytes
        pt = lines[2].split("\t")
        assert pt[0] == "12"  # total bytes
        assert pt[1] == "total"
