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

list_merge <- function(x, y) {
  if (rlang::is_empty(y)) {
    return(x)
  }
  if (rlang::is_empty(x)) {
    return(y)
  }

  x_names <- rlang::names2(x)
  y_names <- rlang::names2(y)

  for (i in seq_along(y)) {
    y_nm <- y_names[i]

    # Handle unnamed elements by position
    if (y_nm == "") {
      x <- c(x, list(y[[i]]))
      next
    }

    both_lists <- rlang::is_list(x[[y_nm]]) && rlang::is_list(y[[i]])

    # If item exists in x and both values are lists, recurse
    if (y_nm %in% x_names && both_lists) {
      x[[y_nm]] <- list_merge(x[[y_nm]], y[[i]])
    } else {
      # Otherwise, overwrite or add
      x[[y_nm]] <- y[[i]]
    }
  }

  return(x)
}

list_restyle_names <- function(x, style = c("snake", "kebab")) {
  style <- arg_match(style)

  if (inherits(x, c("brand_yml", "list"))) {
    if (!is.null(names(x))) {
      new_names <- switch(
        style,
        snake = as_snake_case(names(x)),
        kebab = as_kebab_case(names(x))
      )
      is_conflicted <-
        (new_names %in% names(x)) | # skip unchanged names
        (names(x) %in% names(x)[duplicated(names(x))]) | # skip original duplicates
        new_names %in% new_names[duplicated(new_names)] # skip would-be duplicates
      names(x)[!is_conflicted] <- new_names[!is_conflicted]
    }
    x <- map(x, list_restyle_names, style)
  }
  return(x)
}

as_snake_case <- function(x) gsub("-", "_", x)
as_kebab_case <- function(x) gsub("_", "-", x)

paste. <- function(...) {
  paste(c(...), collapse = ".")
}

read_yaml <- function(path) {
  yaml::read_yaml(path, eval.expr = FALSE, readLines.warn = FALSE)
}
