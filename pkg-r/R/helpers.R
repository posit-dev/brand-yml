# Brand utilities --------------------------------------------------------------

brand_has <- function(brand, ...) {
  x <- brand

  for (f in c(...)) {
    val <- tryCatch(x[[f]], error = function(e) NULL)
    if (is.null(val)) return(FALSE)
    x <- x[[f]]
  }

  TRUE
}

brand_pluck <- function(brand, ...) {
  if (!brand_has(brand, ...)) {
    return(NULL)
  }

  brand[[c(...)]]
}

brand_has_string <- function(brand, ...) {
  if (!brand_has(brand, ...)) return(FALSE)
  is_string(brand[[c(...)]])
}

brand_has_list <- function(brand, ...) {
  if (!brand_has(brand, ...)) return(FALSE)
  is_list(brand[[c(...)]])
}
