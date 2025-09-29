brand_logo_resource <- function(path, alt = NULL, attrs = NULL) {
  resource <- list(path = path, alt = alt)

  attrs <- check_dots_named(dots_list(!!!attrs))
  if (length(attrs)) {
    resource$attrs <- attrs
  }

  structure(resource, class = "brand_logo_resource")
}

format_inline_brand_logo_resource <- function(x) {
  attrs <- attrs_as_raw_html(x$attrs, "html")
  if (nzchar(attrs)) {
    attrs <- paste0(" ", attrs)
  }

  cli::format_inline(
    '{.cls brand_logo_resource src="{x$path}" alt="{x$alt}"{attrs}}'
  )
}

#' @export
print.brand_logo_resource <- function(x, ...) {
  cat(format_inline_brand_logo_resource(x))
  invisible(x)
}

brand_logo_resource_light_dark <- function(light = NULL, dark = NULL) {
  as_light_dark(light, dark)
}

#' @export
print.brand_logo_resource_light_dark <- function(x, ...) {
  light <- x$light
  dark <- x$dark

  if (!is.null(light)) {
    light$attrs <- c(list(variant = "light"), light$attrs)
    cat(format_inline_brand_logo_resource(light))
  }

  if (!is.null(dark)) {
    dark$attrs <- c(list(variant = "dark"), dark$attrs)
    if (!is.null(light)) {
      cat("\n")
    }
    cat(format_inline_brand_logo_resource(dark))
  }

  invisible(x)
}

brand_logo <- function(
  images = NULL,
  small = NULL,
  medium = NULL,
  large = NULL
) {
  logo <- compact(list(
    images = images,
    small = small,
    medium = medium,
    large = large
  ))

  brand_logo_normalize(list(logo = logo))$logo
}

brand_logo_normalize <- function(brand) {
  if (is.null(brand$logo)) {
    return(brand)
  }

  if (is_string(brand$logo)) {
    brand$logo <- brand_logo_resource(path = brand$logo)
    return(brand)
  }

  if (!is.list(brand$logo)) {
    cli::cli_abort(
      "{.var logo} must be a string or a list, not {.obj_type_friendly {x}}."
    )
  }

  if (is_list(brand$logo) && "path" %in% names(brand$logo)) {
    check_is_list(brand$logo, arg = "logo", allowed_names = c("path", "alt"))
    brand$logo <- brand_logo_resource(
      path = brand$logo$path,
      alt = brand$logo$alt
    )
    return(brand)
  }

  check_is_list(
    brand$logo,
    arg = "logo",
    allowed_names = c("images", "small", "medium", "large")
  )

  brand$logo$images <- brand_logo_normalize_images(brand$logo$images)
  brand$logo <- brand_logo_normalize_sizes(brand$logo, brand$logo$images)

  brand
}

brand_logo_normalize_images <- function(images) {
  check_is_list(images, allow_null = TRUE, arg = "logo.images")

  for (nm in names(images)) {
    x <- images[[nm]]
    if (is.character(x)) {
      images[[nm]] <- brand_logo_resource(path = x)
      next
    }

    if (!is.list(x)) {
      cli::cli_abort(
        "{.var logo.images.{nm}} must be a string or a list, not {.obj_type_friendly {x}}."
      )
    }

    check_list(
      x,
      list(path = "path", alt = "string"),
      path = c("logo", "images")
    )

    images[[nm]] <- brand_logo_resource(x$path, x$alt)
  }

  images
}

brand_logo_normalize_path_or_image <- function(
  path,
  images = NULL,
  size = NULL
) {
  if (is.null(path)) {
    return(NULL) # nocovr
  }

  if (inherits(path, "brand_logo_resource")) {
    return(path)
  }

  if (is_bare_list(path)) {
    check_list(
      path,
      list(path = "path", alt = "string"),
      path = c("logo", size)
    )
    return(brand_logo_resource(path = path$path, alt = path$alt))
  }

  check_string(path, arg = paste(c("logo", size), collapse = "."))

  if (is.null(images) || !path %in% names(images)) {
    return(brand_logo_resource(path = path))
  }

  if (is.character(images[[path]])) {
    return(brand_logo_resource(path = images[[path]])) # nocov
  }

  images[[path]]
}

brand_logo_normalize_sizes <- function(logo, images) {
  # Normalize small, medium, and large
  for (size in c("small", "medium", "large")) {
    value <- logo[[size]]

    brand_logo_normalize_size <- function(x, .size = NULL) {
      brand_logo_normalize_path_or_image(x, images, size = c(size, .size))
    }

    if (is.null(value)) {
      next
    }

    if (is.character(value)) {
      logo[[size]] <- brand_logo_normalize_size(value)
      next
    }

    if (!is.list(value)) {
      cli::cli_abort(
        c(
          "Invalid value for {.field logo.{size}}:",
          "x" = "{.val {value}}",
          "i" = "Expected a string (path or {.field logo.image} name) or a list."
        ),
        class = "brand_logo_invalid_size"
      )
    }

    is_light_dark <- any(
      map_lgl(names(value), function(x) x %in% c("light", "dark"))
    )

    if (is_light_dark) {
      value <- brand_logo_resource_light_dark(
        light = brand_logo_normalize_size(value$light, "light"),
        dark = brand_logo_normalize_size(value$dark, "dark")
      )

      check_list(
        value,
        list(
          light = list(path = "path", alt = "string", attrs = "list"),
          dark = list(path = "path", alt = "string", attrs = "list")
        ),
        path = c("logo", size)
      )

      value$light <- value$light %??%
        brand_logo_resource(path = value$light$path, alt = value$light$alt)
      value$dark <- value$dark %??%
        brand_logo_resource(path = value$dark$path, alt = value$dark$alt)

      logo[[size]] <- value
      next
    }

    value <- brand_logo_normalize_size(value)

    check_list(
      value,
      list(path = "path", alt = "string", attrs = "list"),
      path = c("logo", size)
    )

    logo[[size]] <- brand_logo_resource(path = value$path, alt = value$alt)
  }

  logo
}
