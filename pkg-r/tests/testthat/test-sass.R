describe("brand_sass_color_palette()", {
  it("returns empty defaults and rules when palette is NULL", {
    brand <- list(color = list())
    result <- brand_sass_color_palette(brand)

    expect_equal(result$defaults, list())
    expect_equal(result$rules, list())
  })

  it("creates brand-prefixed Sass variables for palette colors", {
    brand <- list(
      color = list(
        palette = list(
          primary = "#007bff",
          secondary = "#6c757d",
          success = "#28a745"
        )
      )
    )

    result <- brand_sass_color_palette(brand)

    expect_equal(result$defaults[["brand-primary"]], "#007bff !default")
    expect_equal(result$defaults[["brand-secondary"]], "#6c757d !default")
    expect_equal(result$defaults[["brand-success"]], "#28a745 !default")
  })

  it("uses Sass variable references for bootstrap colors", {
    brand <- list(
      color = list(
        palette = list(
          blue = "#007bff",
          red = "#dc3545",
          green = "#28a745",
          custom = "#123456"
        )
      )
    )

    result <- brand_sass_color_palette(brand)

    expect_equal(result$defaults[["blue"]], "$brand-blue !default")
    expect_equal(result$defaults[["red"]], "$brand-red !default")
    expect_equal(result$defaults[["green"]], "$brand-green !default")
    expect_equal(result$defaults[["brand-custom"]], "#123456 !default")
  })

  it("generates CSS custom properties in rules", {
    brand <- list(
      color = list(
        palette = list(
          primary = "#007bff",
          secondary = "#6c757d"
        )
      )
    )

    result <- brand_sass_color_palette(brand)

    expect_match(result$rules, ":root")
    expect_match(result$rules, "--brand-primary")
    expect_match(result$rules, "--brand-secondary")
  })
})

describe("brand_sass_color()", {
  it("returns empty list when no colors", {
    brand <- list()
    result <- brand_sass_color(brand)

    expect_equal(result, list())
  })

  it("excludes palette from color processing", {
    brand <- list(
      color = list(
        palette = list(should = "be ignored"),
        primary = "#007bff",
        secondary = "#6c757d"
      )
    )

    result <- brand_sass_color(brand)

    expect_equal(length(result$defaults), 2)
    expect_null(result$defaults[["brand_color_palette"]])
    expect_equal(result$defaults[["brand_color_primary"]], "#007bff !default")
    expect_equal(result$defaults[["brand_color_secondary"]], "#6c757d !default")
  })

  it("creates brand_color_* variables with !default", {
    brand <- list(
      color = list(
        primary = "#007bff",
        danger = "#dc3545",
        background = "#ffffff"
      )
    )

    result <- brand_sass_color(brand)

    expect_equal(result$defaults[["brand_color_primary"]], "#007bff !default")
    expect_equal(result$defaults[["brand_color_danger"]], "#dc3545 !default")
    expect_equal(
      result$defaults[["brand_color_background"]],
      "#ffffff !default"
    )
  })
})

describe("brand_sass_typography()", {
  it("returns empty defaults when typography is NULL", {
    brand <- list()
    result <- brand_sass_typography(brand)

    expect_equal(result$defaults, list())
  })

  it("skips fonts field", {
    brand <- list(
      typography = list(
        fonts = list(list(family = "ignored", source = "google")),
        base = list(size = "16px")
      )
    )

    result <- brand_sass_typography(brand)

    expect_null(result$defaults[["brand_typography_fonts"]])
    expect_equal(
      result$defaults[["brand_typography_base_size"]],
      "1rem !default"
    )
  })

  it("creates brand_typography_* variables", {
    brand <- list(
      typography = list(
        base = list(
          size = "16px",
          family = "Roboto"
        ),
        headings = list(
          weight = "bold",
          style = "italic"
        )
      )
    )

    result <- brand_sass_typography(brand)

    expect_equal(
      result$defaults[["brand_typography_base_size"]],
      "1rem !default"
    )
    expect_equal(
      result$defaults[["brand_typography_base_family"]],
      "Roboto !default"
    )
    expect_equal(
      result$defaults[["brand_typography_headings_weight"]],
      "bold !default"
    )
    expect_equal(
      result$defaults[["brand_typography_headings_style"]],
      "italic !default"
    )
  })

  it("replaces hyphens with underscores in variable names and translate base size to rem", {
    brand <- list(
      typography = list(
        "base" = list(
          "size" = "14px",
          "line-height" = 1.6
        )
      )
    )

    result <- brand_sass_typography(brand)

    expect_equal(
      result$defaults[["brand_typography_base_size"]],
      "0.875rem !default"
    )
    expect_equal(
      result$defaults[["brand_typography_base_line_height"]],
      "1.6 !default"
    )
  })
})

describe("brand_sass_fonts()", {
  it("returns empty defaults and rules when fonts is NULL", {
    brand <- list(typography = list())
    result <- brand_sass_fonts(brand)

    expect_equal(result$defaults, list())
    expect_equal(result$rules, list())
  })

  it("handles Google fonts source", {
    skip_if_not_installed("sass")

    brand <- list(
      typography = list(
        fonts = list(
          list(
            family = "Roboto",
            source = "google",
            weight = c(400, 700),
            style = c("normal", "italic")
          )
        )
      )
    )

    result <- brand_sass_fonts(brand)

    expect_true("brand-font-roboto" %in% names(result$defaults))
    expect_true(any(grepl("\\.brand-font-roboto", result$rules)))
  })

  it("creates sanitized font variable names", {
    skip_if_not_installed("sass")

    brand <- list(
      typography = list(
        fonts = list(
          list(
            family = "Open Sans Pro",
            source = "google"
          ),
          list(
            family = "Font@Special#123",
            source = "google"
          )
        )
      )
    )

    result <- brand_sass_fonts(brand)

    expect_true("brand-font-open-sans-pro" %in% names(result$defaults))
    expect_true("brand-font-font-special-123" %in% names(result$defaults))
  })

  it("handles system fonts source", {
    skip_if_not_installed("sass")

    brand <- list(
      typography = list(
        fonts = list(
          list(
            family = "Arial",
            source = "system"
          )
        )
      )
    )

    result <- brand_sass_fonts(brand)

    expect_equal(result$defaults, list())
    expect_equal(result$rules, list())
  })

  it("errors on unknown font source", {
    skip_if_not_installed("sass")

    brand <- list(
      typography = list(
        fonts = list(
          list(
            family = "MyFont",
            source = "unknown"
          )
        )
      )
    )

    expect_error(
      brand_sass_fonts(brand),
      "font[$]source"
    )
  })
})

describe("brand_sass_defaults_bootstrap()", {
  it("returns empty when no bootstrap or shiny defaults", {
    brand <- list()
    result <- brand_sass_defaults_bootstrap(brand)

    expect_equal(result$defaults, list())
    expect_equal(result$layer, list())
  })

  it("processes bootstrap defaults", {
    skip_if_not_installed("sass")

    brand <- list(
      defaults = list(
        bootstrap = list(
          defaults = list(
            primary = "#007bff",
            enable_rounded = TRUE,
            enable_shadows = FALSE
          )
        )
      )
    )

    result <- brand_sass_defaults_bootstrap(brand)

    expect_equal(result$defaults[["primary"]], "#007bff !default")
    expect_equal(result$defaults[["enable_rounded"]], "true !default")
    expect_equal(result$defaults[["enable_shadows"]], "false !default")
  })

  it("processes shiny theme defaults", {
    skip_if_not_installed("sass")

    brand <- list(
      defaults = list(
        shiny = list(
          theme = list(
            defaults = list(
              primary = "#428bca",
              font_size_base = "14px"
            )
          )
        )
      )
    )

    result <- brand_sass_defaults_bootstrap(brand)

    expect_equal(result$defaults[["primary"]], "#428bca !default")
    expect_equal(result$defaults[["font_size_base"]], "14px !default")
  })

  it("shiny defaults override bootstrap defaults", {
    skip_if_not_installed("sass")

    brand <- list(
      defaults = list(
        bootstrap = list(
          defaults = list(
            primary = "#007bff"
          )
        ),
        shiny = list(
          theme = list(
            defaults = list(
              primary = "#428bca"
            )
          )
        )
      )
    )

    result <- brand_sass_defaults_bootstrap(brand)

    expect_equal(result$defaults[["primary"]], "#428bca !default")
  })

  it("handles NULL values as 'null' string", {
    skip_if_not_installed("sass")

    brand <- list(
      defaults = list(
        bootstrap = list(
          defaults = list(
            spacer = NULL
          )
        )
      )
    )

    result <- brand_sass_defaults_bootstrap(brand)

    expect_equal(result$defaults[["spacer"]], "null !default")
  })

  it("includes functions, mixins, and rules in layer", {
    skip_if_not_installed("sass")

    brand <- list(
      defaults = list(
        bootstrap = list(
          functions = "@function test() { @return 1; }",
          mixins = "@mixin test-mixin { color: red; }",
          rules = ".test { color: blue; }"
        ),
        shiny = list(
          theme = list(
            functions = "@function shiny() { @return 2; }",
            mixins = "@mixin shiny-mixin { color: green; }",
            rules = ".shiny { color: yellow; }"
          )
        )
      )
    )

    result <- brand_sass_defaults_bootstrap(brand)

    expect_s3_class(result$layer, "sass_bundle")
    expect_equal(
      result$layer$layers[[1]]$functions,
      c("@function test() { @return 1; }", "@function shiny() { @return 2; }")
    )
    expect_equal(
      result$layer$layers[[1]]$mixins,
      c(
        "@mixin test-mixin { color: red; }",
        "@mixin shiny-mixin { color: green; }"
      )
    )
    expect_equal(
      result$layer$layers[[1]]$rules,
      c(".test { color: blue; }", ".shiny { color: yellow; }")
    )
  })
})
