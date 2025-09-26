brand_color_normalize <- function(brand) {
  if (!brand_has(brand, "color")) {
    return(brand)
  }

  brand_color_check_fields(brand$color)

  # Pull out colors and resolve each color from original brand
  theme <- brand_pluck(brand, "color")

  for (field in names(brand_pluck(brand, "color"))) {
    if (field == "palette") {
      theme[[field]] <- lapply(
        rlang::set_names(names(theme[[field]])),
        brand_color_pluck,
        brand = brand
      )
    } else {
      theme[[field]] <- brand_color_pluck(brand, field)
    }
  }

  # Then replace brand.color with resolved colors
  brand[["color"]] <- theme
  brand
}

brand_color_check_fields <- function(color) {
  ptype <- list(palette = "list")
  for (theme_field in brand_color_fields_theme()) {
    ptype[[theme_field]] <- "string"
  }

  check_list(color, ptype, "color")

  if (!is.null(color$palette)) {
    check_is_list(color$palette, all_named = TRUE, arg = "color.palette")

    for (field in names(color$palette)) {
      check_string(
        color$palette[[field]],
        arg = sprintf("color.palette.%s", field)
      )
    }
  }
}

brand_color_fields_theme <- function() {
  c(
    "foreground",
    "background",
    "primary",
    "secondary",
    "tertiary",
    "success",
    "info",
    "warning",
    "danger",
    "light",
    "dark"
  )
}

#' Extract a color value from a brand object
#'
#' @description
#' Safely extracts a color value from a `brand` object based on the provided
#' key. This function handles color references and resolves them, including
#' references to palette colors and other theme colors. It detects and prevents
#' cyclic references.
#'
#' @details
#' The function checks for the color key in both the main color theme and the
#' color palette. It can resolve references between colors (e.g., if "primary"
#' references "palette.blue"). If a cyclic reference is detected (e.g., A
#' references B which references A), the function will throw an error.
#'
#' @examples
#' brand <- as_brand_yml(list(
#'   color = list(
#'     primary = "blue",
#'     secondary = "info",
#'     info = "light-blue",
#'     palette = list(
#'       blue = "#004488",
#'       light_blue = "#c3ddff"
#'     )
#'   )
#' ))
#'
#' # Extract the primary color
#' brand_color_pluck(brand, "primary") # "#004488"
#'
#' # Extract a color that references another color
#' brand_color_pluck(brand, "info") # "#c3ddff"
#'
#' # Extract a color that references another color
#' # which in turn references the palette
#' brand_color_pluck(brand, "secondary") # "#c3ddff"
#'
#' # Extract a color that isn't defined
#' brand_color_pluck(brand, "green") # "green"
#'
#' # Use brand_pluck() if you need direct (resolved) values
#' brand_pluck(brand, "color", "primary") # "#004488"
#' brand_pluck(brand, "color", "info") # "#c3ddff"
#' brand_pluck(brand, "color", "green") # NULL
#'
#' @inheritParams brand_has
#' @param key A character string representing the color key to extract.
#'
#' @return The resolved color value (typically a hex color code) if the key
#'   exists, otherwise returns the key itself.
#'
#' @family brand.yml helpers
#' @export
brand_color_pluck <- function(brand, key) {
  if (!brand_has(brand, "color")) {
    return(key)
  }

  theme_colors <- brand[["color"]]
  theme_colors$palette <- NULL
  palette <- brand[["color"]][["palette"]] %||% list()

  key_og <- key
  visited <- c()

  cycle <- function(key) {
    path <- c(visited, key)
    if (length(path) > 10) {
      path <- c(path[1:2], "...", path[-(1:(length(path) - 2))])
    }
    paste(path, collapse = " -> ")
  }

  assert_no_cycles <- function(key) {
    if (key %in% visited) {
      abort(
        c(
          sprintf(
            "Cyclic references detected in `brand.color` for color '%s'.",
            key_og
          ),
          "i" = cycle(key)
        )
      )
    }
    visited <<- c(visited, key)
  }

  check_string_or_null <- function(key, value) {
    if (is.null(value)) {
      return()
    }
    if (is_string(value)) {
      return(value)
    }

    abort(sprintf("`brand.color.%s` must be a string or `NULL`.", key))
  }

  p_key <- function(key) paste0("palette.", key)
  value <- ""
  i <- 0
  while (!identical(value, key)) {
    if (is.null(key) || is.null(value)) {
      return()
    }

    i <- i + 1
    if (i > 100) {
      abort(
        c(
          sprintf(
            "Max recursion limit reached while trying to resolve color '%s' using `brand.color`.",
            key_og
          ),
          i = cycle(key)
        )
      )
    }

    in_theme <- key %in% names(theme_colors)
    in_theme_unseen <- in_theme && !key %in% visited
    in_pal <- key %in% names(palette)

    if (in_pal && !in_theme_unseen) {
      # Prioritize palette if theme was already visited
      assert_no_cycles(p_key(key))
      key <- check_string_or_null(p_key(key), palette[[key]])
    } else if (in_theme) {
      assert_no_cycles(key)
      key <- check_string_or_null(key, theme_colors[[key]])
    } else {
      value <- key
    }
  }

  return(value)
}
