# Helper function to combine multiple flextable objects into a single HTML output
combine_flextables_html <- function(..., titles = NULL, preview = TRUE) {
  # Check if htmltools is installed
  if (!requireNamespace("htmltools", quietly = TRUE)) {
    warning("htmltools package is required to combine flextables into HTML.")
    return(invisible())
  }

  # Get the list of flextables from dots
  ft_list <- list(...)

  # If titles not provided, create generic ones
  if (is.null(titles) || length(titles) != length(ft_list)) {
    titles <- paste("Table", seq_along(ft_list))
  }

  # Create a list of HTML elements for each flextable
  html_elements <- lapply(seq_along(ft_list), function(i) {
    ft <- ft_list[[i]]
    title <- titles[i]

    # Skip if not a flextable object
    if (!inherits(ft, "flextable")) {
      return(NULL)
    }

    # Create an HTML div with a title and the flextable
    htmltools::div(
      htmltools::h3(title),
      flextable::htmltools_value(ft),
      htmltools::hr(),
      style = "margin-bottom: 30px;"
    )
  })

  # Filter out NULL elements
  html_elements <- html_elements[!sapply(html_elements, is.null)]

  # Combine all elements into a single HTML document
  result <- htmltools::tagList(
    htmltools::tags$head(
      htmltools::tags$style("
        body { font-family: Arial, sans-serif; }
        h3 { margin-top: 20px; }
      ")
    ),
    htmltools::h2("Flextable Theme Tests"),
    html_elements
  )

  # If preview is TRUE, display HTML in the viewer pane
  if (preview) {
    # Create a temporary HTML file
    tmp_file <- tempfile(fileext = ".html")

    # Save the HTML to the file
    html_content <- as.character(result)
    writeLines(html_content, tmp_file)

    # Check if we're in RStudio/Positron
    viewer <- getOption("viewer")
    if (!is.null(viewer) && is.function(viewer)) {
      # Use the RStudio/Positron viewer
      viewer(tmp_file)
      message("HTML preview opened in the viewer pane")
    } else if (interactive()) {
      # Fallback to browser for interactive sessions not in RStudio/Positron
      utils::browseURL(tmp_file)
      message("HTML preview opened in your default web browser")
    } else {
      # Just provide the file path in non-interactive sessions
      message("HTML file saved to: ", tmp_file)
    }
  }

  return(result)
}

test_that("theme_brand_ggplot2", {
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

  # Verify that the last applied theme takes precedence
  # Background color should match the dark theme
  expect_equal(plot_both$theme$rect$fill, dark_theme$rect$fill)
})

test_that("theme_colors_ggplot2", {
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

  # Verify that the last applied theme takes precedence
  # Background color should match the dark theme
  expect_equal(plot_both$theme$rect$fill, dark_colors_theme$rect$fill)
})

test_that("theme_brand_flextable", {
  skip_if_not_installed("flextable")
  skip_if_not_installed("htmltools")

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

  # Create a flextable for visual testing
  library(flextable)
  ft <- flextable(airquality[sample.int(nrow(airquality), 10),])
  ft <- add_header_row(
    ft,
    colwidths = c(4, 2),
    values = c("Air quality", "Time")
  )
  ft <- flextable::theme_vanilla(ft)
  ft <- add_footer_lines(ft, "Daily air quality measurements in New York, May to September 1973.")
  ft <- color(ft, part = "footer", color = "#666666")
  ft <- set_caption(ft, caption = "New York Air Quality Measurements")

  # Apply themes but don't print individually
  light_ft <- ft |> light_theme()
  dark_ft <- ft |> dark_theme()
  both_ft <- ft |> light_theme() |> dark_theme()

  # Create a combined HTML display of all tables
  all_tables <- combine_flextables_html(
    light_ft, dark_ft,
    titles = c(
      "Light theme using theme_brand_flextable with brand-posit.yml",
      "Dark theme using theme_brand_flextable with brand-posit-dark.yml"
    )
  )

  # Print combined HTML output once
  cat("\n\n")
  print(all_tables)
  cat("\n\n")
})

test_that("theme_colors_flextable", {
  skip_if_not_installed("flextable")
  skip_if_not_installed("htmltools")

  # Use colors consistent with our brand YAML files
  light_bg <- "#FFFFFF"
  light_fg <- "#151515"

  dark_bg <- "#1A1A1A"
  dark_fg <- "#F1F1F2"

  # Create themes with direct colors
  light_colors_theme <- theme_colors_flextable(bg = light_bg, fg = light_fg)
  dark_colors_theme <- theme_colors_flextable(bg = dark_bg, fg = dark_fg)

  # Verify themes are functions
  expect_type(light_colors_theme, "closure")
  expect_type(dark_colors_theme, "closure")

  # Create a flextable for visual testing
  library(flextable)
  ft <- flextable(airquality[sample.int(nrow(airquality), 10),])
  ft <- add_header_row(
    ft,
    colwidths = c(4, 2),
    values = c("Air quality", "Time")
  )
  ft <- flextable::theme_vanilla(ft)
  ft <- add_footer_lines(ft, "Daily air quality measurements in New York, May to September 1973.")
  ft <- color(ft, part = "footer", color = "#666666")
  ft <- set_caption(ft, caption = "New York Air Quality Measurements")

  # Apply themes but don't print individually
  light_ft <- ft |> light_colors_theme()
  dark_ft <- ft |> dark_colors_theme()
  both_ft <- ft |> light_colors_theme() |> dark_colors_theme()

  # Create a combined HTML display of all tables
  all_tables <- combine_flextables_html(
    light_ft, dark_ft,
    titles = c(
      "Light theme using theme_colors_flextable with direct colors",
      "Dark theme using theme_colors_flextable with direct colors"
    )
  )

  # Print combined HTML output once
  cat("\n\n")
  print(all_tables)
  cat("\n\n")
})

test_that("theme_brand_gt", {
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

test_that("theme_colors_gt", {
  skip_if_not_installed("gt")

  # Create themes with direct colors
  light_colors_theme <- theme_colors_gt(bg = "#FFFFFF", fg = "#151515")
  dark_colors_theme <- theme_colors_gt(bg = "#1A1A1A", fg = "#F1F1F2")

  # Verify themes are functions
  expect_type(light_colors_theme, "closure")
  expect_type(dark_colors_theme, "closure")
})

test_that("theme_brand_plotly", {
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

test_that("theme_colors_plotly", {
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

test_that("theme_brand_thematic", {
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

test_that("theme_colors_thematic", {
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