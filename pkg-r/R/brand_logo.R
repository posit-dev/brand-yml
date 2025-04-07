brand_logo_resource <- function(path, alt = NULL) {
  structure(list(path = path, alt = alt), class = "brand_logo_resource")
}

#' @export
print.brand_logo_resource <- function(x, ...) {
  cat(cli::format_inline(
    '{.cls brand_logo_resource src="{x$path}" alt="{x$alt}"}'
  ))
  invisible(x)
}

brand_logo_resource_light_dark <- function(light = NULL, dark = NULL) {
  structure(
    compact(list(light = light, dark = dark)),
    class = "brand_logo_resource_light_dark"
  )
}

#' @export
print.brand_logo_resource_light_dark <- function(x, ...) {
  if (!is.null(x$light)) {
    cat(cli::format_inline(
      '{.cls brand_logo_resource variant="light" src="{x$light$path}" alt="{x$light$alt}"}'
    ))
  }
  if (!is.null(x$dark)) {
    x$light %??% cat("\n")
    cat(cli::format_inline(
      '{.cls brand_logo_resource variant="dark" src="{x$dark$path}" alt="{x$dark$alt}"}'
    ))
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
  if (is.null(brand$logo)) return(brand)

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

brand_logo_normalize_path_or_image <- function(path, images = NULL) {
  if (is.null(path)) return(NULL) # nocov
  if (!is.character(path)) return(path)

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

    if (is.null(value)) next

    if (is.character(value)) {
      logo[[size]] <- brand_logo_normalize_path_or_image(value, images)
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
        light = brand_logo_normalize_path_or_image(value$light, images),
        dark = brand_logo_normalize_path_or_image(value$dark, images)
      )

      check_list(
        value,
        list(
          light = list(path = "path", alt = "string"),
          dark = list(path = "path", alt = "string")
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

    value <- brand_logo_normalize_path_or_image(value, images)

    check_list(
      value,
      list(path = "path", alt = "string"),
      path = c("logo", size)
    )

    logo[[size]] <- brand_logo_resource(path = value$path, alt = value$alt)
  }

  logo
}
