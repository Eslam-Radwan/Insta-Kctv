import os
import sys
import subprocess
import argparse
import logging

logger = logging.getLogger(__name__)


def compile_tex(tex_path, engine="pdflatex", passes=3):
    if not os.path.exists(tex_path):
        logger.error(f"File not found: {tex_path}")
        return False

    if not tex_path.endswith(".tex"):
        logger.error(f"Input must be a .tex file, got: {tex_path}")
        return False

    if not _check_engine(engine):
        logger.error(f"LaTeX engine '{engine}' not found. Is it installed?")
        return False

    tex_dir = os.path.dirname(os.path.abspath(tex_path))
    tex_file = os.path.basename(tex_path)

    original_cwd = os.getcwd()
    os.chdir(tex_dir)

    try:
        for i in range(passes):
            logger.info(f"Running {engine} (pass {i + 1}/{passes})...")
            result = subprocess.run(
                [engine, "-interaction=nonstopmode", tex_file],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                errors = _extract_errors(result.stdout)
                if errors:
                    for err in errors:
                        logger.error(err)
                    logger.error(f"{engine} failed on pass {i + 1}")
                    return False

        logger.info(f"Successfully compiled: {tex_path}")
        return True
    finally:
        os.chdir(original_cwd)


def _check_engine(engine):
    try:
        subprocess.run([engine, "--version"], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False


def _extract_errors(log_output):
    errors = []
    for line in log_output.splitlines():
        if line.lower().startswith("!"):
            errors.append(line.strip())
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile a .tex file to PDF")
    parser.add_argument("tex_file", help="Path to the .tex file to compile")
    parser.add_argument("--engine", default="pdflatex",
                        choices=["pdflatex", "xelatex", "lualatex"],
                        help="LaTeX engine to use (default: pdflatex)")
    parser.add_argument("--passes", type=int, default=3,
                        help="Number of compilation passes (default: 3)")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    success = compile_tex(args.tex_file, engine=args.engine, passes=args.passes)
    sys.exit(0 if success else 1)
