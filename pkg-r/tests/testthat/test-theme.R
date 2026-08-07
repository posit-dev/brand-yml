describe("theme_brand_ggplot2()", {
  skip_if_not_installed("ggplot2", "4.0.0")

  brand <- test_example("brand-posit.yml")

  it("creates valid ggplot2 theme", {
    theme <- theme_brand_ggplot2(brand)
    expect_s3_class(theme, c("theme", "gg"))
  })

  it("resolves literal color over named color from brand.yml", {
    theme_literal <- theme_brand_ggplot2(brand, background = "#FF0000")
    expect_equal(theme_literal$plot.background$fill, "#FF0000")
  })

  it("resolves named color from brand.yml", {
    theme_named <- theme_brand_ggplot2(brand, background = "orange")
    expect_equal(theme_named$plot.background$fill, "#EE6331")
  })

  it("uses theme fallback when no explicit color provided", {
    theme_default <- theme_brand_ggplot2(brand)
    expect_equal(theme_default$plot.background$fill, "#FFFFFF")
    # Text color is blended (10% background, 90% foreground)
    expect_equal(theme_default$text$colour, "#2C2C2CFF")
  })

  it("resolves foreground color with correct precedence", {
    theme_fg <- theme_brand_ggplot2(brand, foreground = "#00FF00")
    # Text color is blended with background
    expect_equal(theme_fg$text$colour, "#1AFF1AFF")

    theme_fg_named <- theme_brand_ggplot2(brand, foreground = "blue")
    # Text color is blended with background
    expect_equal(theme_fg_named$text$colour, "#577EA3FF")
  })

  it("resolves accent color with correct precedence", {
    theme_accent <- theme_brand_ggplot2(brand, accent = "orange")
    expect_equal(theme_accent$geom$accent, "#EE6331")
  })

  it("works with brand = FALSE and explicit colors", {
    theme <- theme_brand_ggplot2(
      brand = FALSE,
      background = "#FFFFFF",
      foreground = "#000000",
      accent = "#FF0000"
    )
    expect_s3_class(theme, c("theme", "gg"))
    expect_equal(theme$plot.background$fill, "#FFFFFF")
    # Text color is blended with background
    expect_equal(theme$text$colour, "#1A1A1AFF")
  })

  it("selects light or dark brand colors", {
    brand <- as_brand_yml(list(
      color = list(
        background = list(light = "#FFFFFF", dark = "#222222"),
        foreground = list(light = "#111111", dark = "#EEEEEE"),
        primary = list(light = "#0066CC", dark = "#66B2FF")
      )
    ))

    light <- theme_brand_ggplot2(brand)
    dark <- theme_brand_ggplot2(brand, color_mode = "dark")

    expect_equal(light$plot.background$fill, "#FFFFFF")
    expect_equal(light$geom$ink, "#111111")
    expect_equal(light$geom$accent, "#0066CC")
    expect_equal(dark$plot.background$fill, "#222222")
    expect_equal(dark$geom$ink, "#EEEEEE")
    expect_equal(dark$geom$accent, "#66B2FF")
  })
})

describe("theme_brand_thematic()", {
  skip_if_not_installed("thematic")

  brand <- test_example("brand-posit.yml")

  it("creates valid thematic theme", {
    theme <- theme_brand_thematic(brand)
    expect_type(theme, "list")
    expect_true(all(c("bg", "fg", "accent", "font") %in% names(theme)))
  })

  it("resolves literal color over named color from brand.yml", {
    theme_literal <- theme_brand_thematic(brand, background = "#FF0000")
    expect_equal(theme_literal$bg, "#FF0000")
  })

  it("resolves named color from brand.yml", {
    theme_named <- theme_brand_thematic(brand, background = "orange")
    expect_equal(theme_named$bg, "#EE6331")
  })

  it("uses theme fallback when no explicit color provided", {
    theme_default <- theme_brand_thematic(brand)
    expect_equal(theme_default$bg, "#FFFFFF")
    expect_equal(theme_default$fg, "#151515")
  })

  it("resolves foreground color with correct precedence", {
    theme_fg <- theme_brand_thematic(brand, foreground = "#00FF00")
    expect_equal(theme_fg$fg, "#00FF00")

    theme_fg_named <- theme_brand_thematic(brand, foreground = "blue")
    expect_equal(theme_fg_named$fg, "#447099")
  })

  it("resolves accent color with correct precedence", {
    theme_accent <- theme_brand_thematic(brand, accent = "orange")
    expect_equal(theme_accent$accent, "#EE6331")
  })

  it("works with brand = FALSE and explicit colors", {
    theme <- theme_brand_thematic(
      brand = FALSE,
      background = "#FFFFFF",
      foreground = "#000000",
      accent = "#FF0000"
    )
    expect_type(theme, "list")
    expect_equal(theme$bg, "#FFFFFF")
    expect_equal(theme$fg, "#000000")
    expect_equal(theme$accent, "#FF0000")
  })

  it("thematic_on() gives equivalent theme", {
    brand <- read_brand_yml(test_example("brand-posit.yml"))
    theme_brand_thematic_on(brand)
    withr::defer(thematic::thematic_off())

    expect_equal(
      thematic::thematic_get_option("bg"),
      brand_color_pluck(brand, "background")
    )
    expect_equal(
      thematic::thematic_get_option("fg"),
      brand_color_pluck(brand, "foreground")
    )
    expect_equal(
      thematic::thematic_get_option("accent"),
      brand_color_pluck(brand, "accent")
    )
  })

  it("selects light or dark brand colors", {
    brand <- as_brand_yml(list(
      color = list(
        background = list(light = "#FFFFFF", dark = "#222222"),
        foreground = list(light = "#111111", dark = "#EEEEEE"),
        primary = list(light = "#0066CC", dark = "#66B2FF")
      )
    ))

    light <- theme_brand_thematic(brand)
    dark <- theme_brand_thematic(brand, color_mode = "dark")

    expect_equal(light$bg, "#FFFFFF")
    expect_equal(light$fg, "#111111")
    expect_equal(light$accent, "#0066CC")
    expect_equal(dark$bg, "#222222")
    expect_equal(dark$fg, "#EEEEEE")
    expect_equal(dark$accent, "#66B2FF")
  })
})

describe("theme_brand_flextable()", {
  skip_if_not_installed("flextable")

  brand <- test_example("brand-posit.yml")

  library(flextable)
  ft <- flextable(head(mtcars, 2))

  get_flextable_color <- function(ft, part = "body", style = "background") {
    color <- if (style == "background") {
      ft[[part]]$styles$cells$background.color$data[1, 1]
    } else if (style == "text") {
      ft[[part]]$styles$text$color$data[1, 1]
    } else {
      NULL
    }
    unname(color)
  }

  it("returns themed flextable", {
    ft_themed <- theme_brand_flextable(ft, brand)
    expect_s3_class(ft_themed, "flextable")
  })

  it("resolves literal color override", {
    ft_literal <- theme_brand_flextable(ft, brand, background = "#FF0000")
    expect_equal(
      get_flextable_color(ft_literal, "body", "background"),
      "#FF0000"
    )
  })

  it("resolves named color from brand.yml", {
    ft_named <- theme_brand_flextable(ft, brand, foreground = "orange")
    expect_equal(get_flextable_color(ft_named, "body", "text"), "#EE6331")
  })

  it("applies default brand colors", {
    ft_default <- theme_brand_flextable(ft, brand)
    expect_equal(
      get_flextable_color(ft_default, "body", "background"),
      "#FFFFFF"
    )
    expect_equal(get_flextable_color(ft_default, "body", "text"), "#151515")
  })

  it("selects light or dark brand colors", {
    brand <- as_brand_yml(list(
      color = list(
        background = list(light = "#FFFFFF", dark = "#222222"),
        foreground = list(light = "#111111", dark = "#EEEEEE")
      )
    ))

    ft_dark <- theme_brand_flextable(ft, brand, color_mode = "dark")
    expect_equal(
      get_flextable_color(ft_dark, "body", "background"),
      "#222222"
    )
    expect_equal(get_flextable_color(ft_dark, "body", "text"), "#EEEEEE")
  })
})

describe("theme_brand_gt()", {
  skip_if_not_installed("gt")

  brand <- test_example("brand-posit.yml")

  library(gt)
  tbl <- gt(head(mtcars, 2))

  get_gt_color <- function(tbl, param) {
    opts <- tbl[["_options"]]
    idx <- which(opts$parameter == param)
    if (length(idx) == 0) {
      return(NULL)
    }
    opts$value[[idx]]
  }

  it("returns themed gt table", {
    tbl_themed <- theme_brand_gt(tbl, brand)
    expect_s3_class(tbl_themed, "gt_tbl")
  })

  it("resolves literal color override", {
    tbl_literal <- theme_brand_gt(tbl, brand, background = "#FF0000")
    expect_equal(get_gt_color(tbl_literal, "table_background_color"), "#FF0000")
  })

  it("resolves named color from brand.yml", {
    tbl_named <- theme_brand_gt(tbl, brand, foreground = "orange")
    expect_equal(get_gt_color(tbl_named, "table_font_color"), "#EE6331")
  })

  it("applies default brand colors", {
    tbl_default <- theme_brand_gt(tbl, brand)
    expect_equal(get_gt_color(tbl_default, "table_background_color"), "#FFFFFF")
    expect_equal(get_gt_color(tbl_default, "table_font_color"), "#151515")
  })

  it("selects light or dark brand colors", {
    brand <- as_brand_yml(list(
      color = list(
        background = list(light = "#FFFFFF", dark = "#222222"),
        foreground = list(light = "#111111", dark = "#EEEEEE")
      )
    ))

    tbl_dark <- theme_brand_gt(tbl, brand, color_mode = "dark")
    expect_equal(
      get_gt_color(tbl_dark, "table_background_color"),
      "#222222"
    )
    expect_equal(get_gt_color(tbl_dark, "table_font_color"), "#EEEEEE")
  })
})

describe("theme_brand_plotly()", {
  skip_if_not_installed("plotly")

  brand <- test_example("brand-posit.yml")

  p <- plotly::plot_ly(x = 1:3, y = 1:3, type = "scatter", mode = "markers")

  get_plotly_attr <- function(plot, attr) {
    layout_attrs <- plot$x$layoutAttrs
    for (i in seq_along(layout_attrs)) {
      if (!is.null(layout_attrs[[i]][[attr]])) {
        return(layout_attrs[[i]][[attr]])
      }
    }
    NULL
  }

  it("returns themed plotly plot", {
    p_themed <- theme_brand_plotly(p, brand)
    expect_s3_class(p_themed, "plotly")
  })

  it("resolves literal color override", {
    p_literal <- theme_brand_plotly(p, brand, background = "#FF0000")
    expect_equal(get_plotly_attr(p_literal, "paper_bgcolor"), "#FF0000")
    expect_equal(get_plotly_attr(p_literal, "plot_bgcolor"), "#FF0000")
  })

  it("resolves named color from brand.yml", {
    p_named <- theme_brand_plotly(p, brand, foreground = "orange")
    expect_equal(get_plotly_attr(p_named, "font")$color, "#EE6331")
  })

  it("applies default brand colors", {
    p_default <- theme_brand_plotly(p, brand)
    expect_equal(get_plotly_attr(p_default, "paper_bgcolor"), "#FFFFFF")
    expect_equal(get_plotly_attr(p_default, "plot_bgcolor"), "#FFFFFF")
    expect_equal(get_plotly_attr(p_default, "font")$color, "#151515")
  })

  it("resolves accent color", {
    p_accent <- theme_brand_plotly(p, brand, accent = "blue")
    colorway <- get_plotly_attr(p_accent, "colorway")
    expect_equal(colorway[1], "#447099")
  })

  it("selects light or dark brand colors", {
    brand <- as_brand_yml(list(
      color = list(
        background = list(light = "#FFFFFF", dark = "#222222"),
        foreground = list(light = "#111111", dark = "#EEEEEE"),
        primary = list(light = "#0066CC", dark = "#66B2FF")
      )
    ))

    p_dark <- theme_brand_plotly(p, brand, color_mode = "dark")
    expect_equal(get_plotly_attr(p_dark, "paper_bgcolor"), "#222222")
    expect_equal(get_plotly_attr(p_dark, "font")$color, "#EEEEEE")
    expect_equal(get_plotly_attr(p_dark, "colorway")[1], "#66B2FF")
  })
})
