<div align="center">
<h1><img src="https://github.com/posit-dev/brand-yml/raw/refs/heads/main/docs/logos/wide/brand-yml-wide-color.svg" width="400px" alt="brand.yml" /></h1>

Unified branding with a single YAML file
</div>

<p align="center">
<!-- badges start -->
<a href="https://pypi.org/project/brand-yml/"><img alt="PyPI" src="https://img.shields.io/pypi/v/brand_yml?logo=python&logoColor=white&color=orange"></a>
<a href="https://github.com/posit-dev/brand-yml"><img src="https://github.com/posit-dev/brand-yml/actions/workflows/py-test.yml/badge.svg?branch=main" alt="Python Tests"></a>
<a href="https://choosealicense.com/licenses/mit/"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
<a href="https://choosealicense.com/licenses/mit/"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
<!-- badges end -->
</p>


## About brand.yml

Create reports, apps, dashboards, plots and more that match your company's brand guidelines with a single `_brand.yml` file.

**brand.yml** is a simple, portable YAML file that codifies your company's brand guidelines into a format that can be used by [Quarto](https://quarto.org), Python and R tooling to create branded outputs.
Our goal is to support unified, branded theming for all of [Posit's open source tools](https://posit.co/products/open-source/)—from web applications to printed reports to dashboards and presentations—with a consistent look and feel.

With a single `_brand.yml` file you can collect brand logos, colors, fonts and typographic choices, typically found in your company's brand guidelines.
This `_brand.yml` can be used Quarto and Shiny for Python[^1] to instantly basic themes that match the brand guidelines.

## Links

- [brand.yml Documentation](https://posit-dev.github.io/brand-yml) - The brand.yml specification, explanation, details, examples and more.

- [brand_yml for Python](https://posit-dev.github.io/brand-yml/pkg/py) - Python package for reading and applying the `_brand.yml` file.

- [Quarto](https://quarto.org) - An open-source scientific and technical publishing system. Automatically uses `_brand.yml` in the v1.6 release.

- [Shiny](https://shiny.posit.co) - An open-source framework for effortless web applications for data scientists. [Shiny for Python](https://shiny.posit.co/py) supports [branded theming via brand.yml](https://shiny.posit.co/py/api/core/ui.Theme.html#shiny.ui.Theme.from_brand). Support in Shiny for R will arrive soon.


## Contributing

**Questions?** Feel free to ask questions in [our discussions forum](https://github.com/posit-dev/brand-yml/discussions)! For questions about using brand.yml in Quarto, please head over to [Quarto's discussions](https://github.com/quarto-dev/quarto-cli/discussions).

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
