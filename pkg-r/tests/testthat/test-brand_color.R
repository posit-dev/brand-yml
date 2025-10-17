describe("brand_color_pluck()", {
  it("detects cyclic references in brand.color.palette", {
    brand <- list(
      color = list(
        palette = list(red = "blue", blue = "red")
      )
    )

    expect_error(
      brand_color_pluck(brand, "red"),
      "palette.red -> palette.blue -> palette.red"
    )

    expect_error(
      brand_color_pluck(brand, "blue"),
      "palette.blue -> palette.red -> palette.blue"
    )
  })

  it("detects cyclic references in brand.color", {
    brand <- list(
      color = list(
        primary = "secondary",
        secondary = "primary"
      )
    )

    expect_error(
      brand_color_pluck(brand, "primary"),
      "primary -> secondary -> primary"
    )

    expect_error(
      brand_color_pluck(brand, "secondary"),
      "secondary -> primary -> secondary"
    )
  })

  it("detects cyclic references in brand.color and brand.color.palette", {
    brand1 <- list(
      color = list(
        palette = list(
          primary = "secondary",
          secondary = "resolved" # cycles before reaches here
        ),
        primary = "primary",
        secondary = "primary" # bad
      )
    )

    expect_error(
      brand_color_pluck(brand1, "primary"),
      "primary -> palette.primary -> secondary -> palette.primary"
    )

    brand2 <- list(
      color = list(
        palette = list(red = "primary"),
        primary = "red"
      )
    )

    expect_error(
      brand_color_pluck(brand2, "red"),
      "palette.red -> primary -> palette.red"
    )

    expect_error(
      brand_color_pluck(brand2, "primary"),
      "primary -> palette.red -> primary"
    )
  })

  it("avoids high levels of recursion", {
    max_recursion <- 101
    seq_max <- 1:max_recursion
    color_ref <- function(i) sprintf("color%s", i)

    brand <- list(
      color = list(
        palette = lapply(
          rlang::set_names(seq_max, color_ref(seq_max - 1)),
          color_ref
        )
      )
    )

    expect_error(
      brand_color_pluck(brand, color_ref(0)),
      "recursion limit"
    )
  })

  it("returns `key` if `brand.color` isn't present", {
    brand <- list(meta = list(name = "no color"))
    expect_equal(brand_color_pluck(brand, "red"), "red")
  })

  it("returns `NULL` if the color is preset but `NULL`", {
    brand <- list(color = list(secondary = NULL, palette = list(black = NULL)))
    expect_null(brand_color_pluck(brand, "secondary"))
    expect_null(brand_color_pluck(brand, "black"))
  })

  it("errors if the color value is not a string", {
    brand <- list(
      color = list(
        secondary = 123456,
        palette = list(black = 123456)
      )
    )

    expect_error(brand_color_pluck(brand, "secondary"), "brand.color.secondary")
    expect_error(brand_color_pluck(brand, "black"), "brand.color.palette.black")
  })
})

test_that("brand.color is validated for unexpected fields and basic field structure", {
  expect_error(
    as_brand_yml(list(color = list(palette = "one"))),
    "color[.]palette"
  )

  expect_error(
    as_brand_yml(list(color = list(palette = list("one")))),
    "color[.]palette"
  )

  expect_error(
    as_brand_yml(list(color = list(palette = list("one" = 12)))),
    "color[.]palette[.]one"
  )

  expect_error(
    as_brand_yml(list(color = list(bad = "foo"))),
    "Unexpected"
  )

  for (key in brand_color_fields_theme()) {
    b <- list(color = list())
    b$color[[key]] <- 123

    expect_error(
      as_brand_yml(!!b),
      sprintf("color[.]%s", key)
    )
  }
})

describe("brand_color light/dark variants", {
  it("validates light/dark color structures", {
    # Valid light/dark structure
    brand <- as_brand_yml(list(
      color = list(
        foreground = list(light = "#111111", dark = "#fafafa")
      )
    ))
    expect_true(inherits(brand, "brand_yml"))
    expect_s3_class(brand$color$foreground, "character_light_dark")
    expect_s3_class(brand$color$foreground, "light_dark")
    expect_equal(brand$color$foreground$light, "#111111")
    expect_equal(brand$color$foreground$dark, "#fafafa")
  })

  it("rejects light/dark structures with invalid keys", {
    expect_error(
      as_brand_yml(list(
        color = list(
          foreground = list(light = "#111", invalid = "#fff")
        )
      )),
      "invalid keys.*'invalid'"
    )
  })

  it("rejects empty light/dark structures", {
    expect_error(
      as_brand_yml(list(
        color = list(
          foreground = list()
        )
      )),
      "must have at least one"
    )
  })

  it("rejects non-string values in light/dark structures", {
    expect_error(
      as_brand_yml(list(
        color = list(
          foreground = list(light = 123, dark = "#fff")
        )
      )),
      "must be a string"
    )
  })

  it("resolves light/dark color references", {
    brand <- as_brand_yml(list(
      color = list(
        palette = list(
          sky = "#87CEEB",
          ocean = "#4A90A4"
        ),
        secondary = list(light = "sky", dark = "ocean")
      )
    ))

    expect_s3_class(brand$color$secondary, "character_light_dark")
    expect_s3_class(brand$color$secondary, "light_dark")
    expect_equal(brand$color$secondary$light, "#87CEEB")
    expect_equal(brand$color$secondary$dark, "#4A90A4")
  })

  it("brand_color_pluck() with color_mode='auto' returns light/dark structure", {
    brand <- list(
      color = list(
        foreground = list(light = "#111", dark = "#fff")
      )
    )

    result <- brand_color_pluck(brand, "foreground", color_mode = "auto")
    expect_s3_class(result, "character_light_dark")
    expect_s3_class(result, "light_dark")
    expect_equal(result$light, "#111")
    expect_equal(result$dark, "#fff")
  })

  it("brand_color_pluck() with color_mode='light' returns light value", {
    brand <- list(
      color = list(
        foreground = list(light = "#111", dark = "#fff")
      )
    )

    result <- brand_color_pluck(brand, "foreground", color_mode = "light")
    expect_equal(result, "#111")
  })

  it("brand_color_pluck() with color_mode='dark' returns dark value", {
    brand <- list(
      color = list(
        foreground = list(light = "#111", dark = "#fff")
      )
    )

    result <- brand_color_pluck(brand, "foreground", color_mode = "dark")
    expect_equal(result, "#fff")
  })

  it("brand_color_pluck() with color_mode='light-dark' returns both", {
    brand <- list(
      color = list(
        foreground = list(light = "#111", dark = "#fff")
      )
    )

    result <- brand_color_pluck(brand, "foreground", color_mode = "light-dark")
    expect_s3_class(result, "character_light_dark")
    expect_s3_class(result, "light_dark")
    expect_equal(result$light, "#111")
    expect_equal(result$dark, "#fff")
  })

  it("brand_color_pluck() promotes scalar to light-dark with color_mode='light-dark'", {
    brand <- list(
      color = list(
        primary = "#6339E0"
      )
    )

    result <- brand_color_pluck(brand, "primary", color_mode = "light-dark")
    expect_s3_class(result, "character_light_dark")
    expect_s3_class(result, "light_dark")
    expect_equal(result$light, "#6339E0")
    expect_equal(result$dark, "#6339E0")
  })

  it("brand_color_pluck() with color_mode='light' uses scalar for light", {
    brand <- list(
      color = list(
        primary = "#6339E0"
      )
    )

    result <- brand_color_pluck(brand, "primary", color_mode = "light")
    expect_equal(result, "#6339E0")
  })

  it("brand_color_pluck() with color_mode='dark' uses scalar for dark", {
    brand <- list(
      color = list(
        primary = "#6339E0"
      )
    )

    result <- brand_color_pluck(brand, "primary", color_mode = "dark")
    expect_equal(result, "#6339E0")
  })

  it("brand_color_pluck() falls back when light or dark is missing", {
    brand <- list(
      color = list(
        foreground = list(light = "#111")
      )
    )

    # Light mode: returns light value
    expect_equal(
      brand_color_pluck(brand, "foreground", color_mode = "light"),
      "#111"
    )

    # Dark mode: falls back to light value
    expect_equal(
      brand_color_pluck(brand, "foreground", color_mode = "dark"),
      "#111"
    )
  })
})
