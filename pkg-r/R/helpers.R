# Brand utilities --------------------------------------------------------------

#' Check if a brand has a specific nested element
#'
#' @description
#' Checks if a given `brand` object has a specific nested element accessible via
#' the additional arguments provided as key paths.
#'
#' @examples
#' brand <- as_brand_yml(list(
#'   meta = list(name = "Example Brand"),
#'   color = list(primary = "#FF5733")
#' ))
#'
#' # Check if brand has a primary color
#' brand_has(brand, "color", "primary") # TRUE
#'
#' # Check if brand has a secondary color
#' brand_has(brand, "color", "secondary") # FALSE
#'
#' @param brand A brand object created by [read_brand_yml()] or
#'   [as_brand_yml()].
#' @param ... One or more character strings or symbols representing the path to
#'   the nested element to check.
#'
#' @return `TRUE` if the nested element exists in the brand object,
#'   `FALSE` otherwise.
#'
#' @family brand.yml helpers
#' @export
brand_has <- function(brand, ...) {
  x <- brand

  for (f in c(...)) {
    val <- tryCatch(x[[f]], error = function(e) NULL)
    if (is.null(val)) {
      return(FALSE)
    }
    x <- x[[f]]
  }

  TRUE
}

#' Extract a nested element from a brand object
#'
#' @description
#' Safely extracts a nested element from a `brand` object using the provided key
#' path. Returns `NULL` if the element doesn't exist.
#'
#' @examples
#' brand <- as_brand_yml(list(
#'   meta = list(name = "Example Brand"),
#'   color = list(primary = "#FF5733")
#' ))
#'
#' # Extract the primary color
#' brand_pluck(brand, "color", "primary") # "#FF5733"
#'
#' # Try to extract a non-existent element
#' brand_pluck(brand, "color", "secondary") # NULL
#'
#' @inheritParams brand_has
#' @param ... One or more character strings or symbols representing the path to
#'   the nested element to extract.
#'
#' @return The value of the nested element if it exists, `NULL` otherwise.
#' @family brand.yml helpers
#' @export
brand_pluck <- function(brand, ...) {
  if (!brand_has(brand, ...)) {
    return(NULL)
  }

  brand[[c(...)]]
}

brand_has_string <- function(brand, ...) {
  if (!brand_has(brand, ...)) {
    return(FALSE)
  }
  is_string(brand[[c(...)]])
}

brand_has_list <- function(brand, ...) {
  if (!brand_has(brand, ...)) {
    return(FALSE)
  }
  is_list(brand[[c(...)]])
}
