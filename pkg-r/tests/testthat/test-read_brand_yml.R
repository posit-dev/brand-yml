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
      path_norm(file.path(getwd(), "_brand.yml"))
    )
  })

  it("finds _brand.yml in brand/ subdir", {
    withr::local_dir(test_path("fixtures", "find-brand-dir"))

    expect_equal(
      find_project_brand_yml(),
      path_norm(file.path(getwd(), "brand", "_brand.yml"))
    )
  })

  it("finds _brand.yml in a parent directory", {
    withr::local_dir(test_path("fixtures", "find-brand-dir", "app"))

    expect_equal(
      find_project_brand_yml(),
      path_norm(file.path(getwd(), "..", "brand", "_brand.yml"))
    )
  })

  it("find _brand.yml relative to a file", {
    expect_equal(
      find_project_brand_yml(
        test_path("fixtures", "find-brand-dir", "app", "app.R")
      ),
      path_norm(
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
      path_norm(test_path("fixtures", "find-brand-yml", "_brand.yml"))
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

describe("envvar_brand_yml_path()", {
  it("returns NULL when BRAND_YML_PATH is not set", {
    withr::local_envvar("BRAND_YML_PATH" = NA)
    expect_null(envvar_brand_yml_path())
  })

  it("returns path when BRAND_YML_PATH is set", {
    test_path <- path_norm(file.path(tempdir(), "test_brand.yml"))
    withr::local_envvar("BRAND_YML_PATH" = test_path)
    expect_equal(envvar_brand_yml_path(), test_path)
  })
})

describe("read_brand_yml() with environment variable", {
  # Create a temporary brand.yml file for testing
  temp_brand_file <- function(brand = NULL, .envir = parent.frame()) {
    tmp_file <- withr::local_tempfile(fileext = ".yml", .local_envir = .envir)
    brand <- brand %||%
      list(color = list(palette = list(blue = "#0000FF"), primary = "blue"))
    brand <- as_brand_yml(brand)
    writeLines(format(brand), tmp_file)
    path_norm(tmp_file)
  }

  it("uses BRAND_YML_PATH when path is NULL", {
    brand_file <- temp_brand_file()
    withr::local_envvar(BRAND_YML_PATH = brand_file)

    brand <- read_brand_yml()
    expect_equal(brand$path, brand_file)
    expect_equal(brand$color$primary, "#0000FF")
  })

  it("explicit path overrides BRAND_YML_PATH", {
    # Create two brand files with different content
    brand_file1 <- temp_brand_file()
    brand_file2 <- temp_brand_file(
      list(color = list(palette = list(red = "#FF0000"), primary = "red"))
    )

    withr::local_envvar("BRAND_YML_PATH" = brand_file1)

    # Use explicit path instead of env var
    brand <- read_brand_yml(brand_file2)
    expect_equal(brand$path, brand_file2)
    expect_equal(brand$color$primary, "#FF0000")
  })

  it("BRAND_YML_PATH can point to directory as long as it has _brand.yml", {
    # Create temp directory structure
    tmp_dir <- withr::local_tempdir()
    brand_dir <- file.path(tmp_dir, "brand")
    app_dir <- file.path(tmp_dir, "app")

    dir.create(brand_dir, recursive = TRUE)
    dir.create(app_dir, recursive = TRUE)

    # Create brand.yml in brand directory
    brand_file <- file.path(brand_dir, "_brand.yml")
    writeLines(
      format(
        as_brand_yml(
          list(
            color = list(palette = list(green = "#00FF00"), primary = "green")
          )
        )
      ),
      brand_file
    )

    withr::local_envvar("BRAND_YML_PATH" = brand_dir)
    brand <- read_brand_yml()
    expect_equal(brand$color$primary, "#00FF00")

    withr::local_envvar("BRAND_YML_PATH" = app_dir)
    expect_error(
      read_brand_yml(),
      class = "brand_yml_not_found"
    )
  })

  it("error if path is NULL, BRAND_YML_PATH not set, and no brand.yml found", {
    # Create an empty temp directory with no brand.yml
    tmp_dir <- withr::local_tempdir()
    withr::local_dir(tmp_dir)
    withr::local_envvar(BRAND_YML_PATH = NA)
    expect_error(read_brand_yml(), class = "brand_yml_not_found")
  })
})
