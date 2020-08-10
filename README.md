# reference-manager
Python classes and methods for capturing and handling citation metadata

### Description
The contained modules simulate the basic functionality of other reference
management software (such as Zotero or Mendeley) at the programming level.
Citation metadata scraping and reference management can be imported into other
applications.

The citation metadata is found by scraping the html source files for meta tags
used to index the sites by Google Scholar. Most journals use the Highwire
Press metadata tagging system. Another common system, the Dublin Core system,
is not currently supported by this project.

### Dependencies
This project was developed entirely in python3 using standard library modules.