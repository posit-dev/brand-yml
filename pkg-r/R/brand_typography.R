brand_typography_normalize <- function(brand) {
  if (!brand_has(brand, "typography")) {
    return(brand)
  }

  brand$typography <- brand_typography_expand_strings(brand)
  brand$typography <- brand_typography_forward_monospace(brand)
  brand_typography_check_allowed_color_fields(brand$typography)
  brand_typography_check(brand$typography)

  brand_typography_fonts_check(brand)
  brand$typography$fonts <- brand_typography_fonts_declare_implied(brand)
  brand$typography$fonts <- brand_typography_fonts_normalize(brand)

  brand
}

brand_typography_expand_strings <- function(brand) {
  typography <- brand_pluck(brand, "typography")
  if (is.null(typography)) {
    return(NULL) # nocovr
  }

  expand_family <- c(
    "base",
    "headings",
    "monospace",
    "monospace-inline",
    "monospace-block"
  )

  for (field in expand_family) {
    if (brand_has_string(typography, field)) {
      typography[[field]] <- list(
        family = typography[[field]]
      )
    }
  }

  typography
}

brand_typography_check <- function(typography) {
  check_list(
    typography,
    brand_typography_prototype(),
    path = "typography"
  )
}

brand_typography_prototype <- function() {
  opt_family <- "string"
  opt_color <- "string"
  opt_size <- "string"
  opt_background_color <- "string"
  opt_style <- function(path) {
    force(path)

    function(style) {
      check_enum(
        style,
        c("normal", "italic"),
        max_len = 2,
        arg = paste.("typography", path, style)
      )
    }
  }
  opt_weight <- function(path) {
    path_weight <- paste.("typography", path, "weight")

    function(weight) {
      check_string_or_number(weight, arg = path_weight)

      if (is.numeric(weight)) {
        check_number_whole(
          weight,
          min = 0,
          max = 1000,
          arg = path_weight
        )
        return()
      }

      if (is_string(weight)) {
        check_enum(
          weight,
          values = names(brand_font_weight_map),
          arg = path_weight
        )
      }
    }
  }
  opt_line_height = function(path) {
    path <- paste.("typography", path, "line-height")

    function(...) {
      check_string_or_number(..., arg = path)
    }
  }

  list(
    fonts = "list",
    base = list(
      family = opt_family,
      weight = opt_weight("base"),
      size = opt_size,
      "line-height" = opt_line_height("base")
    ),
    headings = list(
      family = opt_family,
      weight = opt_weight("headings"),
      style = opt_style("headings"),
      "line-height" = opt_line_height("headings"),
      color = opt_color
    ),
    monospace = list(
      family = opt_family,
      weight = opt_weight("monospace"),
      size = opt_size
    ),
    "monospace-inline" = list(
      family = opt_family,
      weight = opt_weight("monospace-inline"),
      size = opt_size,
      color = opt_color,
      "background-color" = opt_background_color
    ),
    "monospace-block" = list(
      family = opt_family,
      weight = opt_weight("monospace-block"),
      size = opt_size,
      color = opt_color,
      "background-color" = opt_background_color,
      "line-height" = opt_line_height("monospace-block")
    ),
    "link" = list(
      weight = opt_weight("link"),
      color = opt_color,
      "background-color" = opt_background_color
    )
  )
}

# Forward values from `monospace` to inline and block variants.
#
# Ensures that `monospace-inline` and `monospace-block` inherit `family`,
# `style`, `weight`, and `size` from `monospace` if not explicitly set.
brand_typography_forward_monospace <- function(brand) {
  typography <- brand_pluck(brand, "typography")

  if (!brand_has_list(typography, "monospace")) {
    return(typography)
  }

  fwd_keys <- c("family", "style", "weight", "size")

  monospace_defaults <- typography$monospace[
    intersect(fwd_keys, names(typography$monospace))
  ]

  for (field in c("monospace-inline", "monospace-block")) {
    if (brand_has_list(typography, field)) {
      typography[[field]] <- list_merge(monospace_defaults, typography[[field]])
    }
  }

  typography
}

brand_typography_check_allowed_color_fields <- function(typography) {
  disallowed_fields <- list()

  for (field in names(typography)) {
    if (field == "fonts") {
      next
    }

    color_keys <- intersect(
      c("color", "background-color"),
      names(typography[[field]])
    )

    for (key in color_keys) {
      if (is.null(typography[[field]][[key]])) {
        next # nocovr
      }

      not_allowed <-
        field == "base" ||
        field == "monospace" ||
        field == "headings" && key == "background-color"

      if (not_allowed) {
        disallowed_fields <- c(disallowed_fields, list(c(field, key)))
      }
    }
  }

  if (length(disallowed_fields) > 0) {
    disallowed_fields <- map_chr(disallowed_fields, paste, collapse = ".")
    disallowed_fields <- paste0("typography.", disallowed_fields)
    cli::cli_abort(
      "The following fields are not allowed in brand.yml: {.field {disallowed_fields}}."
    )
  }
}

brand_resolve_typography_colors <- function(brand) {
  typography <- brand_pluck(brand, "typography")

  if (is.null(typography)) {
    return(brand)
  }

  theme_color_fields <- brand_color_fields_theme()

  for (field in names(typography)) {
    if (field == "fonts") {
      next
    }

    color_keys <- intersect(
      c("color", "background-color"),
      names(typography[[field]])
    )

    for (key in color_keys) {
      old <- typography[[field]][[key]]
      if (is.null(old)) {
        next # nocovr
      }

      new <- brand_color_pluck(brand, old)

      if (identical(old, new) && old %in% theme_color_fields) {
        path <- as_kebab_case(paste.(field, key))
        cli::cli_abort(
          "{.field typography.{path}} referred to {.code color.{old}} which is not defined."
        )
      }

      typography[[field]][[key]] <- new
    }
  }

  brand$typography <- typography
  brand
}


brand_typography_fonts_check <- function(brand) {
  if (!brand_has(brand, "typography", "fonts")) {
    return(invisible())
  }

  check_is_list(
    brand$typography$fonts,
    allow_null = TRUE,
    arg = "typography.fonts"
  )

  for (i in seq_along(brand$typography$fonts)) {
    font <- brand$typography$fonts[[i]]
    path <- sprintf("typography.fonts[%d]", i)

    check_is_list(font, arg = path)

    check_list(
      font,
      proto = list(family = "string", source = "string"),
      path = path,
      closed = FALSE
    )

    if (length(intersect(c("family", "source"), names(font))) != 2) {
      cli::cli_abort(
        "{.var {path}} must include both `family` and `source`."
      )
    }

    check_enum(font$source, c("system", "file", "google", "bunny"))
  }
}

brand_typography_fonts_declare_implied <- function(brand) {
  fonts <-
    if (brand_has(brand, "typography", "fonts")) {
      brand$typography$fonts
    } else {
      list()
    }

  font_family_listed <- map_chr(fonts, "[[", "family")
  font_family_implied <- map_chr(
    keep(brand$typography, function(x) "family" %in% names(x)),
    `[[`,
    "family"
  )

  font_family_not_declared <- setdiff(
    font_family_implied,
    font_family_listed
  )

  for (family in unique(font_family_not_declared)) {
    font <- list(
      family = family,
      source = brand_typography_default_font_source()
    )
    fonts <- c(fonts, list(font))
  }

  fonts
}

brand_typography_default_font_source <- function() {
  opt <- getOption("brand_yml.default_font_source", NULL)
  if (!is.null(opt)) {
    return(opt)
  }

  Sys.getenv("BRAND_YML_DEFAULT_FONT_SOURCE", "system")
}

brand_typography_fonts_normalize <- function(brand) {
  fonts <- brand$typography$fonts
  if (is.null(fonts)) {
    return(NULL) # nocovr
  }

  defaults <- list(
    file = list(
      format = "truetype",
      weight = "auto",
      style = "normal"
    )
  )

  for (i in seq_along(fonts)) {
    default <- defaults[[fonts[[i]]$source]]

    check_enum(
      fonts[[i]]$source,
      c("system", "file", "bunny", "google"),
      arg = sprintf("typography$fonts[[%d]]$source", i)
    )

    if (fonts[[i]]$source == "file") {
      fonts[[i]]$files <- map(fonts[[i]]$files, function(file) {
        list_merge(
          list(weight = "auto", style = "normal"),
          file
        )
      })
    }
  }

  fonts
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
  if (is.null(x)) {
    return()
  }

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
