# Contributor Guidelines

## Overview

1. Be respectful and considerate in all interactions.
2. Before starting work on a new feature or bug fix, please open an issue to discuss it with the maintainers.
3. For minor changes or typo fixes, you can directly submit a pull request.
4. Try to follow the coding style and conventions used in the existing codebase.
5. Write clear, concise commit messages.
6. Include tests for new features or bug fixes.
7. Update documentation as necessary.
8. Be patient and open to feedback during the review process.
9. If you're unsure about anything, don't hesitate to ask for help or clarification.

We appreciate your contributions and look forward to working with you!


## `brand_yml` Python Package

The Python package uses [uv](https://docs.astral.sh/uv/) for dependency management,
[ruff](https://docs.astral.sh/ruff/) for linting and formatting,
[pre-commit](https://pre-commit.com/) for automated linting on commit,
[pytest](https://docs.pytest.org/en/stable/) for testing,
and [quartodoc](https://machow.github.io/quartodoc/) for documentation.
All primary commands are available in the `Makefile` in the repo root,
and `make` without arguments prints a list of commands.

To get started, use `make py-setup` to set up the development environment
with all development dependencies and using the oldest supported version of Python.
Use `make py-check` to check tests, formatting, and type hints with a single version of Python,
or `make py-check-tox` to check across all supported versions of Python in parallel.

`brand_yml` is being developed in tandem with new features planned for Quarto v1.6,
so we also use [qvm](https://github.com/dpastoor/qvm) to manage Quarto versions,
which is pinned in this project.
Use `make install-quarto` (assuming qvm is installed) to install the pinned version of Quarto.
Updating the package documentation is not currently automated.
Run `make py-docs` to update the documentation.
Docs are published automatically by GitHub Actions to https://posit-dev.github.io/brand-yml/.

### Releases

This project uses [hatch-vcs](https://github.com/ofek/hatch-vcs) for versioning.
Version tags for the Python project use `py/v{major}.{minor}.{patch}{extra}`.
