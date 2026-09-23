# Temporarily set the `BRAND_YML_PATH` environment variable

This function sets the `BRAND_YML_PATH` environment variable to the
specified path for the duration of the local environment. This ensures
that, for the scope of the local environment, any calls to functions
that automatically discover a `_brand.yml` file will use the path
specified.

## Usage

``` r
with_brand_yml_path(path, code)

local_brand_yml_path(path, .local_envir = parent.frame())
```

## Arguments

- path:

  The path to a brand.yml file.

- code:

  `[any]`  
  Code to execute in the temporary environment

- .local_envir:

  `[environment]`  
  The environment to use for scoping.

## Value

`[any]`  
The results of the evaluation of the `code` argument.

## Functions

- `with_brand_yml_path()`: Run code in a temporary environment with the
  `BRAND_YML_PATH` environment variable set to `path`.

- `local_brand_yml_path()`: Set the `BRAND_YML_PATH` environment
  variable for the scope of the local environment (e.g. within the
  current function).

## See also

Other brand.yml helpers:
[`brand_color_pluck()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_color_pluck.md),
[`brand_has()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_has.md),
[`brand_pluck()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/brand_pluck.md)

## Examples

``` r
# Create a temporary brand.yml file in a tempdir for this example
tmpdir <- withr::local_tempdir("brand")
path_brand <- file.path(tmpdir, "my-brand.yml")
yaml::write_yaml(
  list(color = list(primary = "#abc123")),
  path_brand
)
#> Warning: cannot open file '/tmp/RtmprxOkEa/brand1c513bb73bc9/my-brand.yml': No such file or directory
#> Error in file(file, "w", encoding = fileEncoding): cannot open the connection

with_brand_yml_path(path_brand, {
  brand <- read_brand_yml()
  brand$color$primary
})
#> Error in as_brand_yml(path): `brand` must be a path to a brand.yml file or a string of YAML.
```
