# Extract a logo resource from a brand

Returns a brand logo resource specified by name and variant from a brand
object. The image paths in the returned object are adjusted to be
absolute, relative to the location of the brand YAML file, if `brand`
was read from a file, or the local working directory otherwise.

## Usage

``` r
brand_use_logo(
  brand,
  name,
  variant = c("auto", "light", "dark", "light-dark"),
  ...,
  .required = !name %in% c("small", "medium", "large", "smallest", "largest"),
  .allow_fallback = TRUE
)
```

## Arguments

- brand:

  A brand object from
  [`read_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/read_brand_yml.md)
  or
  [`as_brand_yml()`](https://posit-dev.github.io/brand-yml/pkg/r/dev/reference/as_brand_yml.md).

- name:

  The name of the logo to use. Either a size (`"small"`, `"medium"`,
  `"large"`) or an image name from `brand.logo.images`. Alternatively,
  you can also use `"smallest"` or `"largest"` to select the smallest or
  largest available logo size, respectively.

- variant:

  Which variant to use, only used when `name` is one of the brand.yml
  fixed logo sizes (`"small"`, `"medium"`, or `"large"`). Can be one of:

  - `"auto"`: Auto-detect, returns a light/dark logo resource if both
    variants are present, otherwise it returns a single logo resource,
    either the value for `brand.logo.{name}` or the single light or dark
    variant if only one is present.

  - `"light"`: Returns only the light variant. If no light variant is
    present, but `brand.logo.{name}` is a single logo resource and
    `allow_fallback` is `TRUE`, `brand_use_logo()` falls back to the
    single logo resource.

  - `"dark"`: Returns only the dark variant, or, as above, falls back to
    the single logo resource if no dark variant is present and
    `allow_fallback` is `TRUE`.

  - `"light-dark"`: Returns a light/dark object with both variants. If a
    single logo resource is present for `brand.logo.{name}` and
    `allow_fallback` is `TRUE`, the single logo resource is promoted to
    a light/dark logo resource with identical light and dark variants.

- ...:

  Additional named attributes to be added to the image HTML or markdown
  when created via [`format()`](https://rdrr.io/r/base/format.html),
  [`knitr::knit_print()`](https://rdrr.io/pkg/knitr/man/knit_print.html),
  or
  [`htmltools::as.tags()`](https://rstudio.github.io/htmltools/reference/as.tags.html).

- .required:

  Logical or character string. If `TRUE`, an error is thrown if the
  requested logo is not found. If a string, it is used to describe why
  the logo is required in the error message and completes the phrase
  `"is required ____"`. Defaults to `FALSE` when `name` is one of the
  fixed sizes – `"small"`, `"medium"`, `"large"` or `"smallest"` or
  `"largest"`. Otherwise, an error is thrown by default if the requested
  logo is not found.

- .allow_fallback:

  If `TRUE` (the default), allows falling back to a non-variant-specific
  logo when a specific variant is requested. Only used when `name` is
  one of the fixed logo sizes (`"small"`, `"medium"`, or `"large"`).

## Value

A `brand_logo_resource` object, a `brand_logo_resource_light_dark`
object, or `NULL` if the requested logo doesn't exist and `.required` is
`FALSE`.

## Shiny apps and HTML documents

You can use `brand_use_logo()` to include logos in Shiny apps or in HTML
documents produced by
[Quarto](https://quarto.org/docs/output-formats/html-basics.html) or [R
Markdown](https://pkgs.rstudio.com/rmarkdown/reference/html_document.html).

In Shiny apps, logos returned by `brand_use_logo()` will automatically
be converted into HTML tags using
[`htmltools::as.tags()`](https://rstudio.github.io/htmltools/reference/as.tags.html),
so you can include them directly in your UI code.

    library(shiny)
    library(bslib)

    brand <- read_brand_yml()

    ui <- page_navbar(
      title = tagList(
        brand_use_logo(brand, "small"),
        "Brand Use Logo Test"
      ),
      nav_panel(
        "Page 1",
        card(
          card_header("My Brand"),
          brand_use_logo(brand, "medium", variant = "dark")
        )
      )
      # ... The rest of your app
    )

If your brand includes a light/dark variant for a specific size, both
images will be included in the app, but only the appropriate image will
be shown based on the user's system preference of the app's current
theme mode if you are using
[`bslib::input_dark_mode()`](https://rstudio.github.io/bslib/reference/input_dark_mode.html).

To include additional classes or attributes in the `<img>` tag, you can
call
[`htmltools::as.tags()`](https://rstudio.github.io/htmltools/reference/as.tags.html)
directly and provide those attributes:

    brand <- as_brand_yml(list(
      logo = list(
        images = list(
          "cat-light" = list(
            path = "https://placecats.com/louie/300/300",
            alt = "A light-colored tabby cat on a purple rug"
          ),
          "cat-dark" = list(
            path = "https://placecats.com/millie/300/300",
            alt = "A dark-colored cat looking into the camera"
          ),
          "cat-med" = "https://placecats.com/600/600"
        ),
        small = list(light = "cat-light", dark = "cat-dark"),
        medium = "cat-med"
      )
    ))

    brand_use_logo(brand, "small") |>
      htmltools::as.tags(class = "my-logo", height = 32)

![A light-colored tabby cat on a purple
rug](https://placecats.com/louie/300/300)![A dark-colored cat looking
into the camera](https://placecats.com/millie/300/300)

The same applies to HTML documents produced by Quarto or R Markdown,
where images can be used in-line:

    ```{r}
    brand_use_logo(brand, "small")
    ```

    This is my brand's medium sized logo: `r brand_use_logo(brand, "medium")`

Finally, you can use [`format()`](https://rdrr.io/r/base/format.html) to
convert the logo to raw HTML or markdown:

    cat(format(brand_use_logo(brand, "small", variant = "light")))
    #> <img src="https://placecats.com/louie/300/300" alt="A light-colored tabby cat on a purple rug" class="brand-logo"/>

    cat(format(
      brand_use_logo(brand, "medium"),
      .format = "markdown",
      class = "my-logo",
      height = 500
    ))
    #> ![](https://placecats.com/600/600){.brand-logo .my-logo alt="" height="500"}

## Examples

``` r
brand <- as_brand_yml(list(
  logo = list(
    images = list(
      small = "logos/small.png",
      huge = list(path = "logos/huge.png", alt = "Huge Logo")
    ),
    small = "small",
    medium = list(
      light = list(
        path = "logos/medium-light.png",
        alt = "Medium Light Logo"
      ),
      dark = list(path = "logos/medium-dark.png")
    )
  )
))

brand_use_logo(brand, "small")
#> <brand_logo_resource src="./logos/small.png" alt="">
brand_use_logo(brand, "medium")
#> <brand_logo_resource src="./logos/medium-light.png" alt="Medium Light Logo" variant="light">
#> <brand_logo_resource src="./logos/medium-dark.png" alt="" variant="dark">
brand_use_logo(brand, "large")
#> NULL
brand_use_logo(brand, "huge")
#> <brand_logo_resource src="./logos/huge.png" alt="Huge Logo">

brand_use_logo(brand, "small", variant = "light")
#> <brand_logo_resource src="./logos/small.png" alt="">
brand_use_logo(brand, "small", variant = "light", allow_fallback = FALSE)
#> <brand_logo_resource src="./logos/small.png" alt="" allow_fallback="false">
brand_use_logo(brand, "small", variant = "light-dark")
#> <brand_logo_resource src="./logos/small.png" alt="" variant="light">
#> <brand_logo_resource src="./logos/small.png" alt="" variant="dark">
brand_use_logo(
  brand,
  "small",
  variant = "light-dark",
  allow_fallback = FALSE
)
#> <brand_logo_resource src="./logos/small.png" alt="" variant="light">
#> <brand_logo_resource src="./logos/small.png" alt="" variant="dark">

brand_use_logo(brand, "medium", variant = "light")
#> <brand_logo_resource src="./logos/medium-light.png" alt="Medium Light Logo">
brand_use_logo(brand, "medium", variant = "dark")
#> <brand_logo_resource src="./logos/medium-dark.png" alt="">
brand_use_logo(brand, "medium", variant = "light-dark")
#> <brand_logo_resource src="./logos/medium-light.png" alt="Medium Light Logo" variant="light">
#> <brand_logo_resource src="./logos/medium-dark.png" alt="" variant="dark">
```
