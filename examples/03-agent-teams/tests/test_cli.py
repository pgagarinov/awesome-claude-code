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
