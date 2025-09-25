#' Extract a logo resource from a brand
#'
#' Returns a brand logo resource specified by name and variant from a brand
#' object. The image paths in the returned object are adjusted to be absolute,
#' relative to the location of the brand YAML file, if `brand` was read from a
#' file, or the local working directory otherwise.
#'
#' @section Shiny apps and HTML documents:
#' You can use `brand_use_logo()` to include logos in [Shiny
#' apps][shiny::shinyApp()] or in HTML documents produced by
#' [Quarto](https://quarto.org/docs/output-formats/html-basics.html) or [R
#' Markdown][rmarkdown::html_document()].
#'
#' In Shiny apps, logos returned by `brand_use_logo()` will automatically be
#' converted into HTML tags using [htmltools::as.tags()], so you can include
#' them directly in your UI code.
#'
#' ```r
#' library(shiny)
#' library(bslib)
#'
#' brand <- read_brand_yml()
#'
#' ui <- page_navbar(
#'   title = tagList(
#'     brand_use_logo(brand, "small"),
#'     "Brand Use Logo Test"
#'   ),
#'   nav_panel(
#'     "Page 1",
#'     card(
#'       card_header("My Brand"),
#'       brand_use_logo(brand, "medium", variant = "dark")
#'     )
#'   )
#'   # ... The rest of your app
#' )
#' ```
#'
#' If your brand includes a light/dark variant for a specific size, both images
#' will be included in the app, but only the appropriate image will be shown
#' based on the user's system preference of the app's current theme mode if you
#' are using [bslib::input_dark_mode()].
#'
#' To include additional classes or attributes in the `<img>` tag, you can call
#' [htmltools::as.tags()] directly and provide those attributes:
#'
#' ```{r}
#' brand <- as_brand_yml(list(
#'   logo = list(
#'     images = list(
#'       "cat-light" = list(
#'         path = "https://placecats.com/louie/300/300",
#'         alt = "A light-colored tabby cat on a purple rug"
#'       ),
#'       "cat-dark" = list(
#'         path = "https://placecats.com/millie/300/300",
#'         alt = "A dark-colored cat looking into the camera"
#'       ),
#'       "cat-med" = "https://placecats.com/600/600"
#'     ),
#'     small = list(light = "cat-light", dark = "cat-dark"),
#'     medium = "cat-med"
#'   )
#' ))
#'
#' brand_use_logo(brand, "small") |>
#'   htmltools::as.tags(class = "my-logo", height = 32)
#' ```
#'
#' The same applies to HTML documents produced by Quarto or R Markdown, where
#' images can be used in-line:
#'
#' ````markdown
#' ```{r}
#' brand_use_logo(brand, "small")
#' ```
#'
#' This is my brand's medium sized logo: `r brand_use_logo(brand, "medium")`
#' ````
#'
#' Finally, you can use `format()` to convert the logo to raw HTML or markdown:
#'
#' ```{r}
#' cat(format(brand_use_logo(brand, "small", variant = "light")))
#'
#' cat(format(
#'   brand_use_logo(brand, "medium"),
#'   .format = "markdown",
#'   class = "my-logo",
#'   height = 500
#' ))
#' ```
#'
#' @examples
#' brand <- as_brand_yml(list(
#'   logo = list(
#'     images = list(
#'       small = "logos/small.png",
#'       huge = list(path = "logos/huge.png", alt = "Huge Logo")
#'     ),
#'     small = "small",
#'     medium = list(
#'       light = list(
#'         path = "logos/medium-light.png",
#'         alt = "Medium Light Logo"
#'       ),
#'       dark = list(path = "logos/medium-dark.png")
#'     )
#'   )
#' ))
#'
#' brand_use_logo(brand, "small")
#' brand_use_logo(brand, "medium")
#' brand_use_logo(brand, "large")
#' brand_use_logo(brand, "huge")
#'
#' brand_use_logo(brand, "small", variant = "light")
#' brand_use_logo(brand, "small", variant = "light", allow_fallback = FALSE)
#' brand_use_logo(brand, "small", variant = c("light", "dark"))
#' brand_use_logo(
#'   brand,
#'   "small",
#'   variant = c("light", "dark"),
#'   allow_fallback = FALSE
#' )
#'
#' brand_use_logo(brand, "medium", variant = "light")
#' brand_use_logo(brand, "medium", variant = "dark")
#' brand_use_logo(brand, "medium", variant = c("light", "dark"))
#'
#' @param brand A brand object from [read_brand_yml()] or [as_brand_yml()].
#' @param name The name of the logo to use. Either a size (`"small"`,
#'   `"medium"`, `"large"`) or an image name from `brand.logo.images`.
#'   Alternatively, you can also use `"smallest"` or `"largest"` to select the
#'   smallest or largest available logo size, respectively.
#' @param variant Which variant to use, only used when `name` is one of the
#'   brand.yml fixed logo sizes (`"small"`, `"medium"`, or `"large"`). Can be
#'   one of:
#'
#'   * `"auto"`: Auto-detect, returns a light/dark logo resource if both
#'     variants are present, otherwise it returns a single logo resource, either
#'     the value for `brand.logo.{name}` or the single light or dark variant if
#'     only one is present.
#'   * `"light"`: Returns only the light variant. If no light variant is
#'     present, but `brand.logo.{name}` is a single logo resource and
#'     `allow_fallback` is `TRUE`, `brand_use_logo()` falls back to the single
#'     logo resource.
#'   * `"dark"`: Returns only the dark variant, or, as above, falls back to the
#'     single logo resource if no dark variant is present and `allow_fallback`
#'     is `TRUE`.
#'   * `c("light", "dark")`: Returns a light/dark object with both variants. If
#'     a single logo resource is present for `brand.logo.{name}` and
#'     `allow_fallback` is `TRUE`, the single logo resource is promoted to a
#'     light/dark logo resource with identical light and dark variants.
#' @param required Logical or character string. If `TRUE`, an error is thrown if
#'   the requested logo is not found. If a string, it is used to describe why
#'   the logo is required in the error message and completes the phrase
#'   `"is required ____"`.
#' @param allow_fallback If `TRUE` (the default), allows falling back to a
#'   non-variant-specific logo when a specific variant is requested. Only used
#'   when `name` is one of the fixed logo sizes (`"small"`, `"medium"`, or
#'   `"large"`).
#' @param ... Ignored, must be empty.
#'
#' @return A `brand_logo_resource` object, a `brand_logo_resource_light_dark`
#'   object, or `NULL` if the requested logo doesn't exist and `required` is
#'   `FALSE`.
#'
#' @export
brand_use_logo <- function(
  brand,
  name,
  variant = c("auto", "light", "dark"),
  ...,
  required = FALSE,
  allow_fallback = TRUE
) {
  brand <- as_brand_yml(brand)
  check_dots_empty()
  check_string(name)
  check_bool(allow_fallback)

  if (isTRUE(required)) {
    required_reason <- ""
  } else if (isFALSE(required)) {
    required_reason <- NULL
  } else {
    check_string(required)
    required_reason <- paste0(" ", trimws(required))
  }

  if (name %in% c("smallest", "largest")) {
    sizes <- c("small", "medium", "large")
    available <- intersect(sizes, names(brand$logo))
    if (length(available) == 0 && !name %in% names(brand$logo$images)) {
      if (!is.null(required_reason)) {
        cli::cli_abort(
          "No logos are available to satisfy {.var {name}} in {.var brand.logo} or {.var brand.logo.images}{required_reason}."
        )
      }
      return(NULL)
    } else {
      name <- switch(
        name,
        smallest = available[[1]],
        largest = available[[length(available)]]
      )
    }
  }

  if (!name %in% setdiff(names(brand$logo), "images")) {
    if (brand_has(brand, "logo", "images", name)) {
      res <- brand_pluck(brand, "logo", "images", name)
      res$path <- brand_path(brand, res$path)
      return(res)
    }

    if (!is.null(required_reason)) {
      if (!name %in% c("small", "medium", "large")) {
        name <- sprintf("images['%s']", name)
      }
      cli::cli_abort(
        "{.var brand.logo.{.strong {name}}} is required{required_reason}."
      )
    }

    return(NULL)
  }

  name <- arg_match(name, c("small", "medium", "large"))
  variant <- arg_match(variant, multiple = TRUE)

  if ("auto" %in% variant) {
    variant <- "auto"
  } else if (
    identical(intersect(c("light", "dark"), variant), c("light", "dark"))
  ) {
    variant <- "light_dark"
  }

  if (!brand_has(brand, "logo", name)) {
    if (!is.null(required_reason)) {
      cli::cli_abort(
        "{.var brand.logo.{.strong {name}}} is required{required_reason}."
      )
    }
    return(NULL)
  }

  this <- brand_pluck(brand, "logo", name)
  has_light_dark <- inherits(this, "light_dark")

  # Fixup internal paths to be relative to brand yml file.
  if (has_light_dark) {
    if (!is.null(this$light)) {
      this$light$path <- brand_path(brand, this$light$path)
    }
    if (!is.null(this$dark)) {
      this$dark$path <- brand_path(brand, this$dark$path)
    }
  } else {
    this$path <- brand_path(brand, this$path)
  }

  # | variant    | has        | fallback | return               | case |
  # |:-----------|:-----------|:---------|:---------------------|:-----|
  # | auto       | single     | ~        | single               | A.1  |
  # | auto       | light_dark | ~        | light_dark           | A.2  |
  # | auto       | light      | ~        | light                | A.3  |
  # | auto       | dark       | ~        | dark                 | A.4  |
  # | light,dark | light|dark | ~        | light_dark           | B.1  |
  # | light,dark | single     | TRUE     | single -> light_dark | B.2  |
  # | light,dark | single     | FALSE    |                      | B.3  |
  # | light      | light      | ~        | light                | C    |
  # | dark       | dark       | ~        | dark                 | C    |
  # | light      | single     | TRUE     | single               | D    |
  # | dark       | single     | TRUE     | single               | D    |
  # | light      | single     | FALSE    |                      | X    |
  # | dark       | single     | FALSE    |                      | X    |
  # | light      | dark       | ~        |                      | X    |
  # | dark       | light      | ~        |                      | X    |

  # Case A: "auto" variant
  if (variant == "auto") {
    if (!has_light_dark) {
      # Case A.1: Return single value as-is
      return(this)
    }

    if (!is.null(this$light) && !is.null(this$dark)) {
      # Case A.2: Return light_dark if both variants exist
      return(this)
    }

    if (!is.null(this$light)) {
      # Case A.3: Return light if only light exists
      return(this$light)
    }

    if (!is.null(this$dark)) {
      # Case A.4: Return dark if only dark exists
      return(this$dark)
    }
  }

  # Case B: "light_dark" variant
  if (variant == "light_dark") {
    if (has_light_dark) {
      # Case B.1: Return light_dark if both variants exist
      return(this)
    }

    if (allow_fallback) {
      # Case B.2: Promote single to light_dark if fallback allowed
      return(brand_logo_resource_light_dark(this, this))
    }

    # Case B.3: No fallback allowed, error or return NULL
    if (!is.null(required_reason)) {
      cli::cli_abort(
        "{.var brand.logo.{.strong {name}}} requires light/dark variants{required_reason}."
      )
    }

    return(NULL)
  }

  # variant is now "light" or "dark" by definition

  if (has_light_dark) {
    # Case C: return specific variant if it exists
    if (!is.null(this[[variant]])) {
      return(this[[variant]])
    }
  } else {
    # Case D: return single if fallback allowed
    if (allow_fallback) {
      return(this)
    }
  }

  # Case X: specific variant doesn't exist and can't fallback
  if (!is.null(required_reason)) {
    cli::cli_abort(
      "{.var brand.logo.{.strong {name}.{variant}}} is required{required_reason}."
    )
  }

  return(NULL)
}


#' @exportS3Method htmltools::as.tags
as.tags.brand_logo_resource <- function(x, ...) {
  check_installed("htmltools")
  img_src <- maybe_base64_encode_image(x$path)

  htmltools::img(
    src = img_src,
    alt = x$alt %||% "",
    class = "brand-logo",
    ...,
    html_dep_brand_light_dark()
  )
}

maybe_base64_encode_image <- function(path) {
  if (substr(path, 1, 4) %in% c("http", "data")) {
    return(path)
  }
  check_installed(
    "base64enc",
    reason = "to embed local images as base64 data URIs."
  )
  base64enc::dataURI(
    file = path,
    mime = mime::guess_type(path)
  )
}

#' @exportS3Method htmltools::as.tags
as.tags.brand_logo_resource_light_dark <- function(x, ...) {
  check_installed("htmltools")

  htmltools::span(
    class = "brand-logo-light-dark",
    htmltools::as.tags(x$light, class = "light-content", ...),
    htmltools::as.tags(x$dark, class = "dark-content", ...),
  )
}

#' @exportS3Method knitr::knit_print
knit_print.brand_logo_resource <- function(x, ...) {
  check_installed("knitr")
  check_installed("htmltools")
  knitr::asis_output(
    format(htmltools::as.tags(x)),
    meta = list(html_dep_brand_light_dark())
  )
}

#' @exportS3Method knitr::knit_print
knit_print.brand_logo_resource_light_dark <- function(x, ...) {
  check_installed("knitr")
  check_installed("htmltools")
  knitr::asis_output(
    format(htmltools::as.tags(x)),
    meta = list(html_dep_brand_light_dark())
  )
}


#' @export
format.brand_logo_resource <- function(
  x,
  ...,
  .format = c("html", "markdown")
) {
  check_installed("htmltools")
  .format <- arg_match(.format)

  if (.format == "html") {
    return(format(htmltools::as.tags(x, ...)))
  }

  dots <- dots_list(..., .homonyms = "error")
  if (any(!nzchar(names2(dots)))) {
    cli::cli_abort("All arguments must be named.")
  }

  path <- maybe_base64_encode_image(x$path)

  classes <- ".brand-logo"
  if ("class" %in% names(dots)) {
    user_classes <- sprintf(".%s", unlist(strsplit(dots$class, " ")))
    classes <- c(classes, user_classes)
    dots$class <- NULL
  }

  attrs <- c(
    paste(classes, sep = " "),
    sprintf('alt="%s"', x$alt %||% "")
  )

  for (i in seq_along(dots)) {
    value <- dots[[i]]
    if (is.na(value)) {
      attr <- names(dots)[i]
    } else if (is.logical(value)) {
      attr <- sprintf('%s="%s"', names(dots)[i], tolower(as.character(value)))
    } else {
      attr <- sprintf('%s="%s"', names(dots)[i], value)
    }
    attrs <- c(attrs, attr)
  }
  attrs <- paste(attrs, collapse = " ")

  sprintf('![](%s){%s}', path, attrs)
}

#' @export
format.brand_logo_resource_light_dark <- function(
  x,
  ...,
  .format = c("html", "markdown")
) {
  check_installed("htmltools")
  .format <- arg_match(.format)

  if (.format == "html") {
    return(format(htmltools::as.tags(x, ...)))
  }

  dots <- dots_list(..., .homonyms = "error")
  dots_light <- dots_dark <- dots
  if ("class" %in% names(dots)) {
    if (length(dots$class) == 1) {
      dots_light$class <- paste(dots$class, "light-content")
      dots_dark$class <- paste(dots$class, "dark-content")
    } else if (length(dots$class) > 1) {
      dots_light$class <- c(dots$class[1], "light-content")
      dots_dark$class <- c(dots$class[2], "dark-content")
    } else {
      dots$class <- NULL
    }
  }
  if (is.null(dots$class)) {
    dots_light$class <- "light-content"
    dots_dark$class <- "dark-content"
  }

  light <- format(x$light, ..., .format = "markdown")
  dark <- format(x$dark, ..., .format = "markdown")

  paste(light, dark)
}

knitr_is_in_quarto <- function() {
  if (!knitr_in_progress()) {
    return(FALSE)
  }

  !is.null(knitr::opts_knit$get("quarto.version"))
}

knitr_in_progress <- function() {
  isTRUE(getOption("knitr.in.progress"))
}

html_dep_brand_light_dark <- local({
  dep <- NULL

  function() {
    if (knitr_is_in_quarto()) {
      return(NULL)
    }

    if (!is.null(dep)) {
      return(dep)
    }

    check_installed("htmltools")

    dep <<- htmltools::htmlDependency(
      name = "brand-logo-light-dark",
      version = utils::packageVersion("brand.yml"),
      package = "brand.yml",
      src = "resources",
      stylesheet = "brand-light-dark.css",
      all_files = FALSE
    )

    dep
  }
})
