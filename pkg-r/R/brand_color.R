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
  # Check for unexpected fields
  expected_fields <- c("palette", brand_color_fields_theme())
  actual_fields <- names(color)
  unexpected <- setdiff(actual_fields, expected_fields)
  if (length(unexpected) > 0) {
    abort(
      sprintf(
        "Unexpected fields in `color`: %s",
        paste(sprintf("'%s'", unexpected), collapse = ", ")
      )
    )
  }

  # Validate palette structure
  if (!is.null(color$palette)) {
    check_is_list(color$palette, arg = "color.palette")
  }

  # Validate each theme field separately (can be string or light/dark list)
  for (theme_field in brand_color_fields_theme()) {
    field_value <- color[[theme_field]]
    if (!is.null(field_value)) {
      check_string_or_list(
        field_value,
        allow_null = TRUE,
        arg = sprintf("color.%s", theme_field)
      )
    }
  }

  if (!is.null(color$palette)) {
    check_is_list(color$palette, all_named = TRUE, arg = "color.palette")

    for (field in names(color$palette)) {
      check_string(
        color$palette[[field]],
        arg = sprintf("color.palette.%s", field)
      )
    }
  }

  # Validate light/dark structures in theme colors
  for (theme_field in brand_color_fields_theme()) {
    if (is.list(color[[theme_field]])) {
      # If it's a list, it should have light and/or dark keys
      valid_keys <- c("light", "dark")
      actual_keys <- names(color[[theme_field]])

      if (!all(actual_keys %in% valid_keys)) {
        invalid_keys <- setdiff(actual_keys, valid_keys)
        abort(
          sprintf(
            "`brand.color.%s` has invalid keys: %s. Only 'light' and 'dark' are allowed.",
            theme_field,
            paste(sprintf("'%s'", invalid_keys), collapse = ", ")
          )
        )
      }

      if (length(actual_keys) == 0) {
        abort(
          sprintf(
            "`brand.color.%s` must have at least one of 'light' or 'dark' keys.",
            theme_field
          )
        )
      }

      # Check that light and dark values are strings
      for (variant in c("light", "dark")) {
        if (!is.null(color[[theme_field]][[variant]])) {
          if (!is_string(color[[theme_field]][[variant]])) {
            abort(
              sprintf(
                "`brand.color.%s.%s` must be a string.",
                theme_field,
                variant
              )
            )
          }
        }
      }
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
#' @param color_mode Which color mode to use when extracting colors with
#'   light/dark variants. Can be one of:
#'   * `"auto"` (default): Returns the full light/dark structure if present, or
#'     the scalar color otherwise.
#'   * `"light"`: Extracts the light mode value. If the color is a scalar, uses
#'     it as the light value.
#'   * `"dark"`: Extracts the dark mode value. If the color is a scalar, uses
#'     it as the light value.
#'   * `"light-dark"`: Returns a list with both `light` and `dark` values. If
#'     the color is scalar, returns it for both modes.
#'
#' @return The resolved color value. Depending on `color_mode`:
#'   * `"auto"`: a string or a list with `light` and `dark` elements
#'   * `"light"` or `"dark"`: a string
#'   * `"light-dark"`: a list with `light` and `dark` elements
#'   Returns the key itself if the color doesn't exist.
#'
#' @family brand.yml helpers
#' @export
brand_color_pluck <- function(
  brand,
  key,
  color_mode = c("auto", "light", "dark", "light-dark")
) {
  color_mode <- arg_match(color_mode)

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
      theme_value <- theme_colors[[key]]

      # Handle light/dark structures
      if (is.list(theme_value) && any(names(theme_value) %in% c("light", "dark"))) {
        # It's a light/dark structure, resolve each variant
        resolved <- list()
        if (!is.null(theme_value$light)) {
          resolved$light <- brand_color_pluck(brand, theme_value$light, color_mode = "auto")
        }
        if (!is.null(theme_value$dark)) {
          resolved$dark <- brand_color_pluck(brand, theme_value$dark, color_mode = "auto")
        }

        # Apply color_mode to the resolved light/dark structure
        value <- brand_color_apply_mode(resolved, color_mode)
        return(value)
      } else {
        # It's a string reference, continue resolving
        key <- check_string_or_null(key, theme_value)
      }
    } else {
      value <- key
    }
  }

  # Apply color_mode to scalar value
  brand_color_apply_mode(value, color_mode)
}

# Helper function to apply color_mode to a resolved value
brand_color_apply_mode <- function(value, color_mode) {
  # If value is a light/dark structure (list with light/dark keys)
  is_light_dark <- is.list(value) && any(names(value) %in% c("light", "dark"))

  if (is_light_dark) {
    if (color_mode == "auto") {
      # Return as-is
      return(as_light_dark(value$light, value$dark))
    } else if (color_mode == "light") {
      # Return light value, or dark as fallback if light is NULL
      return(value$light %||% value$dark)
    } else if (color_mode == "dark") {
      # Return dark value, or light as fallback if dark is NULL
      return(value$dark %||% value$light)
    } else if (color_mode == "light-dark") {
      # Return both
      return(as_light_dark(value$light, value$dark))
    }
  } else {
    # Scalar value
    if (color_mode == "auto") {
      return(value)
    } else if (color_mode == "light") {
      return(value)
    } else if (color_mode == "dark") {
      return(value)
    } else if (color_mode == "light-dark") {
      # Promote scalar to light/dark
      return(as_light_dark(value, value))
    }
  }

  value
}
