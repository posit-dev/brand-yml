describe("brand_use_logo()", {
  brand <- as_brand_yml(list(
    logo = list(
      images = list(
        small = "logos/small.png",
        huge = list(path = "logos/huge.png", alt = "Huge logo")
      ),
      small = "small",
      medium = list(
        light = list(
          path = "logos/medium-light.png",
          alt = "Medium light logo"
        ),
        dark = list(path = "logos/medium-dark.png")
      )
    )
  ))

  it("returns the logo resource for a simple logo", {
    # Get the small logo with default parameters
    result <- brand_use_logo(brand, name = "small")
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/small.png")
  })

  it("returns the logo resource from images if specified", {
    result <- brand_use_logo(brand, name = "huge")
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/huge.png")
  })

  it("returns smallest logo with 'smallest' parameter", {
    brand_sizes <- as_brand_yml(list(
      logo = list(
        small = list(path = "logos/small.png"),
        medium = list(path = "logos/medium.png")
      )
    ))

    result <- brand_use_logo(brand_sizes, name = "smallest")
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/small.png")

    # Test with a brand that has only medium logo
    brand_medium_only <- brand_sizes
    brand_medium_only$logo$small <- NULL

    result <- brand_use_logo(brand_medium_only, name = "smallest")
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/medium.png")
  })

  it("returns largest logo with 'largest' parameter", {
    brand_sizes <- as_brand_yml(list(
      logo = list(
        small = list(path = "logos/small.png"),
        medium = list(path = "logos/medium.png"),
        large = list(path = "logos/large.png")
      )
    ))

    result <- brand_use_logo(brand_sizes, name = "largest")
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/large.png")

    # Test with a brand that has only small logo
    brand_small_only <- brand_sizes
    brand_small_only$logo$medium <- NULL
    brand_small_only$logo$large <- NULL

    result <- brand_use_logo(brand_small_only, name = "largest")
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/small.png")
  })

  it("returns NULL if the logo doesn't exist and not required", {
    # Try to get non-existent large logo
    result <- brand_use_logo(brand, name = "large")
    expect_null(result)
  })

  it("errors if logo doesn't exist and is required", {
    # Try to get non-existent large logo with .required = TRUE
    expect_snapshot(error = TRUE, {
      brand_use_logo(brand, name = "large", .required = TRUE)
      brand_use_logo(brand, name = "large", .required = "for header display")
      brand_use_logo(brand, name = "tiny", .required = TRUE)
    })
  })

  it("handles smallest/largest parameters with variants", {
    brand_variants <- as_brand_yml(list(
      logo = list(
        small = list(
          light = list(path = "logos/small-light.png"),
          dark = list(path = "logos/small-dark.png")
        ),
        medium = list(
          light = list(path = "logos/medium-light.png"),
          dark = list(path = "logos/medium-dark.png")
        )
      )
    ))

    # Test smallest with light variant
    result <- brand_use_logo(
      brand_variants,
      name = "smallest",
      variant = "light"
    )
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/small-light.png")

    # Test largest with dark variant
    result <- brand_use_logo(brand_variants, name = "largest", variant = "dark")
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$path, "./logos/medium-dark.png")

    # Test smallest with light/dark variant
    result <- brand_use_logo(
      brand_variants,
      name = "smallest",
      variant = c("light", "dark")
    )
    expect_s3_class(result, "brand_logo_resource_light_dark")
    expect_equal(result$light$path, "./logos/small-light.png")
    expect_equal(result$dark$path, "./logos/small-dark.png")
  })

  it("handles errors for smallest/largest when no logos available", {
    brand_no_logos <- as_brand_yml(list(logo = list()))

    expect_null(brand_use_logo(brand_no_logos, name = "smallest"))
    expect_null(brand_use_logo(brand_no_logos, name = "largest"))

    expect_snapshot(error = TRUE, {
      brand_use_logo(brand_no_logos, name = "smallest", .required = TRUE)
      brand_use_logo(
        brand_no_logos,
        name = "largest",
        .required = "for header display"
      )
    })
  })

  it("handles light/dark variants correctly", {
    # Test getting light variant
    light_result <- brand_use_logo(brand, name = "medium", variant = "light")
    expect_s3_class(light_result, "brand_logo_resource")
    expect_equal(light_result$path, "./logos/medium-light.png")

    # Test getting dark variant
    dark_result <- brand_use_logo(brand, name = "medium", variant = "dark")
    expect_s3_class(dark_result, "brand_logo_resource")
    expect_equal(dark_result$path, "./logos/medium-dark.png")

    # Test auto mode (should default to light)
    auto_result <- brand_use_logo(brand, name = "medium", variant = "auto")
    expect_s3_class(auto_result, "brand_logo_resource_light_dark")
    expect_equal(auto_result$light, light_result)
    expect_equal(auto_result$dark, dark_result)
  })

  it("returns NULL when fallback is not allowed and variant is not available", {
    expect_null(
      brand_use_logo(brand, "small", variant = "light", .allow_fallback = FALSE)
    )

    brand$logo$large <- brand_logo_resource_light_dark(
      dark = brand_logo_resource("logos/large-dark.png")
    )
    expect_null(
      brand_use_logo(brand, "large", variant = "light", .allow_fallback = FALSE)
    )
  })

  it("errors when variant is specified and required but not available and fallback not allowed", {
    brand$logo$large <- brand_logo_resource_light_dark(
      dark = brand_logo_resource("logos/large-dark.png")
    )

    expect_snapshot(error = TRUE, {
      brand_use_logo(
        brand,
        "small",
        variant = "light",
        .required = TRUE,
        .allow_fallback = FALSE
      )
      brand_use_logo(
        brand,
        "small",
        variant = "dark",
        .required = "for header display",
        .allow_fallback = FALSE
      )
      brand_use_logo(
        brand,
        "large",
        variant = "light",
        .required = "for light plot icons",
        .allow_fallback = FALSE
      )
    })
  })

  it("adjusts path relative to brand base_path", {
    brand_pathed <- brand
    brand_pathed$path <- "/base/path/_brand.yml"

    result <- brand_use_logo(brand_pathed, name = "small")
    expect_equal(result$path, "/base/path/logos/small.png")

    # Absolute path should remain unchanged
    brand_abs <- brand_pathed
    brand_abs$logo$small$path <- "/absolute/logos/small.png"
    result <- brand_use_logo(brand_abs, name = "small")
    expect_equal(result$path, "/absolute/logos/small.png")

    # URL should remain unchanged
    brand_url <- brand_pathed
    brand_url$logo$small$path <- "https://example.com/logos/small.png"
    result <- brand_use_logo(brand_url, name = "small")
    expect_equal(result$path, "https://example.com/logos/small.png")
  })

  it("returns light_dark object directly when vector variant is provided", {
    # For a regular logo that isn't light/dark
    simple_result <- brand_use_logo(
      brand,
      name = "small",
      variant = c("light", "dark")
    )
    expect_s3_class(simple_result, "brand_logo_resource_light_dark")
    # These are the same because we requested light/dark, so the single value
    # has been promoted to a light_dark object with identical light and dark.
    expect_equal(simple_result$light, simple_result$dark)
    expect_equal(simple_result$light$path, "./logos/small.png")

    # For a light/dark logo
    ld_result <- brand_use_logo(
      brand,
      name = "medium",
      variant = c("light", "dark")
    )
    expect_s3_class(ld_result, "brand_logo_resource_light_dark")
    expect_s3_class(ld_result, "light_dark")
    expect_s3_class(ld_result$light, "brand_logo_resource")
    expect_s3_class(ld_result$dark, "brand_logo_resource")
    expect_equal(ld_result$light$path, "./logos/medium-light.png")
    expect_equal(ld_result$dark$path, "./logos/medium-dark.png")
  })

  it("adjusts paths in light_dark objects when returning full object", {
    # Add path to brand
    brand_pathed <- brand
    brand_pathed$path <- "/base/path/_brand.yml"

    # Get the medium logo as a light_dark object
    result <- brand_use_logo(
      brand_pathed,
      name = "medium",
      variant = c("light", "dark")
    )
    expect_s3_class(result, "brand_logo_resource_light_dark")
    expect_equal(result$light$path, "/base/path/logos/medium-light.png")
    expect_equal(result$dark$path, "/base/path/logos/medium-dark.png")
  })

  it("handles vector variant with missing variants and fallback", {
    # Create a brand with only light variant
    brand_light_only <- as_brand_yml(list(
      logo = list(
        medium = brand_logo_resource_light_dark(
          light = brand_logo_resource("logos/medium-light.png")
        )
      )
    ))

    # Should return the light_dark object with only light variant
    result <- brand_use_logo(
      brand_light_only,
      name = "medium",
      variant = c("light", "dark")
    )
    expect_s3_class(result, "brand_logo_resource_light_dark")
    expect_s3_class(result$light, "brand_logo_resource")
    expect_equal(result$light$path, "./logos/medium-light.png")
    expect_null(result$dark)
  })

  it("returns NULL when requesting light_dark without fallback on non-light_dark logo", {
    # Try to get a non-light_dark logo as light_dark without fallback
    result <- brand_use_logo(
      brand,
      name = "small",
      variant = c("light", "dark"),
      .allow_fallback = FALSE
    )
    expect_null(result)
  })

  it("errors when requesting light_dark with required=TRUE on non-light_dark logo without fallback", {
    # Try to get a non-light_dark logo as light_dark with required=TRUE and without fallback
    expect_snapshot(error = TRUE, {
      brand_use_logo(
        brand,
        name = "small",
        variant = c("light", "dark"),
        .required = TRUE,
        .allow_fallback = FALSE
      )
      brand_use_logo(
        brand,
        name = "small",
        variant = c("light", "dark"),
        .required = "for theme support",
        .allow_fallback = FALSE
      )
    })
  })

  it("stores attributes from ... in the attrs field", {
    # Test with a simple logo
    result <- brand_use_logo(
      brand,
      name = "small",
      class = "custom-class",
      width = 100
    )
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(
      result$attrs,
      list(class = "custom-class", width = 100)
    )

    # Test with a light/dark logo
    result_ld <- brand_use_logo(
      brand,
      name = "medium",
      id = "logo-id",
      height = 50
    )
    expect_s3_class(result_ld, "brand_logo_resource_light_dark")
    expect_equal(result_ld$attrs, list(id = "logo-id", height = 50))
  })

  it("maintains attributes through variant selection", {
    # Test with a specific variant of a light/dark logo
    result <- brand_use_logo(
      brand,
      name = "medium",
      variant = "light",
      class = "light-logo"
    )
    expect_s3_class(result, "brand_logo_resource")
    expect_equal(result$attrs, list(class = "light-logo"))
    expect_equal(result$path, "./logos/medium-light.png")

    # Test with auto variant
    result_auto <- brand_use_logo(
      brand,
      name = "medium",
      variant = "auto",
      id = "auto-logo"
    )
    expect_s3_class(result_auto, "brand_logo_resource_light_dark")
    expect_equal(result_auto$attrs, list(id = "auto-logo"))
  })

  it("concatenates attributes when object already has attrs", {
    # Create a logo resource with existing attrs
    logo_with_attrs <- brand$logo$small
    logo_with_attrs$attrs <- list(class = "existing-class", width = 100)

    # Create brand with this modified logo
    brand_modified <- brand
    brand_modified$logo$small <- logo_with_attrs

    # Test that attributes are concatenated, not merged
    result <- brand_use_logo(
      brand_modified,
      name = "small",
      class = "new-class",
      height = 50
    )

    expect_s3_class(result, "brand_logo_resource")
    expect_equal(
      result$attrs,
      list(class = "existing-class", width = 100, class = "new-class", height = 50)
    )

    # Verify both class attributes exist (not merged into one)
    classes <- result$attrs[names(result$attrs) == "class"]
    expect_equal(length(classes), 2)
    expect_equal(unname(unlist(classes)), c("existing-class", "new-class"))
  })

  it("errors if arguments in ... are not named", {
    expect_error(
      brand_use_logo(brand, name = "small", variant = "auto", "unnamed-arg"),
      "All arguments in `...` must be named"
    )
  })
})

describe("format() method for brand_logo_resource", {
  logo_resource <- brand_logo_resource(local_tiny_image(), "Test logo")

  it("formats as HTML by default", {
    expect_snapshot({
      cat(format(logo_resource))
    })
  })

  it("formats as HTML with additional attributes", {
    expect_snapshot({
      cat(format(logo_resource, class = "my-logo", width = 100, height = 50))
    })
  })

  it("formats as markdown", {
    expect_snapshot({
      cat(format(logo_resource, .format = "markdown"))
    })
  })

  it("formats as markdown with additional attributes", {
    expect_snapshot({
      cat(format(
        logo_resource,
        .format = "markdown",
        class = "my-logo",
        width = 100
      ))
    })
  })
})

describe("format() method for brand_logo_resource_light_dark", {
  logo_light <- brand_logo_resource(local_tiny_image(), "Light logo")
  logo_dark <- brand_logo_resource(local_tiny_image(), "Dark logo")
  logo_light_dark <- brand_logo_resource_light_dark(
    light = logo_light,
    dark = logo_dark
  )

  it("formats as HTML by default", {
    expect_snapshot({
      cat(format(logo_light_dark))
    })
  })

  it("formats as HTML with additional attributes", {
    expect_snapshot({
      cat(format(logo_light_dark, class = "my-logo", width = 100, height = 50))
    })
  })

  it("formats as markdown", {
    expect_snapshot({
      cat(format(logo_light_dark, .format = "markdown"))
    })
  })

  it("formats as markdown with additional attributes", {
    expect_snapshot({
      cat(format(
        logo_light_dark,
        .format = "markdown",
        class = "my-logo",
        width = 100
      ))
    })
  })

  it("handles a vector of classes", {
    expect_snapshot({
      cat(format(
        logo_light_dark,
        .format = "markdown",
        class = c("my-logo", "my-logo-other")
      ))
    })
  })
})

describe("as.tags() method", {
  logo_resource <- brand_logo_resource(local_tiny_image(), "Test logo")
  logo_light <- brand_logo_resource(local_tiny_image(), "Light logo")
  logo_dark <- brand_logo_resource(local_tiny_image(), "Dark logo")
  logo_light_dark <- brand_logo_resource_light_dark(
    light = logo_light,
    dark = logo_dark
  )

  it("converts brand_logo_resource to HTML tags", {
    skip_if_not_installed("htmltools")

    # Test that format(..., .format = "html") calls as.tags()
    # This indirectly tests as.tags() functionality
    expect_snapshot({
      cat(format(logo_resource, .format = "html"))
    })

    expect_snapshot({
      cat(format(
        logo_resource,
        .format = "html",
        class = "custom-logo",
        width = 200
      ))
    })
  })

  it("converts brand_logo_resource_light_dark to HTML tags", {
    skip_if_not_installed("htmltools")

    # Test that format(..., .format = "html") calls as.tags()
    # This indirectly tests as.tags() functionality
    expect_snapshot({
      cat(format(logo_light_dark, .format = "html"))
    })

    expect_snapshot({
      cat(format(
        logo_light_dark,
        .format = "html",
        class = "custom-logo",
        width = 200
      ))
    })
  })
})

describe("knit_print() method", {
  logo_resource <- brand_logo_resource(local_tiny_image(), "Test logo")
  logo_light <- brand_logo_resource(local_tiny_image(), "Light logo")
  logo_dark <- brand_logo_resource(local_tiny_image(), "Dark logo")
  logo_light_dark <- brand_logo_resource_light_dark(
    light = logo_light,
    dark = logo_dark
  )

  local_mocked_bindings(
    asis_output = function(x, meta = list(), ...) {
      list(out = x, meta = meta)
    },
    .package = "knitr"
  )

  it("renders brand_logo_resource in knitr", {
    skip_if_not_installed("knitr")
    skip_if_not_installed("htmltools")

    result <- knit_print.brand_logo_resource(logo_resource)
    expect_equal(result$meta, list(html_dep_brand_light_dark()))
    expect_type(result$out, "character")
    expect_snapshot(cat(result$out))
  })

  it("renders brand_logo_resource_light_dark in knitr", {
    skip_if_not_installed("knitr")
    skip_if_not_installed("htmltools")

    result <- knit_print.brand_logo_resource_light_dark(logo_light_dark)
    expect_equal(result$meta, list(html_dep_brand_light_dark()))
    expect_type(result$out, "character")
    expect_snapshot(cat(result$out))
  })
})
