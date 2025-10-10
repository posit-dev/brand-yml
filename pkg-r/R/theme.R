#' Create a ggplot2 theme using brand colors
#'
#' Create a ggplot2 theme using explicit colors or by automatically extracting
#' colors from a **brand.yml** file.
#'
#' @section Branded Theming:
#' The `theme_brand_*` functions can be used in two ways:
#'
#' 1. **With a brand.yml file**: The `theme_brand_*` functions use
#'    [read_brand_yml()] to automatically detect and use a `_brand.yml` file in
#'    your current project. You can also explicitly pass a path to a brand.yml
#'    file or a brand object (as returned by [read_brand_yml()] or created with
#'    [as_brand_yml()]). When a `brand` is provided, the theme functions will
#'    use the colors defined in the brand file automatically.
#'
#' 2. **With explicit colors**: You can directly provide colors to override the
#'    default brand colors, or you can use `brand = FALSE` to ignore any project
#'    `_brand.yml` files and only use the explicitly provided colors.
#'
#' @examplesIf rlang::is_installed("ggplot2")
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' library(ggplot2)
#' ggplot(diamonds, aes(carat, price)) +
#'   geom_point() +
#'   theme_brand_ggplot2(brand)
#'
#' @param brand One of:
#'   - `NULL` (default): Automatically detect and read a _brand.yml file
#'   - A path to a brand.yml file or directory containing _brand.yml
#'   - A brand object (as returned by `read_brand_yml()` or `as_brand_yml()`)
#'   - `FALSE`: Don't use a brand file; explicit colors must be provided
#' @param background The background color, defaults to `brand.color.background`.
#'   If provided directly, this value can be a valid R color or the name of a
#'   color in `brand.color` or `brand.color.palette`.
#' @param foreground The foreground color, defaults to `brand.color.foreground`.
#'   If provided directly, this value can be a valid R color or the name of a
#'   color in `brand.color` or `brand.color.palette`.
#' @param accent The accent color, defaults to `brand.color.primary` or
#'   `brand.color.palette.accent`. If provided directly, this value can be a
#'   valid R color or the name of a color in `brand.color` or
#'   `brand.color.palette`.
#'
#' @return A [ggplot2::theme()] object.
#'
#' @family branded theming functions
#'
#' @export
theme_brand_ggplot2 <- function(
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL
) {
  check_installed("ggplot2", version = "4.0.0")

  brand <- resolve_brand_yml(brand)

  bg_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  fg_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")
  accent_color <- brand_color_maybe_pluck(brand, accent, "accent", "primary")

  # Create and return the theme directly
  ggplot2::theme_minimal(base_size = 11, accent = accent_color) +
    ggplot2::theme(
      panel.border = ggplot2::element_blank(),
      panel.grid.major.y = ggplot2::element_blank(),
      panel.grid.minor.y = ggplot2::element_blank(),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor.x = ggplot2::element_blank(),
      text = ggplot2::element_text(colour = fg_color),
      axis.text = ggplot2::element_text(colour = fg_color),
      rect = ggplot2::element_rect(colour = bg_color, fill = bg_color),
      plot.background = ggplot2::element_rect(fill = bg_color, colour = NA),
      axis.line = ggplot2::element_line(colour = fg_color),
      axis.ticks = ggplot2::element_line(colour = fg_color)
    )
}


#' Create a thematic theme using brand colors
#'
#' Apply thematic styling using explicit colors or by automatically extracting
#' colors from a **brand.yml** file. This function sets global theming for base
#' R graphics.
#'
#' @examplesIf rlang::is_installed("thematic") && rlang::is_installed("ggplot2")
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' thematic::thematic_with_theme(theme_brand_thematic(brand), {
#'   library(ggplot2)
#'   ggplot(diamonds, aes(carat, price)) +
#'     geom_point()
#' })
#'
#' @inheritParams theme_brand_ggplot2
#'
#' @seealso See the "Branded Theming" section of [theme_brand_ggplot2()] for
#'   more details on how the `brand` argument works.
#' @family branded theming functions
#'
#' @export
theme_brand_thematic <- function(
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL
) {
  check_installed("thematic")

  brand <- resolve_brand_yml(brand)

  bg_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  fg_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")
  accent_color <- brand_color_maybe_pluck(brand, accent, "accent", "primary")

  "light-dark"
  thematic::thematic_on(
    bg = bg_color,
    fg = fg_color,
    accent = accent_color
  )
}


#' Create a flextable theme using brand colors
#'
#' Apply brand colors to a flextable table.
#'
#' @examplesIf rlang::is_installed("flextable") && getRversion() >= "4.5"
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' library(flextable)
#' theme_brand_flextable(
#'   flextable(head(palmerpenguins::penguins)),
#'   brand
#' )
#'
#' @examplesIf rlang::is_installed("flextable") && getRversion() < "4.5"
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' library(flextable)
#' theme_brand_flextable(
#'   flextable(head(mtcars)),
#'   brand
#' )
#'
#' @param table A flextable object to theme.
#' @inheritParams theme_brand_ggplot2
#'
#' @return Returns a themed flextable object.
#'
#' @inherit theme_brand_thematic seealso
#' @family branded theming functions
#'
#' @export
theme_brand_flextable <- function(
  table,
  brand = NULL,
  background = NULL,
  foreground = NULL
) {
  check_installed("flextable")
  if (!inherits(table, "flextable")) {
    cli::cli_abort(
      "{.var table} must be a flextable object, not {.obj_type_friendly {table}}."
    )
  }

  brand <- resolve_brand_yml(brand)

  bg_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  fg_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")

  table <- flextable::bg(table, bg = bg_color, part = "all")
  table <- flextable::color(table, color = fg_color, part = "all")
  flextable::autofit(table)
}


#' Create a gt table theme using brand colors
#'
#' Apply brand colors to a gt table.
#'
#' @examplesIf rlang::is_installed("gt") && getRversion() >= "4.5"
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' library(gt)
#' theme_brand_gt(
#'   gt(head(palmerpenguins::penguins)),
#'   brand
#' )
#'
#' @examplesIf rlang::is_installed("gt") && getRversion() < "4.5"
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' library(gt)
#' theme_brand_gt(
#'   gt(head(mtcars)),
#'   brand
#' )
#'
#' @param table A gt table object to theme.
#' @inheritParams theme_brand_ggplot2
#'
#' @return Returns a themed gt table object.
#'
#' @inherit theme_brand_thematic seealso
#' @family branded theming functions
#' @export
theme_brand_gt <- function(
  table,
  brand = NULL,
  background = NULL,
  foreground = NULL
) {
  check_installed("gt")
  if (!inherits(table, "gt_tbl")) {
    cli::cli_abort(
      "{.var table} must be a gt table object, not {.obj_type_friendly {table}}."
    )
  }

  brand <- resolve_brand_yml(brand)

  bg_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  fg_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")

  gt::tab_options(
    table,
    table.background.color = bg_color,
    table.font.color = fg_color
  )
}


#' Create a plotly theme using brand colors
#'
#' Apply brand colors to a plotly plot.
#'
#' @examplesIf rlang::is_installed("plotly") && getRversion() >= "4.5"
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' library(plotly)
#' plot_ly(palmerpenguins::penguins, x = ~bill_length_mm, y = ~bill_depth_mm) |>
#'   theme_brand_plotly(brand)
#'
#' @examplesIf rlang::is_installed("plotly") && getRversion() < "4.5"
#' brand <- as_brand_yml('
#' color:
#'   palette:
#'     black: "#1A1A1A"
#'     white: "#F9F9F9"
#'     orange: "#FF6F20"
#'   foreground: black
#'   background: white
#'   primary: orange')
#'
#' library(plotly)
#' plot_ly(mtcars, x = ~wt, y = ~mpg) |>
#'   theme_brand_plotly(brand)
#'
#' @param plot A plotly plot object to theme.
#' @inheritParams theme_brand_ggplot2
#'
#' @return Returns a themed plotly plot object.
#'
#' @inherit theme_brand_thematic seealso
#' @family branded theming functions
#' @export
theme_brand_plotly <- function(
  plot,
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL
) {
  check_installed("plotly")
  if (!inherits(plot, "plotly")) {
    cli::cli_abort(
      "{.var plot} must be a plotly object, not {.obj_type_friendly {plot}}."
    )
  }

  brand <- resolve_brand_yml(brand)

  bg_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  fg_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")
  accent_color <- brand_color_maybe_pluck(brand, accent, "accent", "primary")

  plot <- plotly::layout(
    plot,
    paper_bgcolor = bg_color,
    plot_bgcolor = bg_color,
    font = list(color = fg_color)
  )

  if (!is.null(accent_color)) {
    plot <- plotly::layout(
      plot,
      colorway = rep(accent_color, 10)
    )
  }

  plot
}

# Helpers ---------------------------------------------------------------------

brand_color_maybe_pluck <- function(brand, value, ...) {
  # Try brand color directly
  color <- brand_pluck(brand, "color", value)
  if (!is.null(color)) {
    return(color)
  }

  # Try brand color palette
  color <- brand_pluck(brand, "color", "palette", value)
  if (!is.null(color)) {
    return(color)
  }

  # Use explicit value if provided
  if (!is.null(value)) {
    return(value)
  }

  # Try fallback keys
  for (key in c(...)) {
    color <- brand_color_pluck(brand, key)
    if (!is.null(color) && !identical(color, key)) {
      return(color)
    }
  }

  NULL
}
