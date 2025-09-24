describe("as_light_dark()", {
  it("creates a light_dark object with both values", {
    result <- as_light_dark(light = "light-value", dark = "dark-value")
    expect_s3_class(result, "character_light_dark")
    expect_s3_class(result, "light_dark")
    expect_equal(result$light, "light-value")
    expect_equal(result$dark, "dark-value")
  })

  it("creates a light_dark object with only light value", {
    result <- as_light_dark(light = "light-value", dark = NULL)
    expect_s3_class(result, "character_light_dark")
    expect_s3_class(result, "light_dark")
    expect_equal(result$light, "light-value")
    expect_null(result$dark)
  })

  it("creates a light_dark object with only dark value", {
    result <- as_light_dark(light = NULL, dark = "dark-value")
    expect_s3_class(result, "character_light_dark")
    expect_s3_class(result, "light_dark")
    expect_null(result$light)
    expect_equal(result$dark, "dark-value")
  })

  it("errors when light and dark have different classes", {
    expect_error(
      as_light_dark(light = "light-value", dark = 123),
      "must have the same classes"
    )
  })

  it("preserves original class in the class name", {
    # Test with data.frame
    df_light <- data.frame(x = 1)
    df_dark <- data.frame(x = 2)
    result <- as_light_dark(df_light, df_dark)
    expect_s3_class(result, "data.frame_light_dark")
    expect_s3_class(result, "light_dark")

    # Test with list
    list_light <- list(a = 1)
    list_dark <- list(b = 2)
    result <- as_light_dark(list_light, list_dark)
    expect_s3_class(result, "list_light_dark")
    expect_s3_class(result, "light_dark")
  })
})
