![https://github.com/sebkraemer/FinTsUml/actions/workflows/fints_uml.yml](https://github.com/sebkraemer/FinTsUml/actions/workflows/fints_uml.yml/badge.svg)

# About

This program supports conversion from [Star Money](https://starmoney.de/) transaction protocols
to [UML sequence diagrams](https://plantuml.com/en/sequence-diagram). It was
developed to support my debugging efforts by making a better overview.

It works by going through the file, grepping for FinTS message parts,
filter invalid or unprintable characters, add line breaks and send the
preprocessed data to a [plantuml server](http://plantuml.com/plantuml)
which will return a SVG file which is saved to disc.

Just call the script with the log file as parameter: `python fints_uml.py <smpc.pro>`

Currently, a local instance of a plantuml server is necessary. This avoids
sending your data over the net but of course you can easily change the target
URL if you don't mind and don't want to setup plantuml yourself. (I plan to
make the program more flexible in this regard.)

There are plans to extend the functionality to make it even more useful:
- support for the banking kernel's trace files, not only SMPC logs
- watch file(s) or folders for automatic updates
- improved deployment, several ideas come to mind

# Development

Developed in MacOS with python 3.8.
For dependencies, see `requirements.txt`.

## Ideas and TODOs

The following is a loose list of ideas with no guarantee anywith will ever
be actually implemented:

- improve error handling
- add unit tests
- support kernel logs
- support EBICS xml
- file/directory watcher
- add more options regarding plantuml service
  - start own service automatically?
  - make target server configurable
- add HTTP POST support to avoid possible data limitations
- deployment improvements
  - packaging (pypi, native installers or binaries that avoid the need for python installation)
  - dockerization