# brand_yml read and print methods

    Code
      print(brand)
    Message
      ## '_brand.yml'
      meta:
        name:
          full: Posit Software, PBC
          short: Posit
        link:
          home: https://posit.co/
          guide: https://positpbc.atlassian.net/wiki/x/AQAgBQ/
          mastodon: https://fosstodon.org/@Posit/
          linkedin: https://www.linkedin.com/company/posit-software/
          twitter: https://twitter.com/posit_pbc/
      logo:
        small:
          path: posit-icon.png
          alt: ~
        medium:
          path: posit.png
          alt: ~
        large:
          path: posit.svg
          alt: ~
      color:
        palette:
          blue: '#447099'
          orange: '#EE6331'
          gray: '#404041'
          white: '#FFFFFF'
          teal: '#419599'
          green: '#72994E'
          burgundy: '#9A4665'
        foreground: '#151515'
        background: '#FFFFFF'
        primary: '#447099'
        secondary: '#707073'
        tertiary: '#C2C2C4'
        success: '#72994E'
        info: '#419599'
        warning: '#EE6331'
        danger: '#9A4665'
        light: '#FFFFFF'
        dark: '#404041'
      typography:
        fonts:
          - source: google
            family: Open Sans
          - source: google
            family: Fira Code
          - source: google
            family: Roboto Slab
            weight: 600
            style: normal
            display: block
        base:
          family: Open Sans
          line-height: 1.25
          size: 1rem
        headings:
          family: Roboto Slab
          color: '#447099'
          weight: 600
        monospace:
          family: Fira Code
          size: 0.9em
        monospace-inline:
          family: Fira Code
          size: 0.9em
        monospace-block:
          family: Fira Code
          size: 0.9em
    Output
      

# brand_yml read and print methods with typography and colors

    Code
      print(brand)
    Message
      ## '_brand.yml'
      meta:
        name:
          short: examples/brand-typography-color.yml
          full: examples/brand-typography-color.yml
      color:
        palette:
          red: '#FF6F61'
        primary: '#87CEEB'
        secondary: '#50C878'
        danger: '#FF6F61'
        foreground: '#1b1818'
        background: '#f7f4f4'
      typography:
        headings:
          color: '#87CEEB'
        monospace-inline:
          color: '#f7f4f4'
          background-color: '#FF6F61'
        monospace-block:
          color: '#1b1818'
          background-color: '#f7f4f4'
        link:
          color: '#FF6F61'
    Output
      

