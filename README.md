![https://github.com/sebkraemer/FinTsUml/actions/workflows/fints_uml.yml](https://github.com/sebkraemer/FinTsUml/actions/workflows/fints_uml.yml/badge.svg)

# About

This program supports conversion from [Star Money](https://starmoney.de/) transaction protocols
to [UML sequence diagrams](https://plantuml.com/en/sequence-diagram) as well as its
internal kernel log format. It was developed to support my debugging efforts
by getting a better overview.

It works by going through the file, grepping for FinTS message parts,
filter invalid or unprintable characters, add line breaks and send the
preprocessed data to a [plantuml server](http://plantuml.com/plantuml)
which will return a SVG file which is saved to disc.

# Run it

There are two options to run it:

- Just call the script with the log file as parameter: `python fints_uml.py <files>`
- If installed as a package, call it as module: `python -m fints_uml <files>`

Before you do that, note that currently, local instance of a plantuml server is
necessary. This might appear cumbersome but avoids sending your data over the net
in unencrypted form. This is not configurable yet. Adapt the target URL in the source
if you need to, sorry.

# Development

Developed in MacOS with python 3.8.

You need `requests` for running and `pytest` for testing 😀

More references info can be gathered from `setup.cfg` and the [Github actions files](https://github.com/sebkraemer/FinTsUml/tree/main/.github/workflows)

Feel free to send an email or open issues or even PRs, I'll be happy to talk about your feedback and ideas.
