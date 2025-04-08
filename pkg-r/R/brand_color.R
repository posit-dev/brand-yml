brand_color_normalize <- function(brand) {
  if (!brand_has(brand, "color")) {
    return(brand)
  }

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
    if (is.null(value)) return()
    if (is_string(value)) return(value)

    abort(sprintf("`brand.color.%s` must be a string or `NULL`.", key))
  }

  p_key <- function(key) paste0("palette.", key)
  value <- ""
  i <- 0
  while (!identical(value, key)) {
    if (is.null(key) || is.null(value)) return()

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
