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
#' @param ... Reserved for future use.
#' @param base_size Base font size in points. Used for the `size` property of
#'   [ggplot2::element_text()] in the `text` theme element.
#' @param title_size Title font size in points. Used for the `size` property of
#'   [ggplot2::element_text()] in the `title` theme element. Defaults to
#'   `base_size * 1.2`.
#' @param title_color, Color for the `color` property of
#'   [ggplot2::element_text()] in the `title` theme element. Can be a valid R
#'   color or the name of a color in `brand.color` or `brand.color.palette`. If
#'   not provided, defaults to the `foreground` color.
#' @param line_color Color for the `color` property of [ggplot2::element_line()]
#'   in the `line` theme element. Can be a valid R color or the name of a color
#'   in `brand.color` or `brand.color.palette`. If not provided, defaults to a
#'   blend of foreground and background colors.
#' @param rect_fill Fill color for the `fill` property of
#'   [ggplot2::element_rect()] in the `rect` theme element. Can be a valid R
#'   color or the name of a color in `brand.color` or `brand.color.palette`. If
#'   not provided, defaults to the background color.
#' @param text_color Color for the `color` property of [ggplot2::element_text()]
#'   in the `text` theme element. Can be a valid R color or the name of a color
#'   in `brand.color` or `brand.color.palette`. If not provided, defaults to a
#'   blend of foreground and background colors.
#' @param plot_background_fill Fill color for the `fill` property of
#'   [ggplot2::element_rect()] in the `plot.background` theme element. Can be a
#'   valid R color or the name of a color in `brand.color` or
#'   `brand.color.palette`. If not provided, defaults to the background color.
#' @param panel_background_fill Fill color for the `fill` property of
#'   [ggplot2::element_rect()] in the `panel.background` theme element. Can be a
#'   valid R color or the name of a color in `brand.color` or
#'   `brand.color.palette`. If not provided, defaults to the background color.
#' @param panel_grid_major_color Color for the `color` property of
#'   [ggplot2::element_line()] in the `panel.grid.major` theme element. Can be a
#'   valid R color or the name of a color in `brand.color` or
#'   `brand.color.palette`. If not provided, defaults to a blend of foreground
#'   and background colors.
#' @param panel_grid_minor_color Color for the `color` property of
#'   [ggplot2::element_line()] in the `panel.grid.minor` theme element. Can be a
#'   valid R color or the name of a color in `brand.color` or
#'   `brand.color.palette`. If not provided, defaults to a blend of foreground
#'   and background colors.
#' @param axis_text_color Color for the `color` property of
#'   [ggplot2::element_text()] in the `axis.text` theme element. Can be a valid
#'   R color or the name of a color in `brand.color` or `brand.color.palette`.
#'   If not provided, defaults to a blend of foreground and background colors.
#' @param plot_caption_color Color for the `color` property of
#'   [ggplot2::element_text()] in the `plot.caption` theme element. Can be a
#'   valid R color or the name of a color in `brand.color` or
#'   `brand.color.palette`. If not provided, defaults to a blend of foreground
#'   and background colors.
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
  accent = NULL,
  ...,
  base_size = 11,
  title_size = base_size * 1.2,
  title_color = NULL,
  line_color = NULL,
  rect_fill = NULL,
  text_color = NULL,
  plot_background_fill = NULL,
  panel_background_fill = NULL,
  panel_grid_major_color = NULL,
  panel_grid_minor_color = NULL,
  axis_text_color = NULL,
  plot_caption_color = NULL
) {
  check_installed("ggplot2")
  check_installed("prismatic")

  brand <- resolve_brand_yml(brand)

  # fmt: skip
  {
  background_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  foreground_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")
  accent_color     <- brand_color_maybe_pluck(brand, accent, "accent", "primary")
  title_color      <- brand_color_maybe_pluck(brand, title_color)
  line_color       <- brand_color_maybe_pluck(brand, line_color)
  rect_fill        <- brand_color_maybe_pluck(brand, rect_fill)
  text_color       <- brand_color_maybe_pluck(brand, text_color)
  plot_background_fill   <- brand_color_maybe_pluck(brand, plot_background_fill)
  panel_background_fill  <- brand_color_maybe_pluck(brand, panel_background_fill)
  panel_grid_major_color <- brand_color_maybe_pluck(brand, panel_grid_major_color)
  panel_grid_minor_color <- brand_color_maybe_pluck(brand, panel_grid_minor_color)
  axis_text_color        <- brand_color_maybe_pluck(brand, axis_text_color)
  plot_caption_color     <- brand_color_maybe_pluck(brand, plot_caption_color)
  }

  # Create blend function for intermediate colors
  blend <- color_blender(foreground_color, background_color)

  # TODO: ggplot2 fonts
  # text_font <- brand_pluck(brand, "typography", "base", "family")
  # title_font <- brand_pluck(brand, "typography", "headings", "family")
  # text_font_size <- brand_pluck(brand, "typography", "base", "size")
  # if (!is.null(text_font_size)) {
  #   text_font_size <- as.numeric(gsub("[^0-9.]", "", text_font_size))
  # }
  # text_font_size <- text_font_size %||% 11
  # title_font_size <- text_font_size * 1.2

  theme <- ggplot2::theme(
    line = ggplot2::element_line(color = line_color %||% blend(0.2)),
    rect = ggplot2::element_rect(fill = rect_fill %||% background_color),
    text = ggplot2::element_text(
      color = text_color %||% blend(0.1),
      # TODO: ggplot2 fonts
      # family = text_font,
      size = base_size
    ),
    title = ggplot2::element_text(
      color = title_color %||% foreground_color,
      # TODO: ggplot2 fonts
      # family = title_font,
      size = title_size
    ),
    plot.background = ggplot2::element_rect(
      fill = plot_background_fill %||% background_color,
      color = plot_background_fill %||% background_color
    ),
    panel.background = ggplot2::element_rect(
      fill = panel_background_fill %||% background_color,
      color = panel_background_fill %||% background_color
    ),
    panel.grid.major = ggplot2::element_line(
      color = panel_grid_major_color %||% blend(0.85),
      inherit.blank = TRUE
    ),
    panel.grid.minor = ggplot2::element_line(
      color = panel_grid_minor_color %||% blend(0.9),
      inherit.blank = TRUE
    ),
    axis.title = ggplot2::element_text(size = title_size * 0.8),
    axis.ticks = ggplot2::element_line(
      color = panel_grid_major_color %||% blend(0.85)
    ),
    axis.text = ggplot2::element_text(color = axis_text_color %||% blend(0.4)),
    legend.key = ggplot2::element_rect(fill = "transparent", colour = NA),
    plot.caption = ggplot2::element_text(
      size = base_size * 0.8,
      color = plot_caption_color %||% blend(0.3)
    )
  )

  if (packageVersion("ggplot2") >= "4.0.0") {
    theme <- theme +
      ggplot2::theme(
        geom = ggplot2::element_geom(
          ink = foreground_color,
          paper = background_color,
          accent = accent_color
        )
      )
  }

  theme
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
#'
#' library(ggplot2)
#' ggplot(diamonds, aes(carat, price)) +
#'   geom_point() +
#'   theme_brand_thematic(brand)
#'
#' @inheritParams theme_brand_ggplot2
#' @param ... Additional arguments passed to [thematic::thematic_theme()] or
#'   [thematic::thematic_on()].
#'
#' @seealso See the "Branded Theming" section of [theme_brand_ggplot2()] for
#'   more details on how the `brand` argument works.
#' @family branded theming functions
#'
#' @describeIn theme_brand_thematic brand.yml wrapper for
#'   [thematic::thematic_on()]
#' @export
theme_brand_thematic <- function(
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL,
  ...
) {
  check_installed("thematic")

  brand <- resolve_brand_yml(brand)

  bg_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  fg_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")
  accent_color <- brand_color_maybe_pluck(brand, accent, "accent", "primary")

  thematic::thematic_theme(
    bg = bg_color,
    fg = fg_color,
    accent = accent_color,
    ...
  )
}

#' @describeIn theme_brand_thematic brand.yml wrapper for
#'   [thematic::thematic_theme()]
#' @export
theme_brand_thematic_on <- function(
  brand = NULL,
  background = NULL,
  foreground = NULL,
  accent = NULL,
  ...
) {
  check_installed("thematic")

  brand <- resolve_brand_yml(brand)

  bg_color <- brand_color_maybe_pluck(brand, background, "background", "black")
  fg_color <- brand_color_maybe_pluck(brand, foreground, "foreground", "white")
  accent_color <- brand_color_maybe_pluck(brand, accent, "accent", "primary")

  thematic::thematic_on(
    bg = bg_color,
    fg = fg_color,
    accent = accent_color,
    ...
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

blend_colors <- function(x, y, alpha = 0.5) {
  check_installed("prismatic")
  x <- prismatic::clr_mix(x, y, ratio = alpha)
  as.character(x)
}

color_blender <- function(x, y) {
  function(alpha = 0.5) blend_colors(x, y, alpha)
}
