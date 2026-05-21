# Changelog

<!--
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
-->

## [0.2.0] - 2026-05-21

### New features

* `Brand.from_yaml()` now consults the `BRAND_YML_PATH` environment variable when `path` is not provided. (#90)

* Added `use_brand_yml_path()` context manager to temporarily set `BRAND_YML_PATH` environment variable. (#92)

* Added `Brand.use_logo()` method to resolve and use brand logos in a variety of contexts, including Shiny apps. (#98)

### Bug fixes

* `BrandLogoResource.tagify()` and `BrandLogoResourceLightDark.tagify()` now annotate their return type as `htmltools.Tagified` and fully tagify their output, complying with htmltools 0.7.0's tightened Tagifiable contract. Without this fix, rendering a brand logo with htmltools 0.7.0+ raises `TypeError` at the render boundary. (#115)

### Breaking changes

* Dropped support for Python 3.9, which reached end of life on
  2025-10-31. brand_yml now requires Python 3.10 or later.

### Dependencies

* brand_yml now requires pydantic 2.10+. (#100)

### Other changes

* Use PEP 735 `dependency-groups` for dev dependencies. (#100)

## [0.1.1]

### Bug fixes

* Fixed a calculation to correctly convert `in` and `cm` to `rem` units for `brand.typography.base.size`. (#60)

* Updated for compatibility with pydantic v2.11.0 and v2.30.0. (#78)

## [0.1.0]

Initial release of `brand_yml`.
