# brand.typography validation errors

    Code
      as_brand_yml(list(typography = list(fonts = "foo")))
    Condition
      Error in `check_list()`:
      ! `typography.fonts` must be a list, not a string
    Code
      as_brand_yml(list(typography = list(fonts = list(source = "bad"))))
    Condition
      Error in `brand_typography_fonts_check()`:
      ! `typography.fonts[1]` must be a list, not a string
    Code
      as_brand_yml(list(typography = list(fonts = list(source = TRUE))))
    Condition
      Error in `brand_typography_fonts_check()`:
      ! `typography.fonts[1]` must be a list, not `TRUE`

---

    Code
      as_brand_yml(list(typography = list(fonts = list(list(source = "bad")))))
    Condition
      Error in `brand_typography_fonts_check()`:
      ! `typography.fonts[1]` must include both `family` and `source`.
    Code
      as_brand_yml(list(typography = list(fonts = list(list(family = 42)))))
    Condition
      Error in `check_list()`:
      ! `typography.fonts[1].family` must be a single string or `NULL`, not the number 42.
    Code
      as_brand_yml(list(typography = list(fonts = list(list(weight = 400)))))
    Condition
      Error in `brand_typography_fonts_check()`:
      ! `typography.fonts[1]` must include both `family` and `source`.
    Code
      as_brand_yml(list(typography = list(fonts = list(list(family = "foo", source = "bad")))))
    Condition
      Error in `check_enum()`:
      ! `font$source` does not allow "bad".
      i Values must be exactly one of "system", "file", "google", and "bunny".

---

    Code
      as_brand_yml(list(typography = list(bad = "foo")))
    Condition
      Error in `check_list()`:
      ! Unexpected fields in typography: "bad"
    Code
      as_brand_yml(list(typography = list(base = list(family = 42))))
    Condition
      Error in `check_list()`:
      ! `typography.base.family` must be a single string or `NULL`, not the number 42.
    Code
      as_brand_yml(list(typography = list(base = list(size = 42))))
    Condition
      Error in `check_list()`:
      ! `typography.base.size` must be a single string or `NULL`, not the number 42.
    Code
      as_brand_yml(list(typography = list(base = list(size = 42))))
    Condition
      Error in `check_list()`:
      ! `typography.base.size` must be a single string or `NULL`, not the number 42.
    Code
      as_brand_yml(list(typography = list(base = list(color = "red"))))
    Condition
      Error in `brand_typography_check_allowed_color_fields()`:
      ! The following fields are not allowed in brand.yml: typography.base.color.
    Code
      as_brand_yml(list(typography = list(base = list(`background-color` = "red"))))
    Condition
      Error in `brand_typography_check_allowed_color_fields()`:
      ! The following fields are not allowed in brand.yml: typography.base.background-color.
    Code
      as_brand_yml(list(typography = list(base = list(weight = "bad"))))
    Condition
      Error in `check_enum()`:
      ! `typography.base.weight` does not allow "bad".
      i Values must be exactly one of "thin", "extra-light", "ultra-light", "light", "normal", "regular", "medium", "semi-bold", "demi-bold", "bold", "extra-bold", "ultra-bold", and "black".
    Code
      as_brand_yml(list(typography = list(base = list(weight = 100.5))))
    Condition
      Error in `check_proto_item()`:
      ! `typography.base.weight` must be a whole number, not the number 100.5.
    Code
      as_brand_yml(list(typography = list(base = list(`line-height` = NA))))
    Condition
      Error in `check_proto_item()`:
      ! `typography.base.line-height` must be either a string or a number, not `NA`.
    Code
      as_brand_yml(list(typography = list(headings = list(style = "bad"))))
    Condition
      Error in `check_enum()`:
      ! `typography.headings.bad` does not allow "bad".
      i Values must be at most 2 of "normal" and "italic".
    Code
      as_brand_yml(list(typography = list(headings = list(style = rep("normal", 2)))))
    Condition
      Error in `check_enum()`:
      ! `typography.headings.normal.normal` must contain unique values.
      i Duplicated values: "normal"
    Code
      as_brand_yml(list(typography = list(headings = list(color = 42))))
    Condition
      Error in `check_list()`:
      ! `typography.headings.color` must be a single string or `NULL`, not the number 42.

# brand.typography CSS fonts

    Code
      cat(format(brand_fonts_sass_layer))
    Output
      $brand-font-open-sans: 'Open Sans', 'Open Sans' !default;
      $brand-font-closed-sans: 'Closed Sans', 'Closed Sans' !default;
      $brand-font-roboto-slab: 'Roboto Slab' !default;
      $brand-font-fira-code: 'Fira Code' !default;
      .brand-font-open-sans { font-family: $brand-font-open-sans; }
      .brand-font-closed-sans { font-family: $brand-font-closed-sans; }
      .brand-font-roboto-slab { font-family: $brand-font-roboto-slab; }
      .brand-font-fira-code { font-family: $brand-font-fira-code; }

