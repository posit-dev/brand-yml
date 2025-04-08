#' Create a Brand instance from a Brand YAML file.
#'
#' Reads a Brand YAML file or finds and reads a `_brand.yml` file and
#' returns a validated `Brand` instance.
#'
#' By default, `read_brand_yml()` finds a project-specific `_brand.yml` file, by
#' looking in the current working directory directory or any parent directory
#' for a `_brand.yml`, `brand/_brand.yml` or `_brand/_brand.yml` file (or the
#' same variants with a `.yaml` extension). When `path` is provided,
#' `read_brand_yml()` looks for these files in the provided directory; for
#' automatic discovery, `read_brand_yml()` starts the search in the working
#' directory and moves upward to find the `_brand.yml` file.
#'
#' @examples
#'
#' # For this example: copy a brand.yml to a temporary directory
#' tmp_dir <- tempfile()
#' dir.create(tmp_dir)
#' file.copy(
#'   system.file("examples/brand-posit.yml", package = "brand.yml"),
#'   file.path(tmp_dir, "_brand.yml")
#' )
#'
#' brand <- read_brand_yml(tmp_dir)
#'
#' @param path The path to the brand.yml file or a directory where `_brand.yml`
#'   is expected to be found.
#'
#' @return A normalized `brand_yml` list from the brand.yml file.
#'
#' @references <https://posit-dev.github.io/brand-yml/>
#' @export
read_brand_yml <- function(path = NULL) {
  path <- find_project_brand_yml(
    path,
    max_parents = if (is.null(path)) 20 else 1
  )

  brand <- yaml::read_yaml(path, readLines.warn = FALSE)

  brand <- as_brand_yml(brand)
  brand$path <- path

  brand
}

#' Create a Brand instance from a list or character vector.
#'
#' @examples
#' as_brand_yml("
#' meta:
#'   name: Example Brand
#'
#' color:
#'   primary: '#FF5733'
#'   secondary: '#33FF57'
#' ")
#'
#' as_brand_yml(list(
#'   meta = list(name = "Example Brand"),
#'   color = list(primary = "#FF5733", secondary = "#33FF57")
#' ))
#'
#' @param brand A list or YAML as a character vector representing the brand.
#'
#' @return A normalized `brand_yml` list.
#'
#' @export
as_brand_yml <- function(brand) {
  UseMethod("as_brand_yml")
}

#' @export
as_brand_yml.character <- function(brand) {
  brand <- yaml::yaml.load(brand, eval.expr = FALSE)
  as_brand_yml(brand)
}

#' @export
as_brand_yml.list <- function(brand) {
  # Normalize brand internals !! MINIMAL VALIDATION !!
  brand <- brand_meta_normalize(brand)
  brand <- brand_color_normalize(brand)
  brand <- brand_typography_normalize(brand)
  brand <- brand_logo_normalize(brand)

  brand <- compact(brand)

  class(brand) <- "brand_yml"
  brand
}


# Find _brand.yml --------------------------------------------------------------

find_project_brand_yml <- function(path = NULL, max_parents = 20) {
  path <- path %||% getwd()
  path <- normalizePath(path, mustWork = FALSE)

  ext <- if (dir.exists(path)) "" else path_ext(path)
  if (ext %in% c("yml", "yaml")) {
    return(path)
  }

  if (nzchar(ext)) {
    path <- dirname(path)
  }

  find_project_file(
    filename = c("_brand.yml", "_brand.yaml"),
    dir = path,
    subdir = c("brand", "_brand"),
    max_parents = max_parents
  )
}

find_project_file <- function(
  filename,
  dir,
  subdir = character(),
  max_parents = 20
) {
  check_number_whole(max_parents, lower = 1)

  dir_og <- dir
  max_parents_og <- max_parents

  while (dir != dirname(dir) && max_parents > 0) {
    for (fname in filename) {
      file_path <- file.path(dir, fname)
      if (path_is_file(file_path)) {
        return(file_path)
      }
    }

    for (sub in subdir) {
      for (fname in filename) {
        file_path <- file.path(dir, sub, fname)
        if (path_is_file(file_path)) {
          return(file_path)
        }
      }
    }

    dir <- dirname(dir)
    max_parents <- max_parents - 1
  }

  abort(
    sprintf(
      "Could not find %s in %s%s.",
      paste(filename, collapse = ", "),
      dir_og,
      if (max_parents_og == 1) "" else if (max_parents == 2)
        "or its parent directory" else
        sprintf("or its %d parent directories", max_parents_og - 1)
    )
  )
}

path_is_file <- function(path) {
  # The file exists and is a file
  file.exists(path) && !dir.exists(path)
}

path_ext <- function(path) {
  # Same as tools::file_ext()
  pos <- regexpr("\\.([[:alnum:]]+)$", path)
  ifelse(pos > -1L, substring(path, pos + 1L), "")
}
