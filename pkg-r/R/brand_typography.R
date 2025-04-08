brand_typography_normalize <- function(brand) {
  if (!brand_has(brand, "typography")) {
    return(brand)
  }

  expand_family <- c(
    "base",
    "headings",
    "monospace",
    "monospace-inline",
    "monospace-block"
  )

  for (field in expand_family) {
    if (brand_has_string(brand, "typography", field)) {
      brand[["typography"]][[field]] <- list(
        family = brand[["typography"]][[field]]
      )
    }
  }

  brand
}


brand_font_bunny <- function(
  family,
  weight = NULL,
  style = NULL,
  display = NULL
) {
  weight <- brand_remap_font_weight(weight) %||% seq(100, 900, 100)

  style <- style %||% c("normal", "italic")
  style <- rlang::arg_match(
    style,
    values = c("normal", "italic"),
    multiple = TRUE
  )

  display <- display %||% "auto"
  display <- rlang::arg_match(
    display,
    values = c("swap", "auto", "block", "fallback", "optional"),
    error_arg = "display"
  )

  if (!is.null(weight)) {
    stopifnot(is.character(weight) || is.numeric(weight))
    weight <- sort(weight)
  }

  weight_list <- as.character(weight)
  style_map <- c(normal = "", italic = "i")
  ital <- sort(style_map[style])

  values <- character(0)
  if (length(weight_list) > 0 && length(ital) > 0) {
    # 400,700,400i,700i
    values <- as.vector(outer(weight_list, ital, paste0))
  } else if (length(weight_list) > 0) {
    values <- weight_list
  } else if (length(ital) > 0) {
    values <- ifelse(ital == "", "regular", "italic")
  }

  family_values <- ""
  if (length(values) > 0) {
    family_values <- paste0(":", paste(values, collapse = ","))
  }

  params <- list(
    family = paste0(family, family_values),
    display = display
  )

  url_base <- "https://fonts.bunny.net/css"
  url_query <- paste0(
    names(params),
    "=",
    utils::URLencode(unlist(params)),
    collapse = "&"
  )

  url <- paste0(url_base, "?", url_query)

  sass::font_link(family, url)
}

brand_font_file <- function(family, files, brand_root = getwd()) {
  check_installed(c("sass", "base64enc", "mime"))

  if (!(is.list(files) && length(files) > 0)) {
    abort(
      c(
        sprintf(
          "Font family '%s' must have one or more associated files.",
          family
        ),
        "i" = "Use `source: system` for fonts that are provided by the user's system."
      )
    )
  }

  font_collection_files <- lapply(files, function(file) {
    if (is.null(file$path)) {
      abort(
        sprintf(
          "All font `files` for font family '%s' must have a `path`.",
          family
        )
      )
    }

    font_data_uri <- if (grepl("^https?://", file$path)) {
      font_path <- file$path
    } else {
      font_path <- file.path(brand_root, file$path)
      base64enc::dataURI(
        file = font_path,
        mime = mime::guess_type(font_path)
      )
    }
    font_type <- switch(
      path_ext(tolower(font_path)),
      # otc = "collection",
      # ttc = "collection",
      # eot = "embedded-opentype",
      otf = "opentype",
      ttf = "truetype",
      # svg = "svg",
      # svgz = "svg",
      woff = "woff",
      woff2 = "woff2",
      abort(
        c(
          sprintf("Invalid font type: %s", font_path),
          "i" = "Font must be `.ttf`, `.otf`, `.woff` or `.woff2`."
        )
      )
    )

    sass::font_face(
      family = family,
      src = sprintf("url(%s) format(%s)", font_data_uri, font_type),
      weight = brand_remap_font_weight(file$weight),
      style = file$style,
      display = "auto"
    )
  })

  sass::font_collection(!!!font_collection_files)
}

brand_remap_font_weight <- function(x) {
  if (is.null(x)) return()

  for (i in seq_along(x)) {
    if (x[[i]] %in% names(brand_font_weight_map)) {
      x[[i]] <- brand_font_weight_map[x[[i]]]
    }
  }

  x
}

brand_font_weight_map <- c(
  "thin" = 100,
  "extra-light" = 200,
  "ultra-light" = 200,
  "light" = 300,
  "normal" = 400,
  "regular" = 400,
  "medium" = 500,
  "semi-bold" = 600,
  "demi-bold" = 600,
  "bold" = 700,
  "extra-bold" = 800,
  "ultra-bold" = 800,
  "black" = 900
)
