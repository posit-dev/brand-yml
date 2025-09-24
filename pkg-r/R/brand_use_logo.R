brand_use_logo <- function(
  brand,
  name,
  variant = c("auto", "light", "dark"),
  ...,
  required = FALSE,
  allow_fallback = TRUE
) {
  brand <- as_brand_yml(brand)
  name <- arg_match(name, c("small", "medium", "large"))

  variant <- arg_match(variant)

  if (isTRUE(required)) {
    required_reason <- ""
  } else if (isFALSE(required)) {
    required_reason <- NULL
  } else {
    check_string(required)
    required_reason <- paste0(" ", trimws(required))
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
  is_light_dark <- inherits(this, "light_dark")

  if ((variant %in% c("light", "dark")) && !is_light_dark && !allow_fallback) {
    if (!is.null(required_reason)) {
      cli::cli_abort(
        "{.var brand.logo.{name}} doesn't have a {.val {variant}} variant, but {.var brand.logo.{name}.{variant}} is required{required_reason}."
      )
    }
    return(NULL)
  }

  if (is_light_dark) {
    if (variant == "auto") {
      # If auto, prefer light, but use whichever is available
      variants <- intersect(c("light", "dark"), names(this))
      if (length(variants) > 0) {
        this <- this[[variants[1]]]
      } else {
        # This shouldn't be possible after `as_brand_yml()` validation, but
        # someone could get here manually.
        this <- NULL # nocov
      }
    } else {
      this <- this[[variant]]
    }
  }

  if (is.null(this)) {
    if (!is.null(required_reason)) {
      cli::cli_abort(
        "{.var brand.logo.{name}.{variant}} is required{required_reason}."
      )
    }
    return(NULL)
  }

  base_path <- brand$path %||% "."
  is_abs <- substr(this$path, 1, 1) == "/"
  is_link <- substr(this$path, 1, 4) == "http"

  if (!(is_abs || is_link)) {
    this$path <- file.path(base_path, this$path)
  }

  this
}
