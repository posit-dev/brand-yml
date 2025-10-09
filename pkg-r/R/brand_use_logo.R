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
#' brand_use_logo(brand, "small", variant = "light-dark")
#' brand_use_logo(
#'   brand,
#'   "small",
#'   variant = "light-dark",
#'   allow_fallback = FALSE
#' )
#'
#' brand_use_logo(brand, "medium", variant = "light")
#' brand_use_logo(brand, "medium", variant = "dark")
#' brand_use_logo(brand, "medium", variant = "light-dark")
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
#'   * `"light-dark"`: Returns a light/dark object with both variants. If a
#'     single logo resource is present for `brand.logo.{name}` and
#'     `allow_fallback` is `TRUE`, the single logo resource is promoted to a
#'     light/dark logo resource with identical light and dark variants.
#' @param .required Logical or character string. If `TRUE`, an error is thrown if
#'   the requested logo is not found. If a string, it is used to describe why
#'   the logo is required in the error message and completes the phrase
#'   `"is required ____"`. Defaults to `FALSE` when `name` is one of the fixed
#'   sizes -- `"small"`, `"medium"`, `"large"` or `"smallest"` or `"largest"`.
#'   Otherwise, an error is thrown by default if the requested logo is not
#'   found.
#' @param .allow_fallback If `TRUE` (the default), allows falling back to a
#'   non-variant-specific logo when a specific variant is requested. Only used
#'   when `name` is one of the fixed logo sizes (`"small"`, `"medium"`, or
#'   `"large"`).
#' @param ... Additional named attributes to be added to the image HTML or
#'   markdown when created via `format()`, [knitr::knit_print()], or
#'   [htmltools::as.tags()].
#'
#' @return A `brand_logo_resource` object, a `brand_logo_resource_light_dark`
#'   object, or `NULL` if the requested logo doesn't exist and `.required` is
#'   `FALSE`.
#'
#' @export
brand_use_logo <- function(
  brand,
  name,
  variant = c("auto", "light", "dark", "light-dark"),
  ...,
  .required = !name %in% c("small", "medium", "large", "smallest", "largest"),
  .allow_fallback = TRUE
) {
  brand <- as_brand_yml(brand)
  check_string(name)
  check_bool(.allow_fallback)
  variant <- arg_match(variant)

  if (isTRUE(.required)) {
    required_reason <- ""
  } else if (isFALSE(.required)) {
    required_reason <- NULL
  } else {
    check_string(.required)
    required_reason <- paste0(" ", trimws(.required))
  }

  dots <- dots_list(..., .homonyms = "keep")
  check_dots_named(dots)

  attach_attrs <- function(x) {
    if (length(dots) > 0) {
      x$attrs <- c(x$attrs, dots)
    }
    x
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
      return(attach_attrs(res))
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

  if (!brand_has(brand, "logo", name)) {
    if (!is.null(required_reason)) {
      cli::cli_abort(
        "{.var brand.logo.{.strong {name}}} is required{required_reason}."
      )
    }
    return(NULL)
  }

  res <- brand_pluck(brand, "logo", name)
  has_light_dark <- inherits(res, "light_dark")

  # Fixup internal paths to be relative to brand yml file.
  if (has_light_dark) {
    if (!is.null(res$light)) {
      res$light$path <- brand_path(brand, res$light$path)
    }
    if (!is.null(res$dark)) {
      res$dark$path <- brand_path(brand, res$dark$path)
    }
  } else {
    res$path <- brand_path(brand, res$path)
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
      return(attach_attrs(res))
    }

    if (!is.null(res$light) && !is.null(res$dark)) {
      # Case A.2: Return light_dark if both variants exist
      return(attach_attrs(res))
    }

    if (!is.null(res$light)) {
      # Case A.3: Return light if only light exists
      return(attach_attrs(res$light))
    }

    if (!is.null(res$dark)) {
      # Case A.4: Return dark if only dark exists
      return(attach_attrs(res$dark))
    }
  }

  # Case B: "light-dark" variant
  if (variant == "light-dark") {
    if (has_light_dark) {
      # Case B.1: Return light_dark if both variants exist
      return(attach_attrs(res))
    }

    if (.allow_fallback) {
      # Case B.2: Promote single to light_dark if fallback allowed
      return(attach_attrs(brand_logo_resource_light_dark(res, res)))
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
    if (!is.null(res[[variant]])) {
      return(attach_attrs(res[[variant]]))
    }
  } else {
    # Case D: return single if fallback allowed
    if (.allow_fallback) {
      return(attach_attrs(res))
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

  attrs <- x$attrs %||% list()

  htmltools::img(
    src = img_src,
    alt = x$alt %||% "",
    class = "brand-logo",
    !!!attrs,
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
    format(htmltools::as.tags(x, ...)),
    meta = list(html_dep_brand_light_dark())
  )
}

#' @exportS3Method knitr::knit_print
knit_print.brand_logo_resource_light_dark <- function(x, ...) {
  check_installed("knitr")
  check_installed("htmltools")
  knitr::asis_output(
    format(htmltools::as.tags(x, ...)),
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

  attrs <- x$attrs %||% list()

  format_dots <- dots_list(..., .homonyms = "error")
  check_dots_named(format_dots)

  dots <- dots_list(
    class = "brand-logo",
    alt = x$alt %||% "",
    !!!attrs,
    !!!format_dots
  )
  path <- maybe_base64_encode_image(x$path)

  sprintf('![](%s){%s}', path, attrs_as_raw_html(dots, "markdown"))
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

  x$light$attrs <- c(x$light$attrs, list(class = "light-content"))
  x$dark$attrs <- c(x$dark$attrs, list(class = "dark-content"))

  light <- format.brand_logo_resource(
    x$light,
    !!!dots,
    .format = "markdown"
  )
  dark <- format.brand_logo_resource(
    x$dark,
    !!!dots,
    .format = "markdown"
  )

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
