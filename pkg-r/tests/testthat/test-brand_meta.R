test_that("brand$meta normalization", {
  brand_meta <- as_brand_yml(
    list(
      meta = list(
        name = list(
          full = "Very Big Corporation of America ",
          short = " VBC "
        ),
        link = list(home = "https://very-big-corp.com")
      )
    )
  )

  expect_equal(brand_meta$meta$name$full, "Very Big Corporation of America")
  expect_equal(brand_meta$meta$name$short, "VBC")

  expect_true(!is.null(brand_meta$meta$link))
  expect_equal(brand_meta$meta$link$home, "https://very-big-corp.com/")
})

test_that("brand$meta with handle empty values", {
  meta_empty <- as_brand_yml(
    list(
      meta = list(name = NULL, link = NULL)
    )
  )
  expect_true(is.null(meta_empty$meta$name))
  expect_true(is.null(meta_empty$meta$link))

  meta_empty_name <- as_brand_yml(
    list(
      meta = list(name = NULL, link = "https://example.com")
    )
  )
  expect_true(is.null(meta_empty_name$meta$name))
  expect_equal(meta_empty_name$meta$link$home, "https://example.com/")

  meta_empty_link <- as_brand_yml(
    list(
      meta = list(
        name = list(full = "Very Big Corporation of America"),
        link = NULL
      )
    )
  )
  expect_equal(
    meta_empty_link$meta$name$full,
    "Very Big Corporation of America"
  )
  expect_null(meta_empty_link$meta$name$short)
  expect_true(is.null(meta_empty_link$link))
})

# test_that("BrandMeta throws error on bad URL", {
#   expect_error({
#     BrandMeta$new(
#       name = list(full = "Very Big Corporation of America ", short = " VBC "),
#       link = list(home = "not-a-url")
#     )
#   })
# })

test_that("brand$meta from YAML file (full example)", {
  brand <- read_brand_yml(
    test_path("examples/brand-meta-full.yml")
  )

  expect_true(is_list(brand$meta))
  expect_equal(
    brand$meta$name,
    list(full = "Very Big Corporation of America", short = "VBC")
  )

  expect_true(is_list(brand$meta))
  expect_equal(
    brand$meta$link,
    list(
      home = "https://very-big-corp.com/",
      mastodon = "https://mastodon.social/@VeryBigCorpOfficial/",
      github = "https://github.com/Very-Big-Corp/",
      linkedin = "https://linkedin.com/company/very-big-corp/",
      twitter = "https://twitter.com/VeryBigCorp/",
      facebook = "https://facebook.com/Very-Big-Corp/"
    )
  )
})

test_that("brand$meta from YAML file (small example)", {
  brand <- read_brand_yml(
    test_path("examples/brand-meta-small.yml")
  )

  expect_true(is_list(brand$meta))
  expect_equal(
    brand$meta,
    list(
      name = list(
        short = "Very Big Corp. of America",
        full = "Very Big Corp. of America"
      ),
      link = list(
        home = "https://very-big-corp.com/"
      )
    )
  )
})

test_that("brand.meta validates common issues", {
  expect_error(
    as_brand_yml(list(meta = list(name = 12))),
    "meta.name"
  )

  expect_error(
    as_brand_yml(list(meta = list(name = list(bad = "foo")))),
    "meta.name"
  )

  expect_error(
    as_brand_yml(list(meta = list(link = 12))),
    "meta.link"
  )

  expect_error(
    as_brand_yml(list(meta = list(link = list(home = 42)))),
    "meta.link.home"
  )
})

test_that("brand.meta allows extra fields", {
  brand <- as_brand_yml(
    list(
      meta = list(
        link = list(guidelines = "https://example.com/brand-guidelines"),
        extra = "my extra field"
      )
    )
  )

  expect_equal(
    brand_pluck(brand, "meta", "link", "guidelines"),
    "https://example.com/brand-guidelines/"
  )

  expect_equal(
    brand_pluck(brand, "meta", "extra"),
    "my extra field"
  )
})

test_that("brand.meta.name is normalized to a list", {
  brand <- as_brand_yml(list(
    meta = list(name = "brand.yml")
  ))

  expect_equal(brand_pluck(brand, "meta", "name", "short"), "brand.yml")
  expect_equal(brand_pluck(brand, "meta", "name", "full"), "brand.yml")
})
