as_light_dark <- function(light, dark) {
  if (!is.null(light) && !is.null(dark)) {
    cls_light <- class(light)
    cls_dark <- class(dark)

    if (!identical(cls_light, cls_dark)) {
      cli::cli_abort(c(
        "`light` and `dark` must have the same classes",
        "*" = "{.var light} has class{?es} {.cls {cls_light}}",
        "*" = "{.var dark} has class{?es} {.cls {cls_dark}}"
      ))
    }
  }

  ld_ptype <- light %||% dark
  ld_class <- paste0(class(ld_ptype)[1], "_light_dark")

  structure(
    compact(list(light = light, dark = dark)),
    class = c(ld_class, "light_dark")
  )
}
