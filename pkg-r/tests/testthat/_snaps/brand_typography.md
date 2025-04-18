# brand.typography validation errors

    Code
      as_brand_yml(list(typography = list(fonts = "foo")))
    Condition
      Error in `brand_typography_fonts_check()`:
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
      Error in `brand_typography_fonts_check()`:
      ! `font$source` must be one of `system`, `file`, `google`, `bunny`, not the string "bad".

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

