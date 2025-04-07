describe("maybe_convert_font_size_to_rem()", {
  it("returns `rem` directly", {
    expect_equal(maybe_convert_font_size_to_rem("1rem"), "1rem")
    expect_equal(maybe_convert_font_size_to_rem("1.123rem"), "1.123rem")
    expect_equal(maybe_convert_font_size_to_rem("1.123 rem"), "1.123rem")
  })

  it("returns `em` as 1:1 with `rem`", {
    expect_equal(maybe_convert_font_size_to_rem("1em"), "1rem")
    expect_equal(maybe_convert_font_size_to_rem("1.123em"), "1.123rem")
    expect_equal(maybe_convert_font_size_to_rem("1.123 em"), "1.123rem")
  })

  it("converts `%` as 100%:1rem", {
    expect_equal(maybe_convert_font_size_to_rem("100%"), "1rem")
    expect_equal(maybe_convert_font_size_to_rem("225%"), "2.25rem")
    expect_equal(maybe_convert_font_size_to_rem("50 %"), "0.5rem")
  })

  it("converts `in`, `cm` and `mm` to `rem`", {
    expect_equal(maybe_convert_font_size_to_rem("1in"), "6rem")
    expect_equal(maybe_convert_font_size_to_rem("0.5in"), "3rem")

    expect_equal(maybe_convert_font_size_to_rem("2.54cm"), "6rem")
    expect_equal(maybe_convert_font_size_to_rem("1.27cm"), "3rem")

    expect_equal(maybe_convert_font_size_to_rem("25.4mm"), "6rem")
    expect_equal(maybe_convert_font_size_to_rem("12.7mm"), "3rem")
  })

  it("throws for unsupported units", {
    expect_error(
      maybe_convert_font_size_to_rem("1 foo")
    )
    expect_error(
      maybe_convert_font_size_to_rem("1 foo bar")
    )
    expect_error(
      maybe_convert_font_size_to_rem("1vw")
    )
    expect_error(
      maybe_convert_font_size_to_rem("123")
    )
  })
})
