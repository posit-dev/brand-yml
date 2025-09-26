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

describe("list_restyle_names()", {
  it("converts names to snake case", {
    input_list <- list("a-b" = 1, "c-d" = 2)
    expected_output <- list(a_b = 1, c_d = 2)
    output <- list_restyle_names(input_list, style = "snake")
    expect_equal(output, expected_output)
  })

  it("converts names to kebab case", {
    input_list <- list(a_b = 1, c_d = 2)
    expected_output <- list("a-b" = 1, "c-d" = 2)
    output <- list_restyle_names(input_list, style = "kebab")
    expect_equal(output, expected_output)
  })

  it("does not change names without '-' or '_'", {
    x <- list(aa = 1, ab = 2)
    names(x) <- c("aa", "ab")
    expect_identical(names(list_restyle_names(x, "snake")), c("aa", "ab"))
    expect_identical(names(list_restyle_names(x, "kebab")), c("aa", "ab"))
  })

  it("handles nested lists", {
    input_list <- list(a_b = list(c_d = 1), e_f = list(g_h = 2))
    expected_output <- list("a-b" = list("c-d" = 1), "e-f" = list("g-h" = 2))
    output <- list_restyle_names(input_list, style = "kebab")
    expect_equal(output, expected_output)
  })

  it("handles empty lists", {
    input_list <- list()
    expected_output <- list()
    output <- list_restyle_names(input_list, style = "snake")
    expect_equal(output, expected_output)
  })

  it("handles lists with NULL names", {
    input_list <- list(1, 2, 3)
    expected_output <- list(1, 2, 3)
    output <- list_restyle_names(input_list, style = "snake")
    expect_equal(output, expected_output)
  })

  it("avoids converting names that would create duplicates", {
    input_list <- list("a_b" = "a_b", "a-b" = "a-b")
    expect_equal(list_restyle_names(input_list[2:1], "snake"), input_list[2:1])
    expect_equal(list_restyle_names(input_list, "kebab"), input_list)
  })

  it("snake: skips if it would duplicate an existing original name", {
    x <- list(a_b = 1, "a-b" = 2)
    expect_identical(list_restyle_names(x, "snake"), x)
    expect_identical(list_restyle_names(x[2:1], "snake"), x[2:1])
  })

  it("kebab: skips if it would duplicate an existing original name", {
    x <- list("a-b" = 1, a_b = 2)
    expect_identical(list_restyle_names(x, "kebab"), x)
    expect_identical(list_restyle_names(x[2:1], "kebab"), x[2:1])
  })

  it("snake: only entirely non-duplicated names can be converted", {
    x <- list("p-q" = 1, "p-q" = 2, "r-s" = 3)
    expected <- set_names(x, c("p-q", "p-q", "r_s"))
    expect_equal(list_restyle_names(x, "snake"), expected)
  })

  it("kebab: only entirely non-duplicated names can be converted", {
    x <- list("p_q" = 1, "p_q" = 2, "r_s" = 3)
    expected <- set_names(x, c("p_q", "p_q", "r-s"))
    expect_equal(list_restyle_names(x, "kebab"), expected)
  })

  it("round trips snake -> kebab -> snake", {
    # note we start with entirely snake-case names
    x <- list("p_q" = 1, "p_q" = 2, "r_s" = 3)
    expect_equal(
      list_restyle_names(list_restyle_names(x, "kebab"), "snake"),
      x
    )
  })

  it("round trips kebab -> snake -> kebab", {
    # note we start with entirely kebab-case names
    x <- list("p-q" = 1, "p-q" = 2, "r-s" = 3)
    expect_equal(
      list_restyle_names(list_restyle_names(x, "snake"), "kebab"),
      x
    )
  })
})
