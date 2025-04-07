test_that("brand.logo single path works", {
  brand <- read_brand_yml(test_path("examples", "brand-logo-single.yml"))

  expect_s3_class(brand$logo, "brand_logo_resource")
  expect_equal(brand$logo$path, "posit.png")
})

test_that("brand.logo single works", {
  brand <- as_brand_yml(list(logo = list(path = "posit.png")))

  expect_s3_class(brand$logo, "brand_logo_resource")
  expect_equal(brand$logo$path, "posit.png")
})

test_that("brand.logo errors are handled", {
  expect_error(as_brand_yml(list(logo = 1234)))
  expect_error(as_brand_yml(list(logo = list(path = "foo", bad = "foo"))))
  expect_error(as_brand_yml(list(logo = list(unknown = "foo.png"))))
  expect_error(as_brand_yml(list(logo = list(images = "foo.png"))))
  expect_error(as_brand_yml(list(logo = list(images = list(light = 1234)))))
  expect_error(as_brand_yml(list(logo = list(small = 1234))))

  expect_snapshot(error = TRUE, {
    as_brand_yml(list(logo = 1234))
    as_brand_yml(list(logo = list(path = "foo", bad = "foo")))
    as_brand_yml(list(logo = list(unknown = "foo.png")))
    as_brand_yml(list(logo = list(images = "foo.png")))
    as_brand_yml(list(logo = list(images = list(light = 1234))))
    as_brand_yml(list(logo = list(small = 1234)))
  })
})

test_that("brand.logo images accept paths", {
  logo <- brand_logo(images = list(cat = "cat.jpg"))
  expect_s3_class(logo$images$cat, "brand_logo_resource")
  expect_equal(logo$images$cat$path, "cat.jpg")
})

test_that("brand.logo simple example works", {
  brand <- read_brand_yml(test_path("examples", "brand-logo-simple.yml"))

  expect_s3_class(brand$logo$small, "brand_logo_resource")
  expect_equal(brand$logo$small$path, "logos/pandas/pandas_mark.svg")

  expect_s3_class(brand$logo$medium, "brand_logo_resource")
  expect_equal(brand$logo$medium$path, "logos/pandas/pandas_secondary.svg")

  expect_s3_class(brand$logo$large, "brand_logo_resource")
  expect_equal(brand$logo$large$path, "logos/pandas/pandas.svg")
})

test_that("brand.logo light/dark example works", {
  brand <- read_brand_yml(test_path("examples", "brand-logo-light-dark.yml"))

  expect_s3_class(brand$logo$small, "brand_logo_resource")
  expect_equal(brand$logo$small$path, "logos/pandas/pandas_mark.svg")

  expect_s3_class(brand$logo$medium, "brand_logo_resource_light_dark")
  expect_s3_class(brand$logo$medium$light, "brand_logo_resource")
  expect_equal(
    brand$logo$medium$light$path,
    "logos/pandas/pandas_secondary.svg"
  )
  expect_s3_class(brand$logo$medium$dark, "brand_logo_resource")
  expect_equal(
    brand$logo$medium$dark$path,
    "logos/pandas/pandas_secondary_white.svg"
  )

  expect_s3_class(brand$logo$large, "brand_logo_resource")
  expect_equal(brand$logo$large$path, "logos/pandas/pandas.svg")
})

test_that("brand.logo full example works", {
  brand <- read_brand_yml(test_path("examples", "brand-logo-full.yml"))

  expect_type(brand$logo$images, "list")
  expect_s3_class(brand$logo$small, "brand_logo_resource")
  expect_equal(brand$logo$small, brand$logo$images$mark)

  expect_s3_class(brand$logo$medium, "brand_logo_resource_light_dark")
  expect_s3_class(brand$logo$medium$light, "brand_logo_resource")
  expect_equal(
    brand$logo$medium$light$path,
    "logos/pandas/pandas_secondary.svg"
  )
  expect_s3_class(brand$logo$medium$dark, "brand_logo_resource")
  expect_equal(brand$logo$medium$dark, brand$logo$images$`secondary-white`)

  expect_s3_class(brand$logo$large, "brand_logo_resource")
  expect_equal(brand$logo$large, brand$logo$images$pandas)

  expect_snapshot(brand$logo)
})

test_that("brand.logo resource images simple works", {
  yaml_str <- "
    logo:
      images:
        logo: brand-yaml.png
      small: logo
  "
  brand <- as_brand_yml(yaml_str)

  expect_type(brand$logo$images, "list")
  expect_true("logo" %in% names(brand$logo$images))
  expect_s3_class(brand$logo$images$logo, "brand_logo_resource")
  expect_null(brand$logo$images$logo$alt)
  expect_equal(brand$logo$images$logo$path, "brand-yaml.png")

  expect_s3_class(brand$logo$small, "brand_logo_resource")
  expect_equal(brand$logo$small, brand$logo$images$logo)
})

test_that("brand.logo resource images with alt works", {
  yaml_str <- "
    logo:
      images:
        logo:
          path: brand-yaml.png
          alt: 'Brand YAML Logo'
      small: logo
  "
  brand <- as_brand_yml(yaml_str)

  expect_type(brand$logo$images, "list")
  expect_true("logo" %in% names(brand$logo$images))
  expect_s3_class(brand$logo$images$logo, "brand_logo_resource")
  expect_equal(brand$logo$images$logo$path, "brand-yaml.png")
  expect_equal(brand$logo$images$logo$alt, "Brand YAML Logo")

  expect_s3_class(brand$logo$small, "brand_logo_resource")
  expect_equal(brand$logo$small, brand$logo$images$logo)
  expect_equal(brand$logo$small$alt, "Brand YAML Logo")
})

test_that("brand.logo resource direct with alt works", {
  yaml_str <- "
    logo:
      small:
        path: brand-yaml.png
        alt: 'Brand YAML Logo'
  "
  brand <- as_brand_yml(yaml_str)

  expect_s3_class(brand$logo$small, "brand_logo_resource")
  expect_equal(brand$logo$small$path, "brand-yaml.png")
  expect_equal(brand$logo$small$alt, "Brand YAML Logo")
})

test_that("brand.logo full alt example works", {
  brand <- read_brand_yml(test_path("examples", "brand-logo-full-alt.yml"))

  expect_type(brand$logo$images, "list")
  expect_s3_class(brand$logo$small, "brand_logo_resource")
  expect_s3_class(brand$logo$medium, "brand_logo_resource_light_dark")
  expect_s3_class(brand$logo$large, "brand_logo_resource")
})
