#' Temporarily set the `BRAND_YML_PATH` environment variable
#'
#' This function sets the `BRAND_YML_PATH` environment variable to the specified
#' path for the duration of the local environment. This ensures that, for the
#' scope of the local environment, any calls to functions that automatically
#' discover a `_brand.yml` file will use the path specified.
#'
#' @examples
#' # Create a temporary brand.yml file in a tempdir for this example
#' tmpdir <- withr::local_tempdir("brand")
#' path_brand <- file.path(tmpdir, "my-brand.yml")
#' yaml::write_yaml(
#'   list(color = list(primary = "#abc123")),
#'   path_brand
#' )
#'
#' with_brand_yml_path(path_brand, {
#'   brand <- read_brand_yml()
#'   brand$color$primary
#' })
#'
#' @param path The path to a brand.yml file.
#' @inheritParams withr::local_envvar
#'
#' @inherit withr::with_envvar return
#'
#' @describeIn with_brand_yml_path Run code in a temporary environment with the
#'   `BRAND_YML_PATH` environment variable set to `path`.
#'
#' @family brand.yml helpers
#' @export
with_brand_yml_path <- function(path, code) {
  local_brand_yml_path(path)
  force(code)
}

#' @describeIn with_brand_yml_path Set the `BRAND_YML_PATH` environment variable
#'   for the scope of the local environment (e.g. within the current function).
#' @export
local_brand_yml_path <- function(path, .local_envir = parent.frame()) {
  withr::local_envvar(
    BRAND_YML_PATH = path,
    .local_envir = .local_envir,
    action = "replace"
  )
}

envvar_brand_yml_path <- function() {
  path <- Sys.getenv("BRAND_YML_PATH", "")
  if (nzchar(path)) path_norm(path) else NULL
}
