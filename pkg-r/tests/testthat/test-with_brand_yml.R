test_that("with_brand_yml", {
  withr::local_envvar(BRAND_YML_PATH = "original")
  tmpdir <- withr::local_tempdir("brand")
  brand_path <- file.path(tmpdir, "my-brand.yml")

  with_brand_yml_path(brand_path, {
    expect_equal(Sys.getenv("BRAND_YML_PATH", "unset"), brand_path)
  })

  expect_equal(Sys.getenv("BRAND_YML_PATH", "unset"), "original")
})
