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
