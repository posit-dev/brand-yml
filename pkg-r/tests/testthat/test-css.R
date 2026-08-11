describe("brand_css_variables()", {
  brand <- as_brand_yml(list(
    color = list(
      palette = list(red = "#ff0000"),
      foreground = list(light = "#111111", dark = "#eeeeee"),
      background = list(light = "#ffffff", dark = "#222222"),
      primary = "#0066cc"
    ),
    typography = list(
      headings = list(color = "foreground"),
      link = list(
        color = list(light = "primary", dark = "#66b2ff")
      )
    )
  ))

  it("uses root and system preference scopes by default", {
    css <- brand_css_variables(brand)

    expect_match(css, ":root {", fixed = TRUE)
    expect_match(css, "--brand-red: #ff0000;", fixed = TRUE)
    expect_match(css, "--brand-color-foreground: #111111;", fixed = TRUE)
    expect_match(
      css,
      "--brand-typography-headings-color: #111111;",
      fixed = TRUE
    )
    expect_match(
      css,
      "@media (prefers-color-scheme: dark)",
      fixed = TRUE
    )
    expect_match(css, "--brand-color-background: #222222;", fixed = TRUE)
    expect_match(
      css,
      "--brand-typography-link-color: #66b2ff;",
      fixed = TRUE
    )
  })

  it("uses custom selectors", {
    css <- brand_css_variables(
      brand,
      mode_scopes = list(
        light = ".quarto-light",
        dark = ".quarto-dark"
      )
    )

    expect_match(css, ".quarto-light {", fixed = TRUE)
    expect_match(css, ".quarto-dark {", fixed = TRUE)
    expect_false(grepl("@media", css, fixed = TRUE))
  })

  it("uses the branch name for prefers-color-scheme", {
    css <- brand_css_variables(
      brand,
      mode_scopes = list(
        light = "prefers-color-scheme",
        dark = ""
      )
    )

    expect_match(
      css,
      "@media (prefers-color-scheme: light)",
      fixed = TRUE
    )
  })

  it("validates mode scopes", {
    expect_error(
      brand_css_variables(brand, mode_scopes = list(light = "")),
      "light.*dark"
    )
    expect_error(
      brand_css_variables(
        brand,
        mode_scopes = list(light = "", dark = 42)
      ),
      "mode_scopes.dark"
    )
  })

  it("omits partial color overrides from an undefined mode", {
    partial <- as_brand_yml(list(
      color = list(
        foreground = list(dark = "#eeeeee")
      ),
      typography = list(
        headings = list(color = "foreground")
      )
    ))

    css <- brand_css_variables(
      partial,
      mode_scopes = list(light = ".light", dark = ".dark")
    )
    light <- strsplit(css, "\n.dark \\{")[[1]][1]
    dark <- strsplit(css, "\n.dark \\{")[[1]][2]

    expect_false(grepl("--brand-color-foreground:", light, fixed = TRUE))
    expect_false(
      grepl("--brand-typography-headings-color:", light, fixed = TRUE)
    )
    expect_match(dark, "--brand-color-foreground: #eeeeee;", fixed = TRUE)
    expect_match(
      dark,
      "--brand-typography-headings-color: #eeeeee;",
      fixed = TRUE
    )
  })
})
