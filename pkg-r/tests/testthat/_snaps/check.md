# check_enum(): fails with an invalid single value

    Code
      test_check_enum("X", values = letters[1:5])
    Condition
      Error in `check_enum()`:
      ! `input` does not allow "X".
      i Values must be exactly one of "a", "b", "c", "d", and "e".

# check_enum(): fails with multiple values exceeding max_len

    Code
      test_check_enum(c("a", "b", "c"), values = letters[1:5], max_len = 2)
    Condition
      Error in `check_enum()`:
      ! `input` must have at most 2 items, not 3 items.

# check_enum(): fails with NULL when allow_null = FALSE

    Code
      test_check_enum(NULL, values = letters[1:5], allow_null = FALSE)
    Condition
      Error in `test_check_enum()`:
      ! `input` must be exactly one of `a`, `b`, `c`, `d`, `e`, not `NULL`.

# check_enum(): fails with duplicates when allow_dups = FALSE

    Code
      test_check_enum(c("a", "a"), values = letters[1:5], allow_dups = FALSE)
    Condition
      Error in `check_enum()`:
      ! `input` must have at most 1 item, not 2 items.

