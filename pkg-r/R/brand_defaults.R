brand_validate_bootstrap_defaults <- function(
  defaults,
  source = "brand.defaults.bootstrap.defaults"
) {
  if (is.null(defaults)) {
    return(list())
  }

  if (!is.list(defaults)) {
    abort("Invalid brand defaults in `", source, "`, must be a list.")
  }

  if (length(defaults) == 0) {
    return(list())
  }

  if (!all(nzchar(names2(defaults)))) {
    abort("Invalid brand defaults in `", source, "`, all values must be named.")
  }

  is_scalar <- function(v) {
    if (is.null(v)) {
      return(TRUE)
    }
    rlang::is_scalar_character(v) ||
      rlang::is_scalar_logical(v) ||
      rlang::is_scalar_double(v) ||
      rlang::is_scalar_integerish(v)
  }

  good <- vapply(defaults, is_scalar, logical(1))

  if (!all(good)) {
    abort(
      sprintf(
        "Invalid brand defaults in `%s`, all values must be scalar: %s",
        source,
        defaults[!good][1]
      )
    )
  }

  return(defaults)
}
