check_is_brand_yml <- function(x) {
  x_name <- deparse(substitute(x))

  if (!inherits(x, "brand_yml")) {
    cli::cli_abort(
      "{.var {x_name}} must be a {.cls brand_yml} object, not {.obj_type_friendly {x}}"
    )
  }
  invisible(x)
}

check_dots_named <- function(dots, arg = "...", call = caller_env()) {
  if (is.null(dots) || length(dots) == 0) {
    return(invisible(dots))
  }

  if (any(!nzchar(names2(dots)))) {
    cli::cli_abort(
      "All arguments in {.arg {arg}} must be named.",
      call = call
    )
  }

  invisible(dots)
}


check_list <- function(input, proto, path = NULL, closed = TRUE) {
  if (!is.list(input)) {
    cli::cli_abort(
      "{.var input} must be a list, not {.obj_type_friendly {input}}"
    )
  }

  if (!is.list(proto)) {
    cli::cli_abort(
      "{.var proto} must be a list, not {.obj_type_friendly {proto}}"
    )
  }

  # Check for items in input that aren't in the proto
  if (isTRUE(closed)) {
    extra_items <- setdiff(names(input), names(proto))
    if (length(extra_items) > 0) {
      field_path <- if (is.null(path)) "" else paste(path, collapse = ".")
      cli::cli_abort(
        "Unexpected fields in {.field {field_path}}: {.val {extra_items}}"
      )
    }
  }

  # Check that each item in input matches the type in proto
  for (name in names(input)) {
    input_item <- input[[name]]
    proto_item <- proto[[name]]

    if (is.null(input_item)) {
      # Skip null values
      next
    }

    if (isFALSE(closed) && is.null(proto_item)) {
      next
    }

    current_path <- c(path, name)

    if (is.list(proto_item)) {
      if (is.list(input_item)) {
        # Recursively check the nested list
        check_list(input_item, proto_item, current_path)
      } else {
        cli::cli_abort(c(
          "Invalid value for {.field {current_path}}:",
          "x" = "{.val {input_item}}",
          "i" = "Expected a list with items {.val {names(proto_item)}}."
        ))
      }
    } else {
      current_path <- paste(current_path, collapse = ".")

      if (is.function(proto_item)) {
        # Validator function
        check_proto_item <- proto_item # alias for traceback
        check_proto_item(input_item)
        next
      }

      # fmt: skip
      switch(
        proto_item,
        path = ,
        string = check_string(input_item, allow_null = TRUE, arg = current_path),
        character = check_character(input_item, allow_null = TRUE, arg = current_path),
        integer = check_number_whole(input_item, allow_null = TRUE, arg = current_path),
        numeric = check_number_decimal(input_item, allow_null = TRUE, arg = current_path),
        boolean = check_logical(input_item, allow_null = TRUE, arg = current_path),
        list = check_is_list(input_item, allow_null = TRUE, arg = current_path),
      )
    }
  }

  invisible(input)
}

check_is_list <- function(
  x,
  allow_null = FALSE,
  arg = NULL,
  allowed_names = NULL,
  all_named = FALSE
) {
  if (is.null(x) && allow_null) {
    return(invisible(x))
  }

  if (is.null(arg)) {
    arg <- deparse(substitute(x))
  }

  if (!is.list(x)) {
    cli::cli_abort(
      "{.var {arg}} must be a list, not {.obj_type_friendly {x}}",
      call = caller_call(),
    )
  }

  if (all_named) {
    if (is.null(names(x)) || !all(nzchar(names2(x)))) {
      cli::cli_abort(
        "All items in {.var {arg}} must be named.",
        call = caller_call()
      )
    }
  }

  if (!is.null(allowed_names)) {
    extra <- setdiff(names(x), allowed_names)
    if (length(extra)) {
      cli::cli_abort(
        c(
          "{.var {arg}} contains unexpected names: {.val {extra}}",
          "i" = "Allowed names: {.val {allowed_names}}"
        ),
        call = caller_call()
      )
    }
  }

  invisible(x)
}

check_enum <- function(
  x,
  values,
  ...,
  max_len = 1,
  allow_null = FALSE,
  allow_dups = FALSE,
  arg = caller_arg(x),
  call = caller_env()
) {
  if (allow_null && is_null(x)) {
    return(invisible(NULL))
  }

  check_number_whole(max_len, allow_infinite = TRUE)
  check_len <- is.finite(max_len)

  is_chr <- is.character(x)
  all_allowed <- if (length(x) > 0) all(map_lgl(x, `%in%`, values)) else FALSE
  is_valid_len <- if (check_len) length(x) <= max_len else length(x) > 0
  no_dups <- if (!allow_dups) identical(unique(x), x) else TRUE

  if (is_chr && all_allowed && is_valid_len && no_dups) {
    return(invisible(NULL))
  }

  values_label <- paste0("`", values, "`", collapse = ", ")

  how_many <-
    if (!check_len) {
      "one or more"
    } else if (max_len == 1) {
      "exactly one"
    } else {
      sprintf("at most %d", max_len)
    }

  msg <- sprintf("%s of %s", how_many, values_label)

  if (!is_chr) {
    stop_input_type(
      x,
      msg,
      ...,
      allow_na = FALSE,
      allow_null = allow_null,
      arg = arg,
      call = call
    )
  } else if (!all_allowed) {
    not_allowed <- unique(setdiff(x, values))
    cli::cli_abort(c(
      "{.arg {arg}} does not allow {.val {not_allowed}}.",
      "i" = "Values must be {how_many} of {.val {values}}."
    ))
  } else if (!is_valid_len) {
    cli::cli_abort(
      "{.arg {arg}} must have at most {max_len} item{?s}, not {length(x)} item{?s}."
    )
  } else if (!no_dups) {
    cli::cli_abort(c(
      "{.arg {arg}} must contain unique values.",
      "i" = "Duplicated values: {.val {unique(x[duplicated(x)])}}"
    ))
  }
}

check_string_or_list <- function(
  x,
  ...,
  allow_null = FALSE,
  arg = caller_arg(x),
  call = caller_env()
) {
  if (allow_null && is.null(x)) {
    return(invisible(NULL))
  }

  if (!is_string(x) && !is_list(x)) {
    stop_input_type(
      x,
      "either a string or a list",
      ...,
      allow_na = FALSE,
      allow_null = allow_null,
      arg = arg,
      call = call
    )
  }
}

check_string_or_number <- function(
  x,
  ...,
  allow_null = FALSE,
  arg = caller_arg(x),
  call = caller_env()
) {
  if (allow_null && is.null(x)) {
    return(invisible(NULL))
  }

  ok_string <- FALSE
  ok_number <- FALSE

  try(silent = TRUE, {
    check_string(x, allow_null = allow_null)
    ok_string <- TRUE
  })
  try(silent = TRUE, {
    check_number_decimal(x, allow_null = TRUE)
    ok_number <- TRUE
  })

  if (ok_string || ok_number) {
    return(invisible(NULL))
  }

  stop_input_type(
    x,
    "either a string or a number",
    ...,
    allow_na = FALSE,
    allow_null = allow_null,
    arg = arg,
    call = call
  )
}
