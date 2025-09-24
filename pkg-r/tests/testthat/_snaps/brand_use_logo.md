# brand_use_logo(): errors if logo doesn't exist and is required

    Code
      brand_use_logo(brand, name = "large", required = TRUE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.large` is required.
    Code
      brand_use_logo(brand, name = "large", required = "for header display")
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.large` is required for header display.

# brand_use_logo(): errors when variant is specified and required but not available and fallback not allowed

    Code
      brand_use_logo(brand, "small", variant = "light", required = TRUE,
        allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small` doesn't have a "light" variant, but `brand.logo.small.light` is required.
    Code
      brand_use_logo(brand, "small", variant = "dark", required = "for header display",
        allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small` doesn't have a "dark" variant, but `brand.logo.small.dark` is required for header display.
    Code
      brand_use_logo(brand, "large", variant = "light", required = "for light plot icons",
        allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.large.light` is required for light plot icons.

