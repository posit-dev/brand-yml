# Brand utilities --------------------------------------------------------------

brand_has <- function(brand, ...) {
  x <- brand

  for (f in c(...)) {
    if (is.null(x[[f]])) return(FALSE)
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
