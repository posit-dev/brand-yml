#' Create a theme for a plotting or table package
#'
#' Create a theme using background and foreground colors (`theme_colors_*`) or
#' using a **brand.yml** file (`theme_brand_*`).
#'
#' The use of the theme will depend on the package. Please see
#' [light/dark renderings examples](https://examples.quarto.pub/lightdark-renderings-examples/ggplot2.html)
#' for examples using each supported package with dark mode, `theme_brand_*`,
#' and `renderings: [light, dark]`,
#' or [theme helper article](https://quarto-dev.github.io/quarto-r/articles/theme-helpers.html)
#' for examples using each package and `theme_colors_*` to specify the
#' background and foreground colors directly.
#'
#' The `theme_brand_*` functions use the brand.yml package to parse brand.yml files
#' and extract the appropriate color values for theming.
#'
#' @param bg The background color
#' @param fg The foreground color
#' @param accent The accent color for plots and visualizations (default: same as foreground color)
#' @param brand_yml The path to a brand.yml file or directory containing a _brand.yml file

#' @rdname theme_helpers
#'
#' @export
theme_colors_flextable <- function(bg, fg) {
  rlang::check_installed(
    "flextable",
    "flextable is required for theme_colors_flextable"
  )
  (function(x) {
    if (!inherits(x, "flextable")) {
      stop("theme_colors_flextable only supports flextable objects.")
    }
    x <- flextable::bg(x, bg = bg, part = "all")
    x <- flextable::color(x, color = fg, part = "all")
    flextable::autofit(x)
  })
}

#' @rdname theme_helpers
#' @family brand.yml helpers
#'
#' @export
theme_brand_flextable <- function(brand_yml) {
  rlang::check_installed(
    "brand.yml",
    "brand.yml is required for brand support in R"
  )
  brand <- brand.yml::read_brand_yml(brand_yml)
  bg_color <- brand.yml::brand_color_pluck(brand, "background")
  fg_color <- brand.yml::brand_color_pluck(brand, "foreground")
  theme_colors_flextable(bg_color, fg_color)
}


#' @rdname theme_helpers
#'
#' @export
theme_colors_ggplot2 <- function(bg, fg, accent = NULL) {
  rlang::check_installed(
    "ggplot2",
    "ggplot2 v4.0 or later is required for theme_colors_ggplot2",
    version = "4.0.0"
  )

  # Create and return the theme directly
  ggplot2::theme_minimal(base_size = 11, accent = accent) +
    ggplot2::theme(
      panel.border = ggplot2::element_blank(),
      panel.grid.major.y = ggplot2::element_blank(),
      panel.grid.minor.y = ggplot2::element_blank(),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor.x = ggplot2::element_blank(),
      text = ggplot2::element_text(colour = fg),
      axis.text = ggplot2::element_text(colour = fg),
      rect = ggplot2::element_rect(colour = bg, fill = bg),
      plot.background = ggplot2::element_rect(fill = bg, colour = NA),
      axis.line = ggplot2::element_line(colour = fg),
      axis.ticks = ggplot2::element_line(colour = fg)
    )
}

#' @rdname theme_helpers
#' @family brand.yml helpers
#'
#' @export
theme_brand_ggplot2 <- function(brand_yml) {
  rlang::check_installed(
    "brand.yml",
    "brand.yml is required for brand support in R"
  )
  brand <- brand.yml::read_brand_yml(brand_yml)
  bg_color <- brand.yml::brand_color_pluck(brand, "background")
  fg_color <- brand.yml::brand_color_pluck(brand, "foreground")

  accent_color <- brand.yml::brand_color_pluck(brand, "accent")
  if (identical(accent_color, "accent")) {
    accent_color <- brand.yml::brand_color_pluck(brand, "primary")
    if (identical(accent_color, "primary")) {
      accent_color <- NULL
    }
  }

  theme_colors_ggplot2(bg_color, fg_color, accent_color)
}


#' @rdname theme_helpers
#'
#' @export
theme_colors_gt <- function(bg, fg) {
  rlang::check_installed(
    "gt",
    "gt is required for theme_colors_gt"
  )
  (function(table) {
    table |>
      gt::tab_options(
        table.background.color = bg,
        table.font.color = fg,
      )
  })
}

#' @rdname theme_helpers
#' @family brand.yml helpers
#'
#' @export
theme_brand_gt <- function(brand_yml) {
  rlang::check_installed(
    "brand.yml",
    "brand.yml is required for brand support in R"
  )
  brand <- brand.yml::read_brand_yml(brand_yml)
  bg_color <- brand.yml::brand_color_pluck(brand, "background")
  fg_color <- brand.yml::brand_color_pluck(brand, "foreground")
  theme_colors_gt(bg_color, fg_color)
}

#' @rdname theme_helpers
#'
#' @export
theme_colors_plotly <- function(bg, fg, accent = NULL) {
  rlang::check_installed(
    "plotly",
    "plotly is required for theme_colors_plotly"
  )
  (function(plot) {
    plot <- plot |> plotly::layout(
      paper_bgcolor = bg,
      plot_bgcolor = bg,
      font = list(color = fg)
    )

    if (!is.null(accent)) {
      plot <- plot |> plotly::layout(
        colorway = rep(accent, 10)
      )
    }

    plot
  })
}

#' @rdname theme_helpers
#' @family brand.yml helpers
#'
#' @export
theme_brand_plotly <- function(brand_yml) {
  rlang::check_installed(
    "brand.yml",
    "brand.yml is required for brand support in R"
  )
  brand <- brand.yml::read_brand_yml(brand_yml)
  bg_color <- brand.yml::brand_color_pluck(brand, "background")
  fg_color <- brand.yml::brand_color_pluck(brand, "foreground")

  accent_color <- brand.yml::brand_color_pluck(brand, "accent")
  if (identical(accent_color, "accent")) {
    accent_color <- brand.yml::brand_color_pluck(brand, "primary")
    if (identical(accent_color, "primary")) {
      accent_color <- NULL
    }
  }

  theme_colors_plotly(bg_color, fg_color, accent_color)
}


#' @rdname theme_helpers
#'
#' @export
theme_colors_thematic <- function(bg, fg, accent = NULL) {
  rlang::check_installed(
    "thematic",
    "thematic is required for theme_colors_thematic"
  )
  (function() {
    thematic::thematic_on(
      bg = bg,
      fg = fg,
      accent = accent
    )
  })
}

#' @rdname theme_helpers
#' @family brand.yml helpers
#'
#' @export
theme_brand_thematic <- function(brand_yml) {
  rlang::check_installed(
    "brand.yml",
    "brand.yml is required for brand support in R"
  )
  brand <- brand.yml::read_brand_yml(brand_yml)
  bg_color <- brand.yml::brand_color_pluck(brand, "background")
  fg_color <- brand.yml::brand_color_pluck(brand, "foreground")

  accent_color <- brand.yml::brand_color_pluck(brand, "accent")
  if (identical(accent_color, "accent")) {
    accent_color <- brand.yml::brand_color_pluck(brand, "primary")
    if (identical(accent_color, "primary")) {
      accent_color <- NULL
    }
  }

  theme_colors_thematic(bg_color, fg_color, accent_color)
}
