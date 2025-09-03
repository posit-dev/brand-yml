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

test_that("brand.typography.monospace default font is forwarded", {
  brand <- as_brand_yml(list(
    typography = list(
      base = "Times New Roman",
      headings = "Helvetica",
      monospace = "Courier New"
    )
  ))

  expect_s3_class(brand, "brand_yml")
  expect_equal(brand$typography$monospace, list(family = "Courier New"))
  expect_equal(brand$typography$monospace_inline, list(family = "Courier New"))
  expect_equal(brand$typography$monospace_block, list(family = "Courier New"))
})

test_that("brand.typography.monospace default font can be overridden", {
  brand <- as_brand_yml(list(
    typography = list(
      base = "Times New Roman",
      headings = "Helvetica",
      monospace = "Courier New",
      "monospace-inline" = "Fira Code",
      "monospace-block" = "Source Code Pro"
    )
  ))

  expect_s3_class(brand, "brand_yml")
  expect_equal(brand$typography$monospace, list(family = "Courier New"))
  expect_equal(brand$typography$monospace_inline, list(family = "Fira Code"))
  expect_equal(
    brand$typography$monospace_block,
    list(family = "Source Code Pro")
  )
})

test_that("brand.typography.monospace with properties is forwarded", {
  monospace <- list(
    family = "Courier New",
    weight = 700,
    size = "1em"
  )

  brand <- as_brand_yml(list(
    typography = list(
      base = "Times New Roman",
      headings = "Helvetica",
      monospace = monospace
    )
  ))

  expect_s3_class(brand, "brand_yml")
  expect_equal(brand$typography$monospace, monospace)
  expect_equal(brand$typography$monospace_inline, brand$typography$monospace)
  expect_equal(brand$typography$monospace_block, brand$typography$monospace)
})

test_that("brand.typography.monospace with properties is forwarded, but overridden", {
  monospace <- list(
    family = "Courier New",
    weight = 700,
    size = "1em"
  )

  brand <- as_brand_yml(list(
    typography = list(
      base = "Times New Roman",
      headings = "Helvetica",
      monospace = monospace,
      monospace_inline = list(weight = 600),
      monospace_block = list(size = "1.5em")
    )
  ))

  mono_block <- mono_inline <- monospace
  mono_inline$weight <- 600
  mono_block$size <- "1.5em"

  expect_s3_class(brand, "brand_yml")
  expect_equal(brand$typography$monospace, monospace)
  expect_equal(brand$typography$monospace_inline, mono_inline)
  expect_equal(brand$typography$monospace_block, mono_block)
})

test_that("brand.typography with Google fonts", {
  withr::with_envvar(c("BRAND_YML_DEFAULT_FONT_SOURCE" = "google"), {
    brand <- read_brand_yml(test_example("brand-typography-simple.yml"))
  })

  withr::with_options(list(brand_yml.default_font_source = "google"), {
    brand_opt <- read_brand_yml(test_example("brand-typography-simple.yml"))
  })

  expect_equal(brand, brand_opt)

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
  brand_path <- withr::local_tempdir()
  file.copy(
    test_example("fonts", "open-sans", "OpenSans-Variable.ttf"),
    brand_path
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

  expect_snapshot(
    error = TRUE,
    brand_sass_fonts(brand)
  )

  brand$path <- file.path(brand_path, "_brand.yml")

  fonts_bundle <- brand_sass_fonts(brand)
  expect_equal(
    names(fonts_bundle$defaults),
    c("brand-font-open-sans", "brand-font-roboto")
  )
  local_file_dep <- fonts_bundle$defaults[["brand-font-open-sans"]]$html_deps[[1]]() # fmt: skip
  expect_s3_class(local_file_dep, "html_dependency")

  local_file_css <- readLines(file.path(local_file_dep$src$file, "font.css"))
  local_file_css <- sub("base64,[^)]+", "base64,...", local_file_css)
  local_file_css <- paste(local_file_css, collapse = "\n")

  expect_match(local_file_css, "font-family: 'Open Sans'", fixed = TRUE)
  expect_match(local_file_css, "font-style: italic;", fixed = TRUE)
  expect_match(local_file_css, "font-weight: 400 800;", fixed = TRUE)
  expect_match(local_file_css, "src: url(data:font/ttf", fixed = TRUE)
})

test_that("brand typography Google fonts weight range", {
  brand_path <- withr::local_tempdir()
  brand <- as_brand_yml(list(
    typography = list(
      fonts = list(
        list(family = "Roboto", source = "google", weight = "200..500")
      )
    )
  ))
  brand$path <- file.path(brand_path, "_brand.yml")

  fonts_bundle <- brand_sass_fonts(brand)
  expect_equal(names(fonts_bundle$defaults), "brand-font-roboto")

  dep <- suppressMessages(
    fonts_bundle$defaults[["brand-font-roboto"]]$html_deps()
  )
  expect_s3_class(dep, "html_dependency")

  css <- readLines(file.path(dep$src$file, "font.css"))
  css <- paste(css, collapse = "\n")

  expect_match(css, "font-family: 'Roboto'", fixed = TRUE)
  expect_match(css, "font-style: normal;", fixed = TRUE)
  expect_match(css, "font-weight: 200 500;", fixed = TRUE)
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
