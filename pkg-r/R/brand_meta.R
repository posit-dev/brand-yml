brand_meta_normalize <- function(brand) {
  if (!brand_has(brand, "meta")) {
    return(brand)
  }

  check_is_list(brand$meta, arg = "meta")
  check_string_or_list(brand$meta$name, allow_null = TRUE, arg = "meta.name")
  check_string_or_list(brand$meta$link, allow_null = TRUE, arg = "meta.link")

  name <- brand_pluck(brand, "meta", "name")
  if (!is.null(name)) {
    brand$meta$name <- brand_meta_name_normalize(name)
  }

  link <- brand_pluck(brand, "meta", "link")
  if (!is.null(link)) {
    brand$meta$link <- brand_meta_link_normalize(link)
  }

  brand$meta <- compact(brand$meta)

  brand
}

brand_meta_name_normalize <- function(name) {
  if (is_string(name)) {
    name <- list(short = name, full = name)
  } else {
    check_list(name, brand_meta_name_prototype(), "meta.name")
  }

  for (key in names(name)) {
    name[[key]] <- trimws(name[[key]])
  }

  name
}

brand_meta_link_normalize <- function(link) {
  if (is_string(link)) {
    link <- list(home = link)
  }

  check_list(link, brand_meta_link_prototype(), "meta.link", closed = FALSE)

  for (l in names(link)) {
    if (!grepl("/$", link[[l]])) {
      link[[l]] <- paste0(link[[l]], "/")
    }
  }

  link
}

brand_meta_name_prototype <- function() {
  list(
    full = "string",
    short = "string"
  )
}

brand_meta_link_prototype <- function() {
  list(
    home = "string",
    mastodon = "string",
    github = "string",
    linkedin = "string",
    bluesky = "string",
    twitter = "string",
    facebook = "string"
  )
}
