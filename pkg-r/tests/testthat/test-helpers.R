test_that("brand_has() can traverse past kebab-snake conversion", {
  brand <- list(
    foo = list("bar-baz" = list(qux = 42))
  )

  expect_true(brand_has(brand, "foo", "bar-baz", "qux"))
  expect_true(
    brand_has(list_restyle_names(brand, "snake"), "foo", "bar_baz", "qux")
  )
})

test_that("brand_pluck() can traverse past kebab-snake conversion", {
  brand <- list(
    foo = list("bar-baz" = list(qux = 42))
  )

  expect_equal(brand_pluck(brand, "foo", "bar-baz", "qux"), 42)
  expect_equal(
    brand_pluck(list_restyle_names(brand, "snake"), "foo", "bar_baz", "qux"),
    42
  )
})
