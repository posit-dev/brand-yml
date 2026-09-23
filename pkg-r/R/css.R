#' Generate mode-aware CSS custom properties from a brand
#'
#' Emits brand-owned CSS custom properties for palette colors, theme colors,
#' and typography color fields. Light and dark values are emitted under
#' configurable CSS scopes. A value that is undefined in one mode is omitted
#' from that scope so a consuming framework can retain its base value.
#'
#' @param brand A brand object, YAML string, or path accepted by
#'   [as_brand_yml()].
#' @param mode_scopes A named list with `light` and `dark` values. An empty
#'   string emits variables under `:root`. `"prefers-color-scheme"` emits a
#'   matching media query. Any other value is used as a CSS selector.
#'
#' @return A string containing CSS rules.
#' @export
brand_css_variables <- function(
  brand,
  mode_scopes = list(
    light = "",
    dark = "prefers-color-scheme"
  )
) {
  brand <- as_brand_yml(brand)
  brand_css_check_mode_scopes(mode_scopes)

  blocks <- lapply(c("light", "dark"), function(mode) {
    declarations <- brand_css_declarations(brand, mode)
    brand_css_scope(declarations, mode_scopes[[mode]], mode)
  })

  paste(unlist(blocks), collapse = "\n")
}

brand_css_check_mode_scopes <- function(mode_scopes) {
  check_is_list(mode_scopes, all_named = TRUE, arg = "mode_scopes")

  if (!setequal(names(mode_scopes), c("light", "dark"))) {
    cli::cli_abort(
      "{.arg mode_scopes} must contain exactly {.val light} and {.val dark}."
    )
  }

  for (mode in c("light", "dark")) {
    check_string(mode_scopes[[mode]], arg = paste0("mode_scopes.", mode))
  }
}

brand_css_declarations <- function(brand, mode) {
  declarations <- character()
  palette <- brand_pluck(brand, "color", "palette") %||% list()

  for (name in names(palette)) {
    declarations[[paste0("--brand-", name)]] <- palette[[name]]
  }

  for (name in brand_color_fields_theme()) {
    value <- brand_color_pluck(brand, name, color_mode = mode)
    if (!is.null(value) && !identical(value, name)) {
      declarations[[paste0("--brand-color-", name)]] <- value
    }
  }

  typography <- brand_pluck(brand, "typography") %||% list()
  for (field in setdiff(names(typography), "fonts")) {
    for (property in c("color", "background_color")) {
      value <- typography[[field]][[property]]
      if (is.null(value)) {
        next
      }
      property_css <- gsub("_", "-", property)
      variable <- paste(
        "--brand-typography",
        gsub("_", "-", field),
        property_css,
        sep = "-"
      )
      value <- brand_color_select(value, mode)
      if (!is.null(value)) {
        declarations[[variable]] <- value
      }
    }
  }

  sprintf("  %s: %s;", names(declarations), unname(declarations))
}

brand_css_scope <- function(declarations, scope, mode) {
  selector <- if (scope %in% c("", "prefers-color-scheme")) {
    ":root"
  } else {
    scope
  }
  block <- c(paste0(selector, " {"), declarations, "}")

  if (scope != "prefers-color-scheme") {
    return(block)
  }

  c(
    sprintf("@media (prefers-color-scheme: %s) {", mode),
    paste0("  ", block),
    "}"
  )
}
