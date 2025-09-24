#' Extract a logo resource from a brand
#'
#' Returns a brand logo resource specified by name and variant from a brand
#' object. The image paths in the returned object are adjusted to be absolute,
#' relative to the location of the brand YAML file, if `brand` was read from a
#' file, or the local working directory otherwise.
#'
#' @examples
#' brand <- as_brand_yml(list(
#'   logo = list(
#'     images = list(
#'       small = "logos/small.png",
#'       huge = list(path = "logos/huge.png", alt = "Huge Logo")
#'     ),
#'     small = "small",
#'     medium = list(
#'       light = list(
#'         path = "logos/medium-light.png",
#'         alt = "Medium Light Logo"
#'       ),
#'       dark = list(path = "logos/medium-dark.png")
#'     )
#'   )
#' ))
#'
#' brand_use_logo(brand, "small")
#' brand_use_logo(brand, "medium")
#' brand_use_logo(brand, "large")
#' brand_use_logo(brand, "huge")
#'
#' brand_use_logo(brand, "small", variant = "light")
#' brand_use_logo(brand, "small", variant = "light", allow_fallback = FALSE)
#' brand_use_logo(brand, "small", variant = c("light", "dark"))
#' brand_use_logo(
#'   brand,
#'   "small",
#'   variant = c("light", "dark"),
#'   allow_fallback = FALSE
#' )
#'
#' brand_use_logo(brand, "medium", variant = "light")
#' brand_use_logo(brand, "medium", variant = "dark")
#' brand_use_logo(brand, "medium", variant = c("light", "dark"))
#'
#' @param brand A brand object from [read_brand_yml()] or [as_brand_yml()].
#' @param name The name of the logo to use. Either a size (`"small"`,
#'   `"medium"`, `"large"`) or an image name from `brand.logo.images`.
#' @param variant Which variant to use, only used when `name` is one of the
#'   brand.yml fixed logo sizes (`"small"`, `"medium"`, or `"large"`). Can be
#'   one of:
#'
#'   * `"auto"`: Auto-detect, returns a light/dark logo resource if both
#'     variants are present, otherwise it returns a single logo resource, either
#'     the value for `brand.logo.{name}` or the single light or dark variant if
#'     only one is present.
#'   * `"light"`: Returns only the light variant. If no light variant is
#'     present, but `brand.logo.{name}` is a single logo resource and
#'     `allow_fallback` is `TRUE`, `brand_use_logo()` falls back to the single
#'     logo resource.
#'   * `"dark"`: Returns only the dark variant, or, as above, falls back to the
#'     single logo resource if no dark variant is present and `allow_fallback`
#'     is `TRUE`.
#'   * `c("light", "dark")`: Returns a light/dark object with both variants. If
#'     a single logo resource is present for `brand.logo.{name}` and
#'     `allow_fallback` is `TRUE`, the single logo resource is promoted to a
#'     light/dark logo resource with identical light and dark variants.
#' @param required Logical or character string. If `TRUE`, an error is thrown if
#'   the requested logo is not found. If a string, it is used to describe why
#'   the logo is required in the error message and completes the phrase
#'   `"is required ____"`.
#' @param allow_fallback If `TRUE` (the default), allows falling back to a
#'   non-variant-specific logo when a specific variant is requested. Only used
#'   when `name` is one of the fixed logo sizes (`"small"`, `"medium"`, or
#'   `"large"`).
#' @param ... Ignored, must be empty.
#'
#' @return A `brand_logo_resource` object, a `brand_logo_resource_light_dark`
#'   object, or `NULL` if the requested logo doesn't exist and `required` is
#'   `FALSE`.
#'
#' @export
brand_use_logo <- function(
  brand,
  name,
  variant = c("auto", "light", "dark"),
  ...,
  required = FALSE,
  allow_fallback = TRUE
) {
  brand <- as_brand_yml(brand)
  check_dots_empty()
  check_string(name)
  check_bool(allow_fallback)

  if (isTRUE(required)) {
    required_reason <- ""
  } else if (isFALSE(required)) {
    required_reason <- NULL
  } else {
    check_string(required)
    required_reason <- paste0(" ", trimws(required))
  }

  if (!name %in% setdiff(names(brand$logo), "images")) {
    if (brand_has(brand, "logo", "images", name)) {
      res <- brand_pluck(brand, "logo", "images", name)
      res$path <- brand_path(brand, res$path)
      return(res)
    }

    if (!is.null(required_reason)) {
      if (!name %in% c("small", "medium", "large")) {
        name <- sprintf("images['%s']", name)
      }
      cli::cli_abort(
        "{.var brand.logo.{name}} is required{required_reason}."
      )
    }

    return(NULL)
  }

  name <- arg_match(name, c("small", "medium", "large"))
  variant <- arg_match(variant, multiple = TRUE)

  if ("auto" %in% variant) {
    variant <- "auto"
  } else if (
    identical(intersect(c("light", "dark"), variant), c("light", "dark"))
  ) {
    variant <- "light_dark"
  }

  if (!brand_has(brand, "logo", name)) {
    if (!is.null(required_reason)) {
      cli::cli_abort(
        "{.var brand.logo.{name}} is required{required_reason}."
      )
    }
    return(NULL)
  }

  this <- brand_pluck(brand, "logo", name)
  has_light_dark <- inherits(this, "light_dark")

  # Fixup internal paths to be relative to brand yml file.
  if (has_light_dark) {
    if (!is.null(this$light)) {
      this$light$path <- brand_path(brand, this$light$path)
    }
    if (!is.null(this$dark)) {
      this$dark$path <- brand_path(brand, this$dark$path)
    }
  } else {
    this$path <- brand_path(brand, this$path)
  }

  # | variant    | has        | fallback | return               | case |
  # |:-----------|:-----------|:---------|:---------------------|:-----|
  # | auto       | single     | ~        | single               | A.1  |
  # | auto       | light_dark | ~        | light_dark           | A.2  |
  # | auto       | light      | ~        | light                | A.3  |
  # | auto       | dark       | ~        | dark                 | A.4  |
  # | light,dark | light|dark | ~        | light_dark           | B.1  |
  # | light,dark | single     | TRUE     | single -> light_dark | B.2  |
  # | light,dark | single     | FALSE    |                      | B.3  |
  # | light      | light      | ~        | light                | C    |
  # | dark       | dark       | ~        | dark                 | C    |
  # | light      | single     | TRUE     | single               | D    |
  # | dark       | single     | TRUE     | single               | D    |
  # | light      | single     | FALSE    |                      | X    |
  # | dark       | single     | FALSE    |                      | X    |
  # | light      | dark       | ~        |                      | X    |
  # | dark       | light      | ~        |                      | X    |

  # Case A: "auto" variant
  if (variant == "auto") {
    if (!has_light_dark) {
      # Case A.1: Return single value as-is
      return(this)
    }

    if (!is.null(this$light) && !is.null(this$dark)) {
      # Case A.2: Return light_dark if both variants exist
      return(this)
    }

    if (!is.null(this$light)) {
      # Case A.3: Return light if only light exists
      return(this$light)
    }

    if (!is.null(this$dark)) {
      # Case A.4: Return dark if only dark exists
      return(this$dark)
    }
  }

  # Case B: "light_dark" variant
  if (variant == "light_dark") {
    if (has_light_dark) {
      # Case B.1: Return light_dark if both variants exist
      return(this)
    }

    if (allow_fallback) {
      # Case B.2: Promote single to light_dark if fallback allowed
      return(brand_logo_resource_light_dark(this, this))
    }

    # Case B.3: No fallback allowed, error or return NULL
    if (!is.null(required_reason)) {
      cli::cli_abort(
        "{.var brand.logo.{name}} requires light/dark variants{required_reason}."
      )
    }

    return(NULL)
  }

  # variant is now "light" or "dark" by definition

  if (has_light_dark) {
    # Case C: return specific variant if it exists
    if (!is.null(this[[variant]])) {
      return(this[[variant]])
    }
  } else {
    # Case D: return single if fallback allowed
    if (allow_fallback) {
      return(this)
    }
  }

  # Case X: specific variant doesn't exist and can't fallback
  if (!is.null(required_reason)) {
    cli::cli_abort(
      "{.var brand.logo.{.strong {name}.{variant}}} is required{required_reason}."
    )
  }

  return(NULL)
}
