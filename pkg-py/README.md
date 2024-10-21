# brand.yml Python Package


``` python
from brand_yml import Brand

brand = Brand(
    meta = {"name": "Posit PBC", "link": "https://posit.co"}
)

brand.meta
```

    BrandMeta(name=BrandMetaName(full='Posit PBC'), link=BrandMetaLink(home=Url('https://posit.co/')))

## Installation

### From PyPI

``` bash
uv pip install brand_yml
```

### From GitHub

``` bash
uv pip install "git+https://github.com/posit-dev/brand-yml#subdirectory=pkg-py"
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management, [ruff](https://docs.astral.sh/ruff/) for linting and
formatting, [pre-commit](https://pre-commit.com/) for automated linting
on commit, [pytest](https://docs.pytest.org/en/stable/) for testing, and
[quartodoc](https://machow.github.io/quartodoc/) for documentation. All
primary commands are available in the `Makefile` in the repo root, and
`make` without arguments prints a list of commands.

To get started, use `make py-setup` to set up the development
environment with all development dependencies and using the oldest
supported version of Python. Use `make py-check` to check tests,
formatting, and type hints with a single version of Python, or
`make py-check-tox` to check across all supported versions of Python in
parallel.

`brand_yml` is being developed in tandem with new features planned for
Quarto v1.6, so we also use [qvm](https://github.com/dpastoor/qvm) to
manage Quarto versions, which is pinned in this project. Use
`make install-quarto` (assuming qvm is installed) to install the pinned
version of Quarto. Updating the package documentation is not currently
automated. Run `make py-docs` to update the documentation. Docs are
published automatically by GitHub Actions to
https://posit-dev.github.io/brand-yml/.

### Releases

This project uses [hatch-vcs](https://github.com/ofek/hatch-vcs) for
versioning. Version tags for the Python project use
`py/v{major}.{minor}.{patch}{extra}`.
