#' Generate Sass variables and CSS custom properties for brand color palette
#'
#' Converts color palette entries from a brand object to Sass variables with
#' `brand-` prefix and CSS custom properties with `--brand-` prefix.
#'
#' @examples
#' brand <- list(
#'   color = list(
#'     palette = list(
#'       primary = "#007bff",
#'       secondary = "#6c757d"
#'     )
#'   )
#' )
#'
#' brand_sass_color_palette(brand)
#'
#' @inheritParams as_brand_yml
#' @return A list with two components:
#'   * `defaults`: Sass variable definitions with `!default` flag
#'   * `rules`: CSS rules that define custom properties in `:root`
#'
#' @family brand.yml Sass helpers
#' @export
brand_sass_color_palette <- function(brand) {
  check_installed("htmltools")
  brand <- as_brand_yml(brand)

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

#' Generate Sass variables for brand colors
#'
#' Creates Sass variables for brand colors with the `brand_color_` prefix.
#' Excludes the color palette which is handled by `brand_sass_color_palette()`.
#'
#' @examples
#' brand <- list(
#'   color = list(
#'     primary = "#007bff",
#'     danger = "#dc3545"
#'   )
#' )
#'
#' brand_sass_color(brand)
#'
#' @inheritParams as_brand_yml
#' @return A list with one component:
#'   * `defaults`: Sass variable definitions with `!default` flag
#'
#' @family brand.yml Sass helpers
#' @export
brand_sass_color <- function(brand) {
  # Create brand Sass variables and set related Bootstrap Sass vars
  # brand.color.primary = "#007bff"
  # ==> $brand_color_primary: #007bff !default;
  # ==> $primary: $brand_color_primary !default;
  brand <- as_brand_yml(brand)

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

#' Generate Sass variables for brand typography
#'
#' Creates Sass variables for typography settings with the `brand_typography_` prefix.
#' Font size values in pixels are converted to rem units, and color references are resolved.
#'
#' @examples
#' brand <- list(
#'   typography = list(
#'     base = list(
#'       size = "16px",
#'       "line-height" = 1.5
#'     ),
#'     headings = list(
#'       weight = "bold",
#'       style = "normal"
#'     )
#'   )
#' )
#'
#' brand_sass_typography(brand)
#'
#' @inheritParams as_brand_yml
#' @return A list with one component:
#'   * `defaults`: Sass variable definitions with `!default` flag
#'
#' @family brand.yml Sass helpers
#' @export
brand_sass_typography <- function(brand) {
  brand <- as_brand_yml(brand)

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

#' Generate Sass variables and CSS rules for brand fonts
#'
#' Creates Sass variables and CSS rules for fonts defined in the brand object.
#' Supports Google fonts, Bunny fonts, and file-based fonts.
#'
#' @examplesIf requireNamespace("sass", quietly = TRUE)
#' brand <- list(
#'   typography = list(
#'     fonts = list(
#'       list(
#'         family = "Roboto",
#'         source = "google",
#'         weight = c(400, 700),
#'         style = "normal"
#'       )
#'     )
#'   )
#' )
#'
#' brand_sass_fonts(brand)
#'
#' @inheritParams as_brand_yml
#' @return A list with two components:
#'   * `defaults`: Sass variables for font definitions
#'   * `rules`: CSS rules for applying fonts via classes
#'
#' @family brand.yml Sass helpers
#' @export
brand_sass_fonts <- function(brand) {
  check_installed("sass")
  brand <- as_brand_yml(brand)

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

#' Generate Sass variables and layer for Bootstrap defaults
#'
#' Creates Sass variables and a sass layer from Bootstrap defaults defined in the brand object.
#' Allows overriding defaults from other sources like Shiny themes.
#'
#' @examplesIf requireNamespace("sass", quietly = TRUE)
#' brand <- list(
#'   defaults = list(
#'     bootstrap = list(
#'       defaults = list(
#'         primary = "#007bff",
#'         enable_rounded = TRUE
#'       ),
#'       functions = "@function brand-function() { @return true; }"
#'     ),
#'     shiny = list(
#'       theme = list(
#'         defaults = list(
#'           primary = "#428bca"  # Override bootstrap primary
#'         )
#'       )
#'     )
#'   )
#' )
#'
#' brand_sass_defaults_bootstrap(brand)
#'
#' @inheritParams as_brand_yml
#' @param overrides Path to override defaults, e.g., "shiny.theme"
#' @return A list with two components:
#'   * `defaults`: Sass variable definitions with `!default` flag
#'   * `layer`: A sass_layer object with functions, mixins, and rules
#'
#' @family brand.yml Sass helpers
#' @export
brand_sass_defaults_bootstrap <- function(brand, overrides = "shiny.theme") {
  check_installed("sass")
  brand <- as_brand_yml(brand)

  bootstrap <- brand_pluck(brand, "defaults", "bootstrap")

  if (!is.null(overrides)) {
    overrides_names <- paste0("defaults.", overrides)
    overrides_names <- sub(
      "defaults.defaults.",
      "defaults.",
      overrides_names,
      fixed = TRUE
    )
    overrides <- strsplit(overrides_names, ".", fixed = TRUE)
    overrides <- map(overrides, brand_pluck, brand = brand)
    for (i in seq_along(overrides)) {
      brand_validate_bootstrap_defaults(
        overrides[[i]]$defaults,
        overrides_names[[i]]
      )
    }
    overrides <- reduce(overrides, function(acc, x) {
      dots_list(!!!acc, !!!x, .homonyms = "last")
    })
  }

  has_overrides <- !is.null(overrides) && length(overrides) > 0

  if (is.null(bootstrap) && !has_overrides) {
    return(
      list(
        defaults = list(),
        layer = list()
      )
    )
  }

  bootstrap <- bootstrap %||% list()
  bootstrap_defaults <- brand_validate_bootstrap_defaults(bootstrap$defaults)

  defaults <- dots_list(
    !!!bootstrap_defaults,
    !!!overrides$defaults,
    .homonyms = "last"
  )
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
      functions = c(bootstrap$functions, overrides$functions),
      mixins = c(bootstrap$mixins, overrides$mixins),
      rules = c(bootstrap$rules, overrides$rules)
    )
  )
}
