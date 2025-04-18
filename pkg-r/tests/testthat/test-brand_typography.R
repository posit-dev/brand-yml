test_that("brand.typography validation errors", {
  expect_snapshot(error = TRUE, {
    as_brand_yml(list(typography = list(fonts = "foo")))
    as_brand_yml(list(typography = list(fonts = list(source = "bad"))))
    as_brand_yml(list(typography = list(fonts = list(source = TRUE))))
  })

  expect_snapshot(error = TRUE, {
    as_brand_yml(list(typography = list(fonts = list(list(source = "bad")))))
    as_brand_yml(list(typography = list(fonts = list(list(family = 42)))))
    as_brand_yml(list(typography = list(fonts = list(list(weight = 400)))))
    as_brand_yml(list(
      typography = list(fonts = list(list(family = "foo", source = "bad")))
    ))
  })

  expect_snapshot(error = TRUE, {
    as_brand_yml(list(typography = list(bad = "foo")))
    as_brand_yml(list(typography = list(base = list(family = 42))))
    as_brand_yml(list(typography = list(base = list(size = 42))))
    as_brand_yml(list(typography = list(base = list(size = 42))))

    # not allowed
    as_brand_yml(list(typography = list(base = list(color = "red"))))
    as_brand_yml(list(
      typography = list(base = list("background-color" = "red"))
    ))

    as_brand_yml(list(typography = list(base = list(weight = "bad"))))
    as_brand_yml(list(typography = list(base = list(weight = 100.50))))

    as_brand_yml(list(typography = list(base = list("line-height" = NA))))

    as_brand_yml(list(typography = list(headings = list(style = "bad"))))
    as_brand_yml(list(
      typography = list(headings = list(style = rep("normal", 2)))
    ))
    as_brand_yml(list(typography = list(headings = list(color = 42))))
  })
})

test_that("brand.typography adds system fonts by default", {
  brand <- read_brand_yml(test_example("brand-typography-simple.yml"))

  expect_true(is.list(brand$typography))

  expect_true(is.list(brand$typography$fonts))
  expect_length(brand$typography$fonts, 3)
  expect_equal(
    map_chr(brand$typography$fonts, function(f) f$family),
    c("Open Sans", "Roboto Slab", "Fira Code")
  )
  expect_equal(
    map_chr(brand$typography$fonts, function(f) f$source),
    rep("system", 3)
  )
})

test_that("brand.typography with Google fonts", {
  withr::with_envvar(c("BRAND_YML_DEFAULT_FONT_SOURCE" = "google"), {
    brand <- read_brand_yml(test_example("brand-typography-simple.yml"))
  })

  expect_true(is.list(brand$typography))

  expect_true(is.list(brand$typography$fonts))
  expect_length(brand$typography$fonts, 3)
  expect_equal(
    map_chr(brand$typography$fonts, function(f) f$family),
    c("Open Sans", "Roboto Slab", "Fira Code")
  )
  expect_equal(
    sapply(brand$typography$fonts, function(f) f$source),
    rep("google", 3)
  )

  expect_null(brand$typography$link)
})

test_that("brand.typography with various font sources", {
  brand <- read_brand_yml(test_example("brand-typography-fonts.yml"))

  expect_true(is.list(brand$typography))
  expect_length(brand$typography$fonts, 4)

  # Local Font Files
  local_font <- brand$typography$fonts[[1]]
  expect_equal(local_font$source, "file")
  expect_equal(local_font$family, "Open Sans")

  for (i in seq_along(local_font$files)) {
    font <- local_font$files[[i]]
    expect_true(grepl("OpenSans", font$path))
    expect_true(grepl("\\.ttf$", font$path))
    # expect_equal(font$format, "truetype")
    expect_equal(as.character(font$weight), "auto")
    expect_equal(font$style, c("normal", "italic")[i])
  }

  # Online Font Files
  online_font <- brand$typography$fonts[[2]]
  expect_equal(online_font$source, "file")
  expect_equal(online_font$family, "Closed Sans")

  for (i in seq_along(online_font$files)) {
    font <- online_font$files[[i]]
    expect_true(grepl("^https://", font$path))
    expect_true(grepl("\\.woff2$", font$path))
    # expect_equal(font$format, "woff2")
    expect_equal(as.character(font$weight), c("bold", "auto")[i])
    expect_equal(font$style, c("normal", "italic")[i])
  }

  # Google Fonts
  google_font <- brand$typography$fonts[[3]]
  expect_equal(google_font$family, "Roboto Slab")
  expect_equal(google_font$source, "google")
  expect_equal(as.character(google_font$weight), "600..900")
  expect_equal(google_font$style, "normal")
  expect_equal(google_font$display, "block")

  # Bunny Fonts
  bunny_font <- brand$typography$fonts[[4]]
  expect_equal(bunny_font$source, "bunny")
  expect_equal(bunny_font$family, "Fira Code")
})

test_that("brand.typography with colors", {
  brand <- read_brand_yml(test_example("brand-typography-color.yml"))

  expect_true(is.list(brand$typography))
  expect_true(is.list(brand$color))

  t <- brand$typography
  color <- brand$color
  expect_false(is.null(color$palette))

  expect_null(t$base) # base color is set via color$foreground

  expect_equal(t$headings$color, color$primary)

  expect_equal(t$monospace_inline$color, color$background)
  expect_equal(t$monospace_inline$background_color, color$palette$red)

  expect_equal(t$monospace_block$color, color$foreground)
  expect_equal(t$monospace_block$background_color, color$background)

  expect_equal(t$link$color, color$palette$red)
})

test_that("brand.typography CSS fonts", {
  brand <- read_brand_yml(test_example("brand-typography-fonts.yml"))
  brand_fonts <- brand_sass_fonts(brand)
  brand_fonts_sass_layer <-
    sass::sass_layer(
      defaults = brand_fonts$defaults,
      rules = brand_fonts$rules
    )

  expect_snapshot(
    cat(format(brand_fonts_sass_layer))
  )
})

test_that("brand.typography CSS fonts local", {
  skip("not yet updated")

  fw <- brand_typography_font_file_weight("400..800")
  expect_equal(as.character(fw), "400 800")
  # expect_equal(jsonlite::toJSON(fw, auto_unbox = TRUE), '"400..800"')
  expect_equal(fw$to_str_url(), "400..800")

  expect_error(brand_typography_font_file_weight("400..600..900"))

  fp <- brand_typography_font_files_path(list(
    path = "OpenSans-Variable.ttf",
    weight = "400..800"
  ))
  expect_equal(
    fp$to_css(),
    paste(
      "font-weight: 400 800;",
      "font-style: normal;",
      "src: url('OpenSans-Variable.ttf') format('truetype');",
      sep = "\n"
    )
  )

  brand <- as_brand_yml(list(
    typography = list(
      fonts = list(
        list(
          family = "Open Sans",
          source = "file",
          files = list(list(
            path = "OpenSans-Variable.ttf",
            weight = "400..800",
            style = "italic"
          ))
        ),
        list(family = "Roboto", source = "google", weight = "200..500")
      )
    )
  ))

  expect_true(is.list(brand$typography))
  fonts_css <- brand$typography$fonts_css_include()
  # at_rules <- stringr::str_extract_all(fonts_css, "@(import|font-face)")[[1]]

  expect_equal(at_rules, c("@import", "@font-face"))
  expect_snapshot(fonts_css)
})

test_that("brand typography Google fonts weight range", {
  skip("not yet updated")

  fw <- brand_typography_google_fonts_weight_range("600..800")
  expect_equal(fw$root, c(600, 800))
  expect_equal(as.character(fw), "600..800")
  # expect_equal(jsonlite::toJSON(fw, auto_unbox = TRUE), '"600..800"')
  expect_equal(fw$to_url_list(), list("600..800"))

  fw <- brand_typography_google_fonts_weight_range(c("thin", "bold"))
  expect_equal(fw$root, c(100, 700))

  expect_error(brand_typography_google_fonts_weight_range("600..800..123"))
  expect_error(brand_typography_google_fonts_weight_range(c(200, 400, 600)))
})

test_that("brand.typography disallowed colors", {
  fixtures_dir <- test_path("fixtures", "typography-undefined-color")

  expect_error(
    read_brand_yml(file.path(fixtures_dir, "undefined-base-color.yml")),
    "typography.base.color"
  )

  expect_error(
    read_brand_yml(
      file.path(fixtures_dir, "undefined-monospace-bg-color.yml")
    ),
    "typography.monospace.background-color"
  )

  # We throw an informative error if you use a theme color under typography
  # that isn't defined in the brand because we need those colors to be resolvable
  expect_error(
    read_brand_yml(file.path(fixtures_dir, "undefined-headings-color.yml")),
    "typography.headings.color"
  )

  # Color values that aren't theme colors, however get passed through as-is
  brand <- read_brand_yml(
    file.path(fixtures_dir, "undefined-palette-headings-color.yml")
  )
  expect_equal(brand_pluck(brand, "typography", "headings", "color"), "orange")
})

test_that("brand.typography write font CSS", {
  skip("not yet updated")

  brand <- read_brand_yml(test_example("brand-typography-fonts.yml"))

  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")

  withr::with_tempdir({
    res <- brand$typography$fonts_write_css(getwd())
    expect_false(is.null(res))
    expect_equal(res, normalizePath(getwd()))

    expect_true(file.exists("fonts.css"))
    expect_true(file.exists(file.path(
      "fonts",
      "open-sans",
      "OpenSans-Variable.ttf"
    )))
    expect_true(file.exists(file.path(
      "fonts",
      "open-sans",
      "OpenSans-Variable-Italic.ttf"
    )))
  })

  withr::with_tempdir({
    dep <- brand$typography$fonts_html_dependency(getwd())
    expect_false(is.null(dep))
    expect_s3_class(dep, "html_dependency")

    expect_false(is.null(dep$src$subdir))
    subdir <- dep$src$subdir
    expect_equal(subdir, normalizePath(getwd()))

    expect_true(file.exists(file.path(subdir, "fonts.css")))
    expect_true(file.exists(file.path(
      subdir,
      "fonts",
      "open-sans",
      "OpenSans-Variable.ttf"
    )))
    expect_true(file.exists(file.path(
      subdir,
      "fonts",
      "open-sans",
      "OpenSans-Variable-Italic.ttf"
    )))

    fonts_css_content <- readLines(file.path(subdir, "fonts.css"))
    expect_equal(
      paste(fonts_css_content, collapse = "\n"),
      brand$typography$fonts_css_include()
    )
  })
})

test_that("brand.typography base font size as rem", {
  test_cases <- list(
    list(original = "18px", rem = "1.125rem"),
    list(original = "50%", rem = "0.5rem"),
    list(original = "1.5em", rem = "1.5rem"),
    list(original = "1in", rem = "6rem"),
    list(original = "1.27cm", rem = "3rem"),
    list(original = "12.7mm", rem = "3rem")
  )

  for (case in test_cases) {
    brand <- as_brand_yml(list(
      typography = list(base = list(size = case$original))
    ))

    expect_equal(
      brand_pluck(brand, "typography", "base", "size"),
      !!case$original
    )

    sass <- brand_sass_typography(brand)
    expect_equal(
      sass$defaults$brand_typography_base_size,
      paste(case$rem, "!default")
    )
  }
})

test_that("brand.typography base font size as rem error", {
  brand <- as_brand_yml(list(
    typography = list(base = list(size = "4vw"))
  ))

  expect_equal(brand_pluck(brand, "typography", "base", "size"), "4vw")
  expect_error(brand_sass_typography(brand), "4vw")
})
