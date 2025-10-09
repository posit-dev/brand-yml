# brand_use_logo(): errors if logo doesn't exist and is required

    Code
      brand_use_logo(brand, name = "large", .required = TRUE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.large` is required.
    Code
      brand_use_logo(brand, name = "large", .required = "for header display")
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.large` is required for header display.
    Code
      brand_use_logo(brand, name = "tiny")
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.images['tiny']` is required.

# brand_use_logo(): handles errors for smallest/largest when no logos available

    Code
      brand_use_logo(brand_no_logos, name = "smallest", .required = TRUE)
    Condition
      Error in `brand_use_logo()`:
      ! No logos are available to satisfy `smallest` in `brand.logo` or `brand.logo.images`.
    Code
      brand_use_logo(brand_no_logos, name = "largest", .required = "for header display")
    Condition
      Error in `brand_use_logo()`:
      ! No logos are available to satisfy `largest` in `brand.logo` or `brand.logo.images` for header display.

# brand_use_logo(): errors when variant is specified and required but not available and fallback not allowed

    Code
      brand_use_logo(brand, "small", variant = "light", .required = TRUE,
        .allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small.light` is required.
    Code
      brand_use_logo(brand, "small", variant = "dark", .required = "for header display",
        .allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small.dark` is required for header display.
    Code
      brand_use_logo(brand, "large", variant = "light", .required = "for light plot icons",
        .allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.large.light` is required for light plot icons.

# brand_use_logo(): errors when requesting light_dark with required=TRUE on non-light_dark logo without fallback

    Code
      brand_use_logo(brand, name = "small", variant = "light-dark", .required = TRUE,
        .allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small` requires light/dark variants.
    Code
      brand_use_logo(brand, name = "small", variant = "light-dark", .required = "for theme support",
        .allow_fallback = FALSE)
    Condition
      Error in `brand_use_logo()`:
      ! `brand.logo.small` requires light/dark variants for theme support.

# format() method for brand_logo_resource: formats as HTML by default

    Code
      cat(format(logo_resource))
    Output
      <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" alt="Test logo" class="brand-logo"/>

# format() method for brand_logo_resource: formats as HTML with additional attributes

    Code
      cat(format(logo_resource, class = "my-logo", width = 100, height = 50))
    Output
      <img alt="Test logo" class="brand-logo my-logo" height="50" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" width="100"/>

# format() method for brand_logo_resource: formats as markdown

    Code
      cat(format(logo_resource, .format = "markdown"))
    Output
      ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo alt="Test logo"}

# format() method for brand_logo_resource: formats as markdown with additional attributes

    Code
      cat(format(logo_resource, .format = "markdown", class = "my-logo", width = 100))
    Output
      ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo .my-logo alt="Test logo" width="100"}

# format() method for brand_logo_resource_light_dark: formats as HTML by default

    Code
      cat(format(logo_light_dark))
    Output
      <span class="brand-logo-light-dark">
        <img alt="Light logo" class="brand-logo light-content" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="/>
        <img alt="Dark logo" class="brand-logo dark-content" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="/>
      </span>

# format() method for brand_logo_resource_light_dark: formats as HTML with additional attributes

    Code
      cat(format(logo_light_dark, class = "my-logo", width = 100, height = 50))
    Output
      <span class="brand-logo-light-dark">
        <img alt="Light logo" class="brand-logo light-content my-logo" height="50" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" width="100"/>
        <img alt="Dark logo" class="brand-logo dark-content my-logo" height="50" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" width="100"/>
      </span>

# format() method for brand_logo_resource_light_dark: formats as markdown

    Code
      cat(format(logo_light_dark, .format = "markdown"))
    Output
      ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo .light-content alt="Light logo"} ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo .dark-content alt="Dark logo"}

# format() method for brand_logo_resource_light_dark: formats as markdown with additional attributes

    Code
      cat(format(logo_light_dark, .format = "markdown", class = "my-logo", width = 100))
    Output
      ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo .light-content .my-logo alt="Light logo" width="100"} ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo .dark-content .my-logo alt="Dark logo" width="100"}

# format() method for brand_logo_resource_light_dark: handles a vector of classes

    Code
      cat(format(logo_light_dark, .format = "markdown", class = c("my-logo",
        "my-logo-other")))
    Output
      ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo .light-content .my-logo .my-logo-other alt="Light logo"} ![](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==){.brand-logo .dark-content .my-logo .my-logo-other alt="Dark logo"}

# as.tags() method: converts brand_logo_resource to HTML tags

    Code
      cat(format(logo_resource, .format = "html"))
    Output
      <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" alt="Test logo" class="brand-logo"/>

---

    Code
      cat(format(logo_resource, .format = "html", class = "custom-logo", width = 200))
    Output
      <img alt="Test logo" class="brand-logo custom-logo" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" width="200"/>

# as.tags() method: converts brand_logo_resource_light_dark to HTML tags

    Code
      cat(format(logo_light_dark, .format = "html"))
    Output
      <span class="brand-logo-light-dark">
        <img alt="Light logo" class="brand-logo light-content" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="/>
        <img alt="Dark logo" class="brand-logo dark-content" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="/>
      </span>

---

    Code
      cat(format(logo_light_dark, .format = "html", class = "custom-logo", width = 200))
    Output
      <span class="brand-logo-light-dark">
        <img alt="Light logo" class="brand-logo light-content custom-logo" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" width="200"/>
        <img alt="Dark logo" class="brand-logo dark-content custom-logo" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" width="200"/>
      </span>

# knit_print() method: renders brand_logo_resource in knitr

    Code
      cat(result$out)
    Output
      <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" alt="Test logo" class="brand-logo"/>

# knit_print() method: renders brand_logo_resource_light_dark in knitr

    Code
      cat(result$out)
    Output
      <span class="brand-logo-light-dark">
        <img alt="Light logo" class="brand-logo light-content" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="/>
        <img alt="Dark logo" class="brand-logo dark-content" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="/>
      </span>

