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

  expect_snapshot(print(brand))
})

test_that("brand typography with Google fonts", {
  withr::with_envvar(c("DEFAULT_FONT_SOURCE" = "google"), {
    brand <- read_brand_yml(test_example("brand-typography-simple.yml"))
  })

  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")

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
  expect_s3_class(brand$typography$base, "brand_typography_base")
  expect_s3_class(brand$typography$headings, "brand_typography_headings")
  expect_s3_class(brand$typography$monospace, "brand_typography_monospace")
  expect_s3_class(
    brand$typography$monospace_inline,
    "brand_typography_monospace_inline"
  )
  expect_s3_class(
    brand$typography$monospace_block,
    "brand_typography_monospace_block"
  )

  expect_snapshot(print(brand))
})

test_that("brand typography with various font sources", {
  brand <- read_brand_yml(test_example("brand-typography-fonts.yml"))

  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")
  expect_length(brand$typography$fonts, 4)

  # Local Font Files
  local_font <- brand$typography$fonts[[1]]
  expect_s3_class(local_font, "brand_typography_font_files")
  expect_equal(local_font$source, "file")
  expect_equal(local_font$family, "Open Sans")

  for (i in seq_along(local_font$files)) {
    font <- local_font$files[[i]]
    expect_s3_class(font, "brand_typography_font_files_path")
    expect_true(grepl("OpenSans", font$path))
    expect_true(grepl("\\.ttf$", font$path))
    expect_equal(font$format, "truetype")
    expect_s3_class(font$weight, "brand_typography_font_file_weight")
    expect_equal(as.character(font$weight), "auto")
    expect_equal(font$style, c("normal", "italic")[i])
  }

  # Online Font Files
  online_font <- brand$typography$fonts[[2]]
  expect_s3_class(online_font, "brand_typography_font_files")
  expect_equal(online_font$source, "file")
  expect_equal(online_font$family, "Closed Sans")

  for (i in seq_along(online_font$files)) {
    font <- online_font$files[[i]]
    expect_s3_class(font, "brand_typography_font_files_path")
    expect_true(grepl("^https://", font$path))
    expect_true(grepl("\\.woff2$", font$path))
    expect_equal(font$format, "woff2")
    expect_equal(as.character(font$weight), c("bold", "auto")[i])
    expect_equal(font$style, c("normal", "italic")[i])
  }

  # Google Fonts
  google_font <- brand$typography$fonts[[3]]
  expect_s3_class(google_font, "brand_typography_font_google")
  expect_equal(google_font$family, "Roboto Slab")
  expect_s3_class(
    google_font$weight,
    "brand_typography_google_fonts_weight_range"
  )
  expect_equal(as.character(google_font$weight), "600..900")
  expect_equal(google_font$weight$to_url_list(), list("600..900"))
  expect_equal(google_font$style, "normal")
  expect_equal(google_font$display, "block")

  # Bunny Fonts
  bunny_font <- brand$typography$fonts[[4]]
  expect_s3_class(bunny_font, "brand_typography_font_bunny")
  expect_equal(bunny_font$family, "Fira Code")

  expect_snapshot(print(brand))
})

test_that("brand typography with colors", {
  brand <- read_brand_yml(test_example("brand-typography-color.yml"))

  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")
  expect_true(is.list(brand$color))
  expect_s3_class(brand$color, "brand_color")

  t <- brand$typography
  color <- brand$color
  expect_false(is.null(color$palette))

  expect_null(t$base) # base color is set via color$foreground

  expect_s3_class(t$headings, "brand_typography_headings")
  expect_equal(t$headings$color, color$primary)

  expect_s3_class(t$monospace_inline, "brand_typography_monospace_inline")
  expect_equal(t$monospace_inline$color, color$background)
  expect_equal(t$monospace_inline$background_color, color$palette$red)

  expect_s3_class(t$monospace_block, "brand_typography_monospace_block")
  expect_equal(t$monospace_block$color, color$foreground)
  expect_equal(t$monospace_block$background_color, color$background)

  expect_s3_class(t$link, "brand_typography_link")
  expect_equal(t$link$color, color$palette$red)

  expect_snapshot(print(brand))
})

test_that("brand typography CSS fonts", {
  brand <- read_brand_yml(test_example("brand-typography-fonts.yml"))

  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")
  expect_snapshot(brand$typography$fonts_css_include())
})

test_that("brand typography CSS fonts local", {
  fw <- brand_typography_font_file_weight("400..800")
  expect_equal(as.character(fw), "400 800")
  expect_equal(jsonlite::toJSON(fw, auto_unbox = TRUE), '"400..800"')
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

  brand <- read_brand_yml_str(
    "
    typography:
      fonts:
        - family: Open Sans
          source: file
          files:
            - path: OpenSans-Variable.ttf
              weight: 400..800
              style: italic
        - family: Roboto
          source: google
          weight: 200..500
  "
  )

  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")
  fonts_css <- brand$typography$fonts_css_include()
  at_rules <- stringr::str_extract_all(fonts_css, "@(import|font-face)")[[1]]

  expect_equal(at_rules, c("@import", "@font-face"))
  expect_snapshot(fonts_css)
})

test_that("brand typography Google fonts weight range", {
  fw <- brand_typography_google_fonts_weight_range("600..800")
  expect_equal(fw$root, c(600, 800))
  expect_equal(as.character(fw), "600..800")
  expect_equal(jsonlite::toJSON(fw, auto_unbox = TRUE), '"600..800"')
  expect_equal(fw$to_url_list(), list("600..800"))

  fw <- brand_typography_google_fonts_weight_range(c("thin", "bold"))
  expect_equal(fw$root, c(100, 700))

  expect_error(brand_typography_google_fonts_weight_range("600..800..123"))
  expect_error(brand_typography_google_fonts_weight_range(c(200, 400, 600)))
})

test_that("brand typography undefined colors", {
  fixtures_dir <- file.path(
    test_path(),
    "fixtures",
    "typography-undefined-color"
  )

  expect_error(
    read_brand_yml(file.path(fixtures_dir, "undefined-base-color.yml")),
    "typography.base.color"
  )

  expect_error(
    read_brand_yml(file.path(
      fixtures_dir,
      "undefined-monospace-background-color.yml"
    )),
    "typography.monospace.background-color"
  )

  expect_error(
    read_brand_yml(file.path(fixtures_dir, "undefined-headings-color.yml")),
    "typography.headings.color"
  )

  brand <- read_brand_yml(file.path(
    fixtures_dir,
    "undefined-palette-headings-color.yml"
  ))
  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")
  expect_s3_class(brand$typography$headings, "brand_typography_headings")
  expect_equal(brand$typography$headings$color, "orange")
})

test_that("brand typography write font CSS", {
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

test_that("brand typography base font size as rem", {
  test_cases <- list(
    list(original = "18px", rem = "1.125rem"),
    list(original = "50%", rem = "0.5rem"),
    list(original = "1.5em", rem = "1.5rem"),
    list(original = "1in", rem = "6rem"),
    list(original = "1.27cm", rem = "3rem"),
    list(original = "12.7mm", rem = "3rem")
  )

  for (case in test_cases) {
    brand <- read_brand_yml_str(sprintf(
      "
      typography:
        base:
          size: %s
    ",
      case$original
    ))

    expect_true(is.list(brand$typography))
    expect_s3_class(brand$typography, "brand_typography")
    expect_s3_class(brand$typography$base, "brand_typography_base")

    data <- brand$typography$model_dump(
      exclude = c("fonts"),
      exclude_none = TRUE,
      context = list(typography_base_size_unit = "rem")
    )
    expect_equal(data, list(base = list(size = case$rem)))
  }
})

test_that("brand typography base font size as rem error", {
  brand <- read_brand_yml_str(
    "
    typography:
      base:
        size: 4vw
  "
  )

  expect_true(is.list(brand$typography))
  expect_s3_class(brand$typography, "brand_typography")
  expect_s3_class(brand$typography$base, "brand_typography_base")

  expect_error(
    brand$typography$model_dump(
      exclude = c("fonts"),
      exclude_none = TRUE,
      context = list(typography_base_size_unit = "rem")
    ),
    "vw units"
  )
})
