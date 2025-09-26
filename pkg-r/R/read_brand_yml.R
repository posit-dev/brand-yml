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
  path <- path %||% envvar_brand_yml_path()

  path <- find_project_brand_yml(
    path,
    max_parents = if (is.null(path)) 20 else 1
  )

  brand <- as_brand_yml(path)
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
#' @param brand A list or string of YAML representing the brand, or a path to a
#'   brand.yml file.
#'
#' @return A normalized `brand_yml` list.
#'
#' @export
as_brand_yml <- function(brand) {
  UseMethod("as_brand_yml")
}

#' @export
as_brand_yml.default <- function(brand) {
  cli::cli_abort(
    "`brand` must be a list or character vector, not {.obj_type_friendly {brand}}."
  )
}

#' @export
as_brand_yml.character <- function(brand) {
  if (length(brand) == 1 && file.exists(brand)) {
    path <- brand
    brand <- read_yaml(path)
    brand$path <- path_norm(path)
  } else {
    brand_list <- yaml::yaml.load(brand, eval.expr = FALSE)
    if (!is.list(brand_list)) {
      cli::cli_abort(
        "{.var brand} must be a path to a brand.yml file or a string of YAML."
      )
    }
    brand <- brand_list
  }
  as_brand_yml(brand)
}

#' @export
as_brand_yml.list <- function(brand) {
  # Validate and normalize the brand structure
  brand <- brand_meta_normalize(brand)
  brand <- brand_color_normalize(brand)
  brand <- brand_typography_normalize(brand)
  brand <- brand_logo_normalize(brand)

  # This is here for consistency with the python package, see
  # Brand._resolve_typography_colors()
  brand <- brand_resolve_typography_colors(brand)

  brand <- compact(brand)

  # Convert to snake-case names after validation and normalization
  brand <- list_restyle_names(brand, "snake")

  class(brand) <- "brand_yml"
  brand
}

#' @export
as_brand_yml.brand_yml <- function(brand) {
  brand
}

brand_path_dir <- function(brand, required = TRUE) {
  check_is_brand_yml(brand)

  if (!required && is.null(brand$path)) {
    return(NULL)
  }

  if (!is_string(brand$path)) {
    cli::cli_abort(
      "{.var brand} must have been read from a file on disk or have a {.var path} field."
    )
  }
  dirname(brand$path)
}

brand_path <- function(brand, ...) {
  dir <- brand_path_dir(brand, required = FALSE) %||% "."
  path <- file.path(...)

  is_abs <- substr(path, 1, 1) == "/"
  is_link <- substr(path, 1, 4) == "http"

  if (is_abs || is_link) {
    return(path)
  }

  file.path(dir, path)
}


# Find _brand.yml --------------------------------------------------------------
find_project_brand_yml <- function(path = NULL, max_parents = 20) {
  path <- path %||% getwd()
  path <- path_norm(path)

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

  extra <- if (max_parents_og == 1) {
    ""
  } else if (max_parents_og == 2) {
    " or its parent directory"
  } else {
    cli::format_inline(
      " or its {.field {max_parents_og - max_parents - 1}} parent directories"
    )
  }

  cli::cli_abort(
    "Could not find {.or {.strong {filename}}} in {.path {dir_og}}{extra}.",
    class = "brand_yml_not_found"
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

path_norm <- function(path, winslash = "/", mustWork = FALSE) {
  normalizePath(path, mustWork = mustWork, winslash = winslash)
}

# Display ---------------------------------------------------------------------

#' @export
print.brand_yml <- function(x, ...) {
  path <- x$path %||% "_brand.yml"
  path <- sub(path.expand("~/"), "~/", path, fixed = TRUE)

  brand_yml <- format(x, ...)

  for (section in c("meta", "color", "typography", "logo", "defaults")) {
    pattern <- paste0("(^|\\n)", section, ":")
    replacement <- paste0("\\1", cli::style_bold(cli::col_cyan(section)), ":")
    brand_yml <- sub(pattern, replacement, brand_yml)
  }

  for (subsection in c("palette", "images", "fonts")) {
    pattern <- paste0("\n  ", subsection, ":")
    replacement <- paste0("\n  ", cli::style_italic(subsection), ":")
    brand_yml <- sub(pattern, replacement, brand_yml)
  }

  cli::cli_text("## {.path {path}}")
  cli::cli_verbatim(brand_yml)
  cli::cat_line()

  invisible(x)
}

#' @export
format.brand_yml <- function(x, ..., style = c("kebab")) {
  path <- x$path %||% "_brand.yml"
  path <- sub(path.expand("~/"), "~/", path, fixed = TRUE)

  x$path <- NULL

  if (brand_has(x, "typography", "fonts")) {
    if (identical(x$typography$fonts, list())) {
      x$typography$fonts <- NULL
    }
  }

  x <- list_restyle_names(x, style)
  yaml::as.yaml(x, indent.mapping.sequence = TRUE, ...)
}
