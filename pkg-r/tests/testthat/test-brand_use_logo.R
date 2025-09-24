describe("brand_use_logo()", {
  brand <- as_brand_yml(list(
    logo = list(
      small = list(path = "logos/small.png", alt = "Small logo"),
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

  it("returns NULL if the logo doesn't exist and not required", {
    # Try to get non-existent large logo
    result <- brand_use_logo(brand, name = "large")
    expect_null(result)
  })

  it("errors if logo doesn't exist and is required", {
    # Try to get non-existent large logo with required = TRUE
    expect_snapshot(error = TRUE, {
      brand_use_logo(brand, name = "large", required = TRUE)
      brand_use_logo(brand, name = "large", required = "for header display")
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
    expect_equal(auto_result, light_result)
  })

  it("returns NULL when fallback is not allowed and variant is not available", {
    expect_null(
      brand_use_logo(brand, "small", variant = "light", allow_fallback = FALSE)
    )

    brand$logo$large <- brand_logo_resource_light_dark(
      dark = brand_logo_resource("logos/large-dark.png")
    )
    expect_null(
      brand_use_logo(brand, "large", variant = "light", allow_fallback = FALSE)
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
        required = TRUE,
        allow_fallback = FALSE
      )
      brand_use_logo(
        brand,
        "small",
        variant = "dark",
        required = "for header display",
        allow_fallback = FALSE
      )
      brand_use_logo(
        brand,
        "large",
        variant = "light",
        required = "for light plot icons",
        allow_fallback = FALSE
      )
    })
  })

  it("adjusts path relative to brand base_path", {
    brand_pathed <- brand
    brand_pathed$path <- "/base/path"

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
})
