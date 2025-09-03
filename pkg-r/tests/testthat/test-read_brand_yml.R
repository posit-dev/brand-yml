describe("as_brand_yml()", {
  brand_list <- list(
    color = list(
      palette = list(red = "#FF1122"),
      primary = "red",
      secondary = "berry"
    )
  )

  brand_str <- "
color:
  palette:
    red: '#FF1122'
  primary: red
  secondary: berry
"

  it("reads lists and character strings", {
    brand_from_list <- as_brand_yml(brand_list)
    brand_from_str <- as_brand_yml(brand_str)

    expect_equal(brand_from_list, brand_from_str)
  })

  it("returns brand_yml objects unchanged", {
    brand <- as_brand_yml(brand_list)
    expect_s3_class(brand, "brand_yml")
    expect_identical(as_brand_yml(brand), brand)
  })

  it("normalizes colors", {
    brand <- as_brand_yml(brand_list)
    expect_s3_class(brand, "brand_yml")
    expect_equal(brand$color$palette$red, brand$color$primary)
    expect_equal(brand$color$secondary, "berry")
  })

  it("normalizes font family choices", {
    brand <- list(
      typography = list(
        base = "Times New Roman",
        headings = "Helvetica",
        monospace = "Courier New",
        "monospace-inline" = "Fira Code"
      )
    )

    brand <- as_brand_yml(brand)
    expect_s3_class(brand, "brand_yml")
    expect_equal(brand$typography$base$family, "Times New Roman")
    expect_equal(brand$typography$headings$family, "Helvetica")
    expect_equal(brand$typography[["monospace"]]$family, "Courier New")
    expect_equal(brand$typography$monospace_inline$family, "Fira Code")
  })
})

describe("find_project_brand_yml()", {
  it("finds _brand.yml in the current working directory", {
    withr::local_dir(test_path("fixtures", "find-brand-yml"))

    expect_equal(
      find_project_brand_yml(),
      file.path(getwd(), "_brand.yml")
    )
  })

  it("finds _brand.yml in brand/ subdir", {
    withr::local_dir(test_path("fixtures", "find-brand-dir"))

    expect_equal(
      find_project_brand_yml(),
      file.path(getwd(), "brand", "_brand.yml")
    )
  })

  it("finds _brand.yml in a parent directory", {
    withr::local_dir(test_path("fixtures", "find-brand-dir", "app"))

    expect_equal(
      find_project_brand_yml(),
      normalizePath(file.path(getwd(), "..", "brand", "_brand.yml"))
    )
  })

  it("find _brand.yml relative to a file", {
    expect_equal(
      find_project_brand_yml(
        test_path("fixtures", "find-brand-dir", "app", "app.R")
      ),
      normalizePath(
        test_path("fixtures", "find-brand-dir", "brand", "_brand.yml")
      )
    )
  })

  it("throws no _brand.yml is found", {
    tmpdir <- withr::local_tempdir()
    expect_error(find_project_brand_yml(tmpdir))
  })
})

describe("read_brand_yml()", {
  it("throws if `path` provided without immediate brand.yml", {
    tmpdir <- withr::local_tempdir()
    expect_error(read_brand_yml(tmpdir), "Could not find")

    expect_error(
      read_brand_yml(
        test_path("fixtures", "find-brand-dir", "app", "app.R")
      ),
      "Could not find"
    )
  })

  it("reads _brand.yml in the current working directory", {
    withr::with_dir(test_path("fixtures", "find-brand-yml"), {
      brand_found <- read_brand_yml()
    })

    brand_direct <- read_brand_yml(
      test_path("fixtures", "find-brand-yml", "_brand.yml")
    )

    expect_equal(brand_found, brand_direct)
    expect_equal(
      brand_found$path,
      normalizePath(test_path("fixtures", "find-brand-yml", "_brand.yml"))
    )
  })
})

test_that("brand_yml read and print methods", {
  brand <- read_brand_yml(test_path("examples", "brand-posit.yml"))
  brand$path <- "_brand.yml"

  expect_snapshot(
    print(brand)
  )
})

test_that("brand_yml read and print methods with typography and colors", {
  brand <- read_brand_yml(test_path("examples", "brand-typography-color.yml"))
  brand$path <- "_brand.yml"

  expect_snapshot(
    print(brand)
  )
})
