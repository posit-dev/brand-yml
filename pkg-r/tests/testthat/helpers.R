test_example <- function(...) {
  test_path("examples", ...)
}

local_tiny_image <- function(.local_envir = parent.frame()) {
  path <- withr::local_tempfile(fileext = ".gif", .local_envir = .local_envir)
  enc <- "R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw"

  raw <- base64enc::base64decode(enc)
  writeBin(raw, path)

  attr(path, "expected") <- paste0("data:image/gif;base64,", enc)
  path
}
