test_that("theme_brand_ggplot2 creates valid themes from brand.yml files", {
  skip_if_not_installed("ggplot2", "4.0.0")

  # Test with light theme (uses orange accent from brand-posit.yml)
  posit_light <- test_example("brand-posit.yml")
  light_theme <- theme_brand_ggplot2(posit_light)

  # Verify light theme created successfully
  expect_s3_class(light_theme, c("theme", "gg"))
  expect_type(light_theme, "list")

  # Test with dark theme (uses burgundy accent from brand-posit-dark.yml)
  posit_dark <- test_example("brand-posit-dark.yml")
  dark_theme <- theme_brand_ggplot2(posit_dark)

  # Verify dark theme created successfully
  expect_s3_class(dark_theme, c("theme", "gg"))
  expect_type(dark_theme, "list")

  # Test application to a ggplot
  library(ggplot2)
  plot_base <- ggplot(mtcars, aes(mpg, wt)) +
    geom_point() +
    geom_smooth(method = "lm")

  # Apply each theme and ensure no errors
  expect_no_error(plot_light <- plot_base + light_theme)
  # Display the light theme plot
  print(plot_light)
  cat("\n\nAbove: Light theme plot using theme_brand_ggplot2 with orange accent from brand-posit.yml\n\n")

  expect_no_error(plot_dark <- plot_base + dark_theme)
  # Display the dark theme plot
  print(plot_dark)
  cat("\n\nAbove: Dark theme plot using theme_brand_ggplot2 with burgundy accent from brand-posit-dark.yml\n\n")

  # Verify sequential theme application (applying both themes)
  expect_no_error(plot_both <- plot_base + light_theme + dark_theme)
  # Display the combined theme plot

  # Verify that the last applied theme takes precedence
  # Background color should match the dark theme
  expect_equal(plot_both$theme$rect$fill, dark_theme$rect$fill)
})

test_that("theme_colors_ggplot2 creates valid themes from direct color specs", {
  skip_if_not_installed("ggplot2", "4.0.0")

  # Use actual accent colors from the brand YAML files
  # Orange from brand-posit.yml for light theme
  light_orange_accent <- "#EE6331"
  # Burgundy from brand-posit-dark.yml for dark theme
  dark_burgundy_accent <- "#C96B8C"

  # Create themes with direct colors and the specific accents
  light_colors_theme <- theme_colors_ggplot2(bg = "#FFFFFF", fg = "#151515", accent = light_orange_accent)
  dark_colors_theme <- theme_colors_ggplot2(bg = "#1A1A1A", fg = "#F1F1F2", accent = dark_burgundy_accent)

  # Verify themes created successfully
  expect_s3_class(light_colors_theme, c("theme", "gg"))
  expect_type(light_colors_theme, "list")
  expect_s3_class(dark_colors_theme, c("theme", "gg"))
  expect_type(dark_colors_theme, "list")

  # Test application to a ggplot
  library(ggplot2)
  plot_base <- ggplot(mtcars, aes(mpg, wt)) +
    geom_point() +
    geom_smooth(method = "lm")

  # Apply each theme and ensure no errors
  expect_no_error(plot_light <- plot_base + light_colors_theme)
  # Display the light colors theme plot
  print(plot_light)
  cat("\n\nAbove: Light theme plot using theme_colors_ggplot2 with orange accent (#EE6331)\n\n")

  expect_no_error(plot_dark <- plot_base + dark_colors_theme)
  # Display the dark colors theme plot
  print(plot_dark)
  cat("\n\nAbove: Dark theme plot using theme_colors_ggplot2 with burgundy accent (#C96B8C)\n\n")

  # Verify sequential theme application (applying both themes)
  expect_no_error(plot_both <- plot_base + light_colors_theme + dark_colors_theme)
  # Display the combined theme plot
  print(plot_both)
  cat("\n\nAbove: Combined plot with light (orange) theme followed by dark (burgundy) theme\n\n")

  # Verify that the last applied theme takes precedence
  # Background color should match the dark theme
  expect_equal(plot_both$theme$rect$fill, dark_colors_theme$rect$fill)
})

test_that("theme_brand_flextable creates valid themes from brand.yml files", {
  skip_if_not_installed("flextable")

  # Test with light theme
  posit_light <- test_example("brand-posit.yml")
  light_theme <- theme_brand_flextable(posit_light)

  # Verify light theme is a function
  expect_type(light_theme, "closure")

  # Test with dark theme
  posit_dark <- test_example("brand-posit-dark.yml")
  dark_theme <- theme_brand_flextable(posit_dark)

  # Verify dark theme is a function
  expect_type(dark_theme, "closure")
})

test_that("theme_colors_flextable creates valid themes from direct color specs", {
  skip_if_not_installed("flextable")

  # Create themes with direct colors
  light_colors_theme <- theme_colors_flextable(bg = "#FFFFFF", fg = "#151515")
  dark_colors_theme <- theme_colors_flextable(bg = "#1A1A1A", fg = "#F1F1F2")

  # Verify themes are functions
  expect_type(light_colors_theme, "closure")
  expect_type(dark_colors_theme, "closure")
})

test_that("theme_brand_gt creates valid themes from brand.yml files", {
  skip_if_not_installed("gt")

  # Test with light theme
  posit_light <- test_example("brand-posit.yml")
  light_theme <- theme_brand_gt(posit_light)

  # Verify light theme is a function
  expect_type(light_theme, "closure")

  # Test with dark theme
  posit_dark <- test_example("brand-posit-dark.yml")
  dark_theme <- theme_brand_gt(posit_dark)

  # Verify dark theme is a function
  expect_type(dark_theme, "closure")
})

test_that("theme_colors_gt creates valid themes from direct color specs", {
  skip_if_not_installed("gt")

  # Create themes with direct colors
  light_colors_theme <- theme_colors_gt(bg = "#FFFFFF", fg = "#151515")
  dark_colors_theme <- theme_colors_gt(bg = "#1A1A1A", fg = "#F1F1F2")

  # Verify themes are functions
  expect_type(light_colors_theme, "closure")
  expect_type(dark_colors_theme, "closure")
})

test_that("theme_brand_plotly creates valid themes from brand.yml files", {
  skip_if_not_installed("plotly")

  # Test with light theme
  posit_light <- test_example("brand-posit.yml")
  light_theme <- theme_brand_plotly(posit_light)

  # Verify light theme is a function
  expect_type(light_theme, "closure")

  # Test with dark theme
  posit_dark <- test_example("brand-posit-dark.yml")
  dark_theme <- theme_brand_plotly(posit_dark)

  # Verify dark theme is a function
  expect_type(dark_theme, "closure")
})

test_that("theme_colors_plotly creates valid themes from direct color specs", {
  skip_if_not_installed("plotly")

  # Use actual accent colors from the brand YAML files
  light_orange_accent <- "#EE6331"  # Orange from brand-posit.yml
  dark_burgundy_accent <- "#C96B8C" # Burgundy from brand-posit-dark.yml

  # Create themes with direct colors and specific accents
  light_colors_theme <- theme_colors_plotly(bg = "#FFFFFF", fg = "#151515", accent = light_orange_accent)
  dark_colors_theme <- theme_colors_plotly(bg = "#1A1A1A", fg = "#F1F1F2", accent = dark_burgundy_accent)

  # Verify themes are functions
  expect_type(light_colors_theme, "closure")
  expect_type(dark_colors_theme, "closure")
})

test_that("theme_brand_thematic creates valid themes from brand.yml files", {
  skip_if_not_installed("thematic")

  # Test with light theme
  posit_light <- test_example("brand-posit.yml")
  light_theme <- theme_brand_thematic(posit_light)

  # Verify light theme is a function
  expect_type(light_theme, "closure")

  # Test with dark theme
  posit_dark <- test_example("brand-posit-dark.yml")
  dark_theme <- theme_brand_thematic(posit_dark)

  # Verify dark theme is a function
  expect_type(dark_theme, "closure")
})

test_that("theme_colors_thematic creates valid themes from direct color specs", {
  skip_if_not_installed("thematic")

  # Use actual accent colors from the brand YAML files
  light_orange_accent <- "#EE6331"  # Orange from brand-posit.yml
  dark_burgundy_accent <- "#C96B8C" # Burgundy from brand-posit-dark.yml

  # Create themes with direct colors and specific accents
  light_colors_theme <- theme_colors_thematic(bg = "#FFFFFF", fg = "#151515", accent = light_orange_accent)
  dark_colors_theme <- theme_colors_thematic(bg = "#1A1A1A", fg = "#F1F1F2", accent = dark_burgundy_accent)

  # Verify themes are functions
  expect_type(light_colors_theme, "closure")
  expect_type(dark_colors_theme, "closure")
})