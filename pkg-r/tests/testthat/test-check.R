describe("check_enum()", {
  it("passes with a single valid value", {
    expect_null(
      check_enum(x = "a", values = letters[1:5])
    )
  })

  it("passes with multiple valid values within max_len", {
    expect_null(
      check_enum(x = c("a", "b"), values = letters[1:5], max_len = 2)
    )
  })

  it("allows NULL when allow_null = TRUE", {
    expect_null(
      check_enum(x = NULL, values = letters[1:5], allow_null = TRUE)
    )
  })

  it("allows duplicates when allow_dups = TRUE", {
    expect_null(
      check_enum(
        x = c("a", "a"),
        values = letters[1:5],
        allow_dups = TRUE,
        max_len = 2
      )
    )
  })

  it("passes with a value within a subset of letters", {
    expect_null(
      check_enum(x = "c", values = letters[1:5])
    )
  })

  it("passes with a mix of options", {
    expect_null(check_enum(
      x = c("a", "b", "b"),
      values = letters[1:5],
      max_len = 5,
      allow_null = TRUE,
      allow_dups = TRUE
    ))
  })

  test_check_enum <- function(input, ...) {
    check_enum(input, ...)
  }

  it("fails with an invalid single value", {
    expect_snapshot(error = TRUE, {
      test_check_enum("X", values = letters[1:5])
    })
  })

  it("fails with multiple values exceeding max_len", {
    expect_snapshot(error = TRUE, {
      test_check_enum(c("a", "b", "c"), values = letters[1:5], max_len = 2)
    })
  })

  it("fails with NULL when allow_null = FALSE", {
    expect_snapshot(error = TRUE, {
      test_check_enum(NULL, values = letters[1:5], allow_null = FALSE)
    })
  })

  it("fails with duplicates when allow_dups = FALSE", {
    expect_snapshot(error = TRUE, {
      test_check_enum(c("a", "a"), values = letters[1:5], allow_dups = FALSE)
    })
  })
})
