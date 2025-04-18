# brand.logo errors are handled

    Code
      as_brand_yml(list(logo = 1234))
    Condition
      Error:
      ! Could not evaluate cli `{}` expression: `x`.
      Caused by error:
      ! object 'x' not found
    Code
      as_brand_yml(list(logo = list(path = "foo", bad = "foo")))
    Condition
      Error in `brand_logo_normalize()`:
      ! `logo` contains unexpected names: "bad"
      i Allowed names: "path" and "alt"
    Code
      as_brand_yml(list(logo = list(unknown = "foo.png")))
    Condition
      Error in `brand_logo_normalize()`:
      ! `logo` contains unexpected names: "unknown"
      i Allowed names: "images", "small", "medium", and "large"
    Code
      as_brand_yml(list(logo = list(images = "foo.png")))
    Condition
      Error in `brand_logo_normalize_images()`:
      ! `logo.images` must be a list, not a string
    Code
      as_brand_yml(list(logo = list(images = list(light = 1234))))
    Condition
      Error in `brand_logo_normalize_images()`:
      ! `logo.images.light` must be a string or a list, not a number.
    Code
      as_brand_yml(list(logo = list(small = 1234)))
    Condition
      Error in `brand_logo_normalize_sizes()`:
      ! Invalid value for logo.small:
      x 1234
      i Expected a string (path or logo.image name) or a list.

# brand.logo full example works

    Code
      brand$logo
    Output
      $images
      $images$mark
      <brand_logo_resource src="logos/pandas/pandas_mark.svg" alt="">
      $images$mark_white
      <brand_logo_resource src="logos/pandas/pandas_mark_white.svg" alt="">
      $images$secondary
      <brand_logo_resource src="logos/pandas/pandas_secondary.svg" alt="">
      $images$secondary_white
      <brand_logo_resource src="logos/pandas/pandas_secondary_white.svg" alt="">
      $images$pandas
      <brand_logo_resource src="logos/pandas/pandas.svg" alt="">
      $images$pandas_white
      <brand_logo_resource src="logos/pandas/pandas_white.svg" alt="">
      
      $small
      <brand_logo_resource src="logos/pandas/pandas_mark.svg" alt="">
      $medium
      <brand_logo_resource variant="light" src="logos/pandas/pandas_secondary.svg" alt="">
      <brand_logo_resource variant="dark" src="secondary-white" alt="">
      $large
      <brand_logo_resource src="logos/pandas/pandas.svg" alt="">

