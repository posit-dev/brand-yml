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
    Code
      brand_use_logo(brand, name = "tiny", required = TRUE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.images['tiny']` is required.

# brand_use_logo(): errors when variant is specified and required but not available and fallback not allowed

    Code
      brand_use_logo(brand, "small", variant = "light", required = TRUE,
        allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small.light` is required.
    Code
      brand_use_logo(brand, "small", variant = "dark", required = "for header display",
        allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small.dark` is required for header display.
    Code
      brand_use_logo(brand, "large", variant = "light", required = "for light plot icons",
        allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.large.light` is required for light plot icons.

# brand_use_logo(): errors when requesting light_dark with required=TRUE on non-light_dark logo without fallback

    Code
      brand_use_logo(brand, name = "small", variant = c("light", "dark"), required = TRUE,
      allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small` requires light/dark variants.
    Code
      brand_use_logo(brand, name = "small", variant = c("light", "dark"), required = "for theme support",
      allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small` requires light/dark variants for theme support.

