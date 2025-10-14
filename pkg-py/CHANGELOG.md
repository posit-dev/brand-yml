# Changelog

<!--
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
-->

## [UNRELEASED]

* `Brand.from_yaml()` now consults the `BRAND_YML_PATH` environment variable when `path` is not provided. (#90)

* Added `use_brand_yml_path()` context manager to temporarily set `BRAND_YML_PATH` environment variable. (#92)

* Added `Brand.use_logo()` method to resolve and use brand logos in a variety of contexts, including Shiny apps. (#98)

* Use PEP 735 `dependency-groups` for dev dependencies. (#100)

* brand_yml now requires pydantic 2.10+. (#100)

## [0.1.1]

### Bug fixes

* Fixed a calculation to correctly convert `in` and `cm` to `rem` units for `brand.typography.base.size`. (#60)

* Updated for compatibility with pydantic v2.11.0 and v2.30.0. (#78)

## [0.1.0]

Initial release of `brand_yml`.
