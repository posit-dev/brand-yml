`%??%` <- function(x, y) {
  if (!is.null(x)) y
}


#' Convert a font size to rem
#'
#' Some frameworks, like Bootstrap expect base font size to be in `rem`. This
#' function converts `em`, `%`, `px`, `pt` to `rem`:
#'
#' 1. `em` is directly replace with `rem`.
#' 2. `1%` is `0.01rem`, e.g. `90%` becomes `0.9rem`.
#' 3. `16px` is `1rem`, e.g. `18px` becomes `1.125rem`.
#' 4. `12pt` is `1rem`.
#' 5. `0.1666in` is `1rem`.
#' 6. `4.234cm` is `1rem`.
#' 7. `42.3mm` is `1rem`.
#'
#' @noRd
maybe_convert_font_size_to_rem <- function(x) {
  x_og <- as.character(x)
  split_result <- split_css_value_and_unit(x)
  value <- split_result$value
  unit <- split_result$unit

  if (unit %in% c("rem", "em")) {
    return(paste0(value, "rem"))
  }

  scale <- list(
    "%" = 100,
    "px" = 16,
    "pt" = 12,
    "in" = 16 / 96, # 96 px/inch
    "cm" = 16 / 96 * 2.54, # inch -> cm
    "mm" = 16 / 96 * 25.4 # cm -> mm
  )

  if (unit %in% names(scale)) {
    return(paste0(as.numeric(value) / scale[[unit]], "rem"))
  }

  if (unit == "") {
    unit <- "unknown"
  }

  abort(
    sprintf(
      "Could not convert font size '%s' from %s units to a relative unit.",
      x_og,
      unit
    )
  )
}

split_css_value_and_unit <- function(x) {
  x <- trimws(x)
  pattern <- "^(-?[0-9]*\\.?[0-9]+)\\s*([a-z%]*)$"
  match <- regexec(pattern, x)
  result <- regmatches(x, match)[[1]]

  if (length(result) != 3) {
    abort(paste0("Invalid CSS value format: ", x))
  }

  return(list(value = result[2], unit = result[3]))
}
