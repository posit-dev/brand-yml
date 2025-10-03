# Helper function to combine multiple HTML widgets (tables) into a single HTML output
combine_html_widgets <- function(..., titles = NULL, preview = TRUE, title = "Theme Tests") {
  # Check if htmltools is installed
  if (!requireNamespace("htmltools", quietly = TRUE)) {
    warning("htmltools package is required to combine tables into HTML.")
    return(invisible())
  }

  # Get the list of tables from dots
  table_list <- list(...)

  # If titles not provided, create generic ones
  if (is.null(titles) || length(titles) != length(table_list)) {
    titles <- paste("Table", seq_along(table_list))
  }

  # Create a list of HTML elements for each table
  html_elements <- lapply(seq_along(table_list), function(i) {
    tbl <- table_list[[i]]
    title <- titles[i]

    # Skip if NULL
    if (is.null(tbl)) {
      return(NULL)
    }

    # Create an HTML div with a title and the table
    # Handle both flextable and gt objects
    if (inherits(tbl, "flextable")) {
      table_html <- flextable::htmltools_value(tbl)
    } else if (inherits(tbl, "gt_tbl")) {
      table_html <- gt::as_raw_html(tbl)
    } else {
      warning("Object type not supported for HTML preview: ", class(tbl)[1])
      return(NULL)
    }

    htmltools::div(
      htmltools::h3(title),
      table_html,
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
    htmltools::h2(title),
    html_elements
  )

  # If preview is TRUE, display HTML in the viewer pane
  if (preview) {
    # Create a temporary HTML file
    tmp_file <- tempfile(fileext = ".html")

    # Use a simpler approach to save the HTML
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

  # Create and preview a combined HTML display of all tables (output goes to viewer)
  invisible(combine_html_widgets(
    light_ft, dark_ft,
    titles = c(
      "Light theme using theme_brand_flextable with brand-posit.yml",
      "Dark theme using theme_brand_flextable with brand-posit-dark.yml"
    ),
    title = "Flextable Theme Tests"
  ))
})

test_that("theme_colors_flextable", {
  skip_if_not_installed("flextable")
  skip_if_not_installed("htmltools")

  # Use fun, playful colors for our themes
  candy_bg <- "#FFCCE5"  # Soft pink
  candy_fg <- "#8A2BE2"  # Blueviolet

  cosmic_bg <- "#0A043C"  # Deep space blue
  cosmic_fg <- "#03FCA1"  # Neon green

  # Create themes with fun colors
  light_colors_theme <- theme_colors_flextable(bg = candy_bg, fg = candy_fg)
  dark_colors_theme <- theme_colors_flextable(bg = cosmic_bg, fg = cosmic_fg)

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

  # Create and preview a combined HTML display of all tables (output goes to viewer)
  invisible(combine_html_widgets(
    light_ft, dark_ft,
    titles = c(
      "Candy theme using theme_colors_flextable (Pink & Purple)",
      "Cosmic theme using theme_colors_flextable (Space Blue & Neon Green)"
    ),
    title = "Fun Flextable Themes"
  ))
})

test_that("theme_brand_gt", {
  skip_if_not_installed("gt")
  skip_if_not_installed("palmerpenguins")
  skip_if_not_installed("dplyr")
  skip_if_not_installed("tidyr")
  skip_if_not_installed("htmltools")

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

  # Create a GT table for visual testing
  library(gt)
  library(dplyr)
  library(tidyr)

  # Get penguin data and prepare it for the table
  penguins <- palmerpenguins::penguins |>
    filter(!is.na(sex)) |>
    mutate(year = as.character(year))

  # Create a summary of penguin counts by species, island, sex, and year
  penguin_counts <- penguins |>
    group_by(species, island, sex, year) |>
    summarise(n = n(), .groups = 'drop')

  # Reshape data to wide format
  penguin_counts_wider <- penguin_counts |>
    pivot_wider(
      names_from = c(species, sex),
      values_from = n
    ) |>
    # Make missing numbers (NAs) into zero
    mutate(across(.cols = -(1:2), .fns = ~tidyr::replace_na(., replace = 0))) |>
    arrange(island, year)

  # Prepare column names for display
  actual_colnames <- colnames(penguin_counts_wider)
  desired_colnames <- actual_colnames |>
    stringr::str_remove('(Adelie|Gentoo|Chinstrap)_') |>
    stringr::str_to_title()
  names(desired_colnames) <- actual_colnames

  # Create the GT table
  penguins_table <- penguin_counts_wider |>
    mutate(across(.cols = -(1:2), ~if_else(. == 0, NA_integer_, .))) |>
    mutate(
      island = as.character(island),
      year = as.numeric(year),
      island = paste0('Island: ', island)
    ) |>
    gt(groupname_col = 'island', rowname_col = 'year') |>
    cols_label(.list = desired_colnames) |>
    tab_spanner(
      label = md('**Adelie**'),
      columns = contains('Adelie')
    ) |>
    tab_spanner(
      label = md('**Chinstrap**'),
      columns = contains('Chinstrap')
    ) |>
    tab_spanner(
      label = md('**Gentoo**'),
      columns = contains('Gentoo')
    ) |>
    tab_header(
      title = 'Penguins in the Palmer Archipelago',
      subtitle = 'Data from the {palmerpenguins} R package'
    ) |>
    sub_missing(missing_text = '-') |>
    summary_rows(
      groups = TRUE,
      fns = list(
        'Maximum' = ~max(., na.rm = TRUE),
        'Total' = ~sum(., na.rm = TRUE)
      ),
      formatter = fmt_number,
      decimals = 0,
      missing_text = '-'
    ) |>
    tab_options(
      data_row.padding = px(2),
      summary_row.padding = px(3),
      row_group.padding = px(4)
    ) |>
    opt_stylize(style = 6, color = 'gray')

  # Apply themes
  light_table <- penguins_table |> light_theme()
  dark_table <- penguins_table |> dark_theme()

  # Create and preview a combined HTML display of the tables
  invisible(combine_html_widgets(
    light_table, dark_table,
    titles = c(
      "Light theme using theme_brand_gt with brand-posit.yml",
      "Dark theme using theme_brand_gt with brand-posit-dark.yml"
    ),
    title = "GT Table Theme Tests"
  ))
})

test_that("theme_colors_gt", {
  skip_if_not_installed("gt")
  skip_if_not_installed("palmerpenguins")
  skip_if_not_installed("dplyr")
  skip_if_not_installed("tidyr")
  skip_if_not_installed("htmltools")

  # Use fun, playful colors for our themes
  sunset_bg <- "#FFF3DE"  # Warm cream
  sunset_fg <- "#FF5722"  # Vibrant orange-red

  ocean_bg <- "#05445E"   # Deep blue
  ocean_fg <- "#D4F1F9"   # Light cyan

  # Create themes with fun colors
  sunset_theme <- theme_colors_gt(bg = sunset_bg, fg = sunset_fg)
  ocean_theme <- theme_colors_gt(bg = ocean_bg, fg = ocean_fg)

  # Verify themes are functions
  expect_type(sunset_theme, "closure")
  expect_type(ocean_theme, "closure")

  # Create a GT table for visual testing
  library(gt)
  library(dplyr)
  library(tidyr)

  # Get penguin data and prepare it for the table
  penguins <- palmerpenguins::penguins |>
    filter(!is.na(sex)) |>
    mutate(year = as.character(year))

  # Create a summary of penguin counts by species, island, sex, and year
  penguin_counts <- penguins |>
    group_by(species, island, sex, year) |>
    summarise(n = n(), .groups = 'drop')

  # Reshape data to wide format
  penguin_counts_wider <- penguin_counts |>
    pivot_wider(
      names_from = c(species, sex),
      values_from = n
    ) |>
    # Make missing numbers (NAs) into zero
    mutate(across(.cols = -(1:2), .fns = ~tidyr::replace_na(., replace = 0))) |>
    arrange(island, year)

  # Prepare column names for display
  actual_colnames <- colnames(penguin_counts_wider)
  desired_colnames <- actual_colnames |>
    stringr::str_remove('(Adelie|Gentoo|Chinstrap)_') |>
    stringr::str_to_title()
  names(desired_colnames) <- actual_colnames

  # Create the GT table
  penguins_table <- penguin_counts_wider |>
    mutate(across(.cols = -(1:2), ~if_else(. == 0, NA_integer_, .))) |>
    mutate(
      island = as.character(island),
      year = as.numeric(year),
      island = paste0('Island: ', island)
    ) |>
    gt(groupname_col = 'island', rowname_col = 'year') |>
    cols_label(.list = desired_colnames) |>
    tab_spanner(
      label = md('**Adelie**'),
      columns = contains('Adelie')
    ) |>
    tab_spanner(
      label = md('**Chinstrap**'),
      columns = contains('Chinstrap')
    ) |>
    tab_spanner(
      label = md('**Gentoo**'),
      columns = contains('Gentoo')
    ) |>
    tab_header(
      title = 'Penguins in the Palmer Archipelago',
      subtitle = 'Data from the {palmerpenguins} R package'
    ) |>
    sub_missing(missing_text = '-') |>
    summary_rows(
      groups = TRUE,
      fns = list(
        'Maximum' = ~max(., na.rm = TRUE),
        'Total' = ~sum(., na.rm = TRUE)
      ),
      formatter = fmt_number,
      decimals = 0,
      missing_text = '-'
    ) |>
    tab_options(
      data_row.padding = px(2),
      summary_row.padding = px(3),
      row_group.padding = px(4)
    ) |>
    opt_stylize(style = 6, color = 'gray')

  # Apply themes
  sunset_table <- penguins_table |> sunset_theme()
  ocean_table <- penguins_table |> ocean_theme()

  # Create and preview a combined HTML display of the tables
  invisible(combine_html_widgets(
    sunset_table, ocean_table,
    titles = c(
      "Sunset theme using theme_colors_gt (Warm Cream & Orange)",
      "Ocean theme using theme_colors_gt (Deep Blue & Cyan)"
    ),
    title = "Fun GT Table Themes"
  ))
})

test_that("theme_brand_plotly light", {
  skip_if_not_installed("plotly")

  # Test with light theme
  posit_light <- test_example("brand-posit.yml")
  light_theme <- theme_brand_plotly(posit_light)

  # Verify light theme is a function
  expect_type(light_theme, "closure")

  # Create a plotly violin plot using iris data
  library(plotly)

  # Create a violin plot with box and meanline visible, showing all points
  fig <- plot_ly(iris, x = ~Species, y = ~Sepal.Width, type = 'violin',
                box = list(visible = TRUE),
                meanline = list(visible = TRUE),
                points = 'all',
                colors = c("#1F77B4", "#FF7F0E", "#2CA02C")) |>
        layout(title = "Iris Sepal Width by Species",
               xaxis = list(title = "Species"),
               yaxis = list(title = "Sepal Width"))

  # Apply the light theme
  light_plot <- fig |> light_theme()

  # Print the light theme plot
  print(light_plot)
  cat("\n\nAbove: Light theme plot using theme_brand_plotly with orange accent from brand-posit.yml\n\n")
})

test_that("theme_brand_plotly dark", {
  skip_if_not_installed("plotly")

  # Test with dark theme
  posit_dark <- test_example("brand-posit-dark.yml")
  dark_theme <- theme_brand_plotly(posit_dark)

  # Verify dark theme is a function
  expect_type(dark_theme, "closure")

  # Create a plotly violin plot using iris data
  library(plotly)

  # Create a violin plot with box and meanline visible, showing all points
  fig <- plot_ly(iris, x = ~Species, y = ~Sepal.Width, type = 'violin',
                box = list(visible = TRUE),
                meanline = list(visible = TRUE),
                points = 'all',
                colors = c("#1F77B4", "#FF7F0E", "#2CA02C")) |>
        layout(title = "Iris Sepal Width by Species",
               xaxis = list(title = "Species"),
               yaxis = list(title = "Sepal Width"))

  # Apply the dark theme
  dark_plot <- fig |> dark_theme()

  # Print the dark theme plot
  print(dark_plot)
  cat("\n\nAbove: Dark theme plot using theme_brand_plotly with burgundy accent from brand-posit-dark.yml\n\n")
})

test_that("theme_colors_plotly light", {
  skip_if_not_installed("plotly")

  # Define colors
  bg <- "#FFFFFF"
  fg <- "#151515"
  light_orange_accent <- "#EE6331"  # Orange from brand-posit.yml

  # Create theme with direct colors and specific accent
  light_colors_theme <- theme_colors_plotly(bg = bg, fg = fg, accent = light_orange_accent)

  # Verify theme is a function
  expect_type(light_colors_theme, "closure")

  # Create a plotly scatter plot with trendline
  library(plotly)

  # Create a linear model for trendline
  model <- lm(mpg ~ wt, data = mtcars)
  x_range <- seq(min(mtcars$wt), max(mtcars$wt), length.out = 50)
  predicted <- predict(model, newdata = data.frame(wt = x_range))

  # Create a scatter plot with trendline overlay
  fig <- plot_ly() |>
    # Add data points
    add_trace(
      data = mtcars,
      x = ~wt,
      y = ~mpg,
      type = 'scatter',
      mode = 'markers',
      marker = list(size = 10),
      text = ~paste("Car:", rownames(mtcars),
                  "<br>Weight:", wt,
                  "<br>MPG:", mpg),
      name = "Data points"
    ) |>
    # Add trendline on the same plot using foreground color with alpha
    add_trace(
      x = x_range,
      y = predicted,
      type = 'scatter',
      mode = 'lines',
      line = list(color = paste0(fg, "66"), width = 2), # fg with 40% alpha
      name = "Trendline"
    ) |>
    # Set layout
    layout(
      title = "Car Weight vs. Fuel Efficiency",
      xaxis = list(title = "Weight (1000 lbs)"),
      yaxis = list(title = "Miles Per Gallon"),
      showlegend = TRUE
    )

  # Apply the light theme with orange accent
  light_plot <- fig |> light_colors_theme()

  # Print the light theme plot
  print(light_plot)
  cat("\n\nAbove: Light theme using theme_colors_plotly with orange accent (#EE6331)\n\n")
})

test_that("theme_colors_plotly dark", {
  skip_if_not_installed("plotly")

  # Define colors
  bg <- "#1A1A1A"
  fg <- "#F1F1F2"
  dark_burgundy_accent <- "#C96B8C" # Burgundy from brand-posit-dark.yml

  # Create theme with direct colors and specific accent
  dark_colors_theme <- theme_colors_plotly(bg = bg, fg = fg, accent = dark_burgundy_accent)

  # Verify theme is a function
  expect_type(dark_colors_theme, "closure")

  # Create a plotly scatter plot with trendline
  library(plotly)

  # Create a linear model for trendline
  model <- lm(mpg ~ wt, data = mtcars)
  x_range <- seq(min(mtcars$wt), max(mtcars$wt), length.out = 50)
  predicted <- predict(model, newdata = data.frame(wt = x_range))

  # Create a scatter plot with trendline overlay
  fig <- plot_ly() |>
    # Add data points
    add_trace(
      data = mtcars,
      x = ~wt,
      y = ~mpg,
      type = 'scatter',
      mode = 'markers',
      marker = list(size = 10),
      text = ~paste("Car:", rownames(mtcars),
                  "<br>Weight:", wt,
                  "<br>MPG:", mpg),
      name = "Data points"
    ) |>
    # Add trendline on the same plot using foreground color with alpha
    add_trace(
      x = x_range,
      y = predicted,
      type = 'scatter',
      mode = 'lines',
      line = list(color = paste0(fg, "66"), width = 2), # fg with 40% alpha
      name = "Trendline"
    ) |>
    # Set layout
    layout(
      title = "Car Weight vs. Fuel Efficiency",
      xaxis = list(title = "Weight (1000 lbs)"),
      yaxis = list(title = "Miles Per Gallon"),
      showlegend = TRUE
    )

  # Apply the dark theme with burgundy accent
  dark_plot <- fig |> dark_colors_theme()

  # Print the dark theme plot
  print(dark_plot)
  cat("\n\nAbove: Dark theme using theme_colors_plotly with burgundy accent (#C96B8C)\n\n")
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