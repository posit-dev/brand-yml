brand_sass_color_palette <- function(brand) {
  check_installed("htmltools")

  palette <- brand_pluck(brand, "color", "palette")

  if (is.null(palette)) {
    return(list(defaults = list(), rules = list()))
  }

  # Resolve internal references in colors
  palette <- lapply(
    rlang::set_names(names(palette)),
    brand_color_pluck,
    brand = brand
  )

  defaults <- palette
  defaults <- lapply(defaults, paste, "!default")
  names(defaults) <- sprintf("brand-%s", names(defaults))

  for (color in intersect(names(palette), bootstrap_colors)) {
    defaults[color] <- sprintf("$brand-%s !default", color)
  }

  css_vars <- palette
  names(css_vars) <- sprintf("--brand-%s", names(css_vars))
  rules <- sprintf(":root { %s }", htmltools::css(!!!css_vars))

  list(
    defaults = defaults,
    rules = rules
  )
}

bootstrap_colors <- c(
  "white",
  "black",
  "blue",
  "indigo",
  "purple",
  "pink",
  "red",
  "orange",
  "yellow",
  "green",
  "teal",
  "cyan"
)

brand_sass_color <- function(brand) {
  # Create brand Sass variables and set related Bootstrap Sass vars
  # brand.color.primary = "#007bff"
  # ==> $brand_color_primary: #007bff !default;
  # ==> $primary: $brand_color_primary !default;

  colors <- brand_pluck(brand, "color") %||% list()
  colors$palette <- NULL

  if (length(colors) == 0) {
    return(list())
  }

  # Resolve internal references in colors
  colors <- lapply(
    rlang::set_names(names(colors)),
    brand_color_pluck,
    brand = brand
  )

  defaults <- list()
  for (thm_name in names(colors)) {
    brand_color_var <- sprintf("brand_color_%s", thm_name)
    defaults[[brand_color_var]] <- paste(colors[[thm_name]], "!default")
  }

  list(defaults = defaults)
}

brand_sass_typography <- function(brand) {
  # Creates a dictionary of Sass variables for typography settings defined in
  # the `brand` object. These are used to set brand Sass variables in the format
  # `$brand_typography_{field}_{prop}`.
  typography <- brand_pluck(brand, "typography")

  if (is.null(typography)) {
    return(list(defaults = list()))
  }

  defaults <- list()

  for (field in names(typography)) {
    if (field == "fonts") {
      next
    }

    prop <- typography[[field]]
    for (prop_key in names(prop)) {
      prop_value <- prop[[prop_key]]
      if (field == "base" && prop_key == "size") {
        prop_value <- maybe_convert_font_size_to_rem(prop_value)
      } else if (prop_key %in% c("color", "background-color")) {
        prop_value <- brand_color_pluck(brand, prop_value)
      }
      field <- gsub("-", "_", field)
      prop_key <- gsub("-", "_", prop_key)
      typo_sass_var <- paste("brand_typography", field, prop_key, sep = "_")
      defaults[[typo_sass_var]] <- paste(prop_value, "!default")
    }
  }

  list(defaults = defaults)
}

brand_sass_fonts <- function(brand) {
  check_installed("sass")

  fonts <- brand_pluck(brand, "typography", "fonts")

  if (is.null(fonts)) {
    return(list(defaults = list(), rules = list()))
  }

  defaults <- list()
  rules <- list()

  for (font in fonts) {
    var_name <- sprintf(
      "brand-font-%s",
      gsub("[^a-z0-9-]+", "-", tolower(font$family))
    )

    font_obj <- switch(
      font$source %||% "google",
      google = sass::font_google(
        family = font$family,
        wght = brand_remap_font_weight(font$weight) %||%
          seq(100, 900, by = 100),
        ital = c("normal" = 0, "italic" = 1)[
          font$style %||% c("normal", "italic")
        ],
        display = font$display %||% "auto"
      ),
      bunny = brand_font_bunny(
        family = font$family,
        weight = font$weight,
        style = font$style,
        display = font$display
      ),
      file = brand_font_file(
        family = font$family,
        files = font$files,
        brand_root = dirname(brand$path)
      ),
      system = NULL,
      abort(sprintf("Unknown font source '%s'.", font$source))
    )

    if (!is.null(font_obj)) {
      defaults[[var_name]] <- font_obj
      rules <- c(
        rules,
        sprintf(".%s { font-family: $%s; }", var_name, var_name)
      )
    }
  }

  list(defaults = defaults, rules = rules)
}

brand_sass_defaults_bootstrap <- function(brand) {
  check_installed("sass")

  bootstrap <- brand_pluck(brand, "defaults", "bootstrap")
  shiny <- brand_pluck(brand, "defaults", "shiny", "theme")

  if (is.null(bootstrap) && is.null(shiny))
    return(
      list(
        defaults = list(),
        layer = list()
      )
    )

  shiny <- shiny %||% list()
  shiny_defaults <- brand_validate_bootstrap_defaults(
    shiny$defaults,
    "brand.defaults.shiny.theme"
  )

  bootstrap <- bootstrap %||% list()
  bootstrap_defaults <- brand_validate_bootstrap_defaults(bootstrap$defaults)

  defaults <- list2(!!!bootstrap_defaults, !!!shiny_defaults)
  defaults <- lapply(defaults, function(x) {
    if (is.null(x)) {
      x <- "null"
    } else if (is.logical(x)) {
      x <- tolower(as.character(x))
    }
    paste(x, "!default")
  })

  list(
    defaults = defaults,
    layer = sass::sass_layer(
      functions = c(bootstrap$functions, shiny$functions),
      mixins = c(bootstrap$mixins, shiny$mixins),
      rules = c(bootstrap$rules, shiny$rules)
    )
  )
}
