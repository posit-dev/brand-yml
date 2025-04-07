brand_meta_normalize <- function(brand) {
  if (!brand_has(brand, "meta")) {
    return(brand)
  }

  if (brand_has_string(brand, "meta", "name")) {
    name <- brand[["meta"]][["name"]]
    brand[["meta"]][["name"]] <- list(short = name, full = name)
  }

  if (brand_has_list(brand, "meta", "name")) {
    for (nm in c("short", "full")) {
      if (!is.null(brand$meta$name[[nm]])) {
        brand$meta$name[[nm]] <- trimws(brand$meta$name[[nm]])
      }
    }
  }

  if (brand_has_string(brand, "meta", "link")) {
    brand[["meta"]][["link"]] <- list(
      home = brand[["meta"]][["link"]]
    )
  }

  for (link in names(brand$meta$link)) {
    if (!grepl("/$", brand$meta$link[[link]])) {
      brand$meta$link[[link]] <- paste0(brand$meta$link[[link]], "/")
    }
  }

  brand$meta <- compact(brand$meta)

  brand
}
