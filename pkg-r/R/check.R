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
      cli::cli_abort(c(
        "Unexpected fields in {.field {field_path}}:",
        "x" = "{.val {extra_items}}"
      ))
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
        proto_item(input_item)
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
  allow_null = FALSE,
  arg = caller_arg(x),
  call = caller_env()
) {
  if (!missing(x)) {
    if (is.character(x) && length(x) == 1 && x %in% values) {
      return(invisible(NULL))
    }
    if (allow_null && is_null(x)) {
      return(invisible(NULL))
    }
  }

  values_label <- paste0("`", values, "`", collapse = ", ")
  msg <- sprintf("one of %s", values_label)

  stop_input_type(
    x,
    msg,
    ...,
    allow_na = FALSE,
    allow_null = allow_null,
    arg = arg,
    call = call
  )
}

check_string_or_list <- function(
  x,
  ...,
  allow_null = FALSE,
  arg = caller_arg(x),
  call = caller_env()
) {
  if (allow_null && is.null(x)) return(invisible(NULL))

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
