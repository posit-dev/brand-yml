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
    expect_equal(theme_default$text$colour, "#151515")
  })

  it("resolves foreground color with correct precedence", {
    theme_fg <- theme_brand_ggplot2(brand, foreground = "#00FF00")
    expect_equal(theme_fg$text$colour, "#00FF00")

    theme_fg_named <- theme_brand_ggplot2(brand, foreground = "blue")
    expect_equal(theme_fg_named$text$colour, "#447099")
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
    expect_equal(theme$text$colour, "#000000")
  })
})

describe("theme_brand_thematic()", {
  skip_if_not_installed("thematic")
  skip("thematic tests are not yet implemented")

  brand <- test_example("brand-posit.yml")
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
})

describe("theme_brand_plotly()", {
  skip_if_not_installed("plotly")

  brand <- test_example("brand-posit.yml")

  library(plotly)
  p <- plot_ly(x = 1:3, y = 1:3, type = "scatter", mode = "markers")

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
})
