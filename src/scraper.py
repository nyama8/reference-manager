from urllib.request import urlopen
from urllib.request import Request
import re
import html

'''
UPDATED: 2 August 2020, Nick Yama

DESCRIPTION:
    This module contains several functions to open and parse html source files for
    article metadata. Primary interfacing with the module is through the
    metadata_dict_from_src() and metadata_dict_from_url() functions. Other functions
    are for internal usage such as the highwire_press_tag_parser().

TESTED PUBLISHER COMPATIBILITY:
    Parsing via URL and HTML source files:
        - Nature Publishing Group
        - Optical Society of America (OSA) Publishing
        - American Physical Society (APS)
        - De Gruyter (Nanophotonics)
        - ArXiv
        - PNAS
        - American Association for the Advancement of Science (Science magazine)
        - Springer Publishing

    Parsing via HTML source files ONLY:
        - American Institute of Physics: Blocks Python parsing from urllib, readable by parser
        - Wiley Online Library: Blocks Python parsing from urllib, readable by parser

    Incompatible:
        - American Chemical Society (uses Dublin Core tagging)
        - IEEE Xplore (Metadata accessible via API or manual gathering)


FUTURE WORK:
    - Parsing function for Dublin Core metadata tagging system
'''



def highwire_press_tag_parser(web_html):
    '''
    Given a website html source file as a string, uses regular expressions (Regex)
    to parse the string for Highwire Press metadata tags of the form:

    <meta name="citation_[TYPE]" content="[VALUE]">

    Then returns a dictionary of type-value pairs.

    Known issues:
        - May not convert all special characters well for certain encodings
    '''

    # Generate metadata type list from available content
    metadata_types = re.findall(r'<meta name="citation_([A-Za-z_]*)"', web_html)

    if len(metadata_types) == 0:
        raise ValueError('No Highwire Press metadata found')


    # Clean up list of metadata types
    metadata_types = list(set(metadata_types))
    try:
        metadata_types.remove('reference')
    except:
        pass

    try:
        metadata_types.remove('abstract')
    except:
        pass

    try:
        metadata_types.remove('author_institution')
    except:
        pass

    try:
        # Get the authors if available
        author_type = metadata_types.pop(metadata_types.index('author'))
        pattern = r'<meta name="citation_author" content="(.*?)"'
        author_names = re.findall(pattern, web_html)

        # Fix names into UTF-8 encoding
        for index, author in enumerate(author_names):
            author_names[index] = html.unescape(author)
    except:
        #print('Authors could not be found.\n')
        pass

    # Generate metadata values for each type found
    metadata_values = []
    for metadata_type in metadata_types:
        #print(metadata_type)
        pattern = r'<meta name="citation_' + metadata_type + '" content="(.*?|$)"'
        try:
            metadata_value = re.findall(pattern, web_html)[0]
        except Exception as e:
            metadata_value = ''
        metadata_values.append(html.unescape(metadata_value))

    # add authors back
    metadata_types.append(author_type)
    metadata_values.append(author_names)

    metadata_dict = dict(zip(metadata_types, metadata_values))

    return metadata_dict





def metadata_dict_from_url(url):
    '''
    Gets journal article metadata from url source html and returns dictionary
    of metadata type-value pairs. Most metadata is saved as a string. Author(s)
    are saved as list of strings when available.

    Known issues:
        - Different metadata tagging systems (dc.Type) are not handled
    '''

    # Get website HTML
    try:
        print('Accessing URL...')
        web_src = urlopen(str(url))
        web_html = str(web_src.read())
        print('Page accessed.\n')
    except Exception as e:
        print('Could not access page (' + str(e) + '), trying alternative...')

        try:
            header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
            req = Request(url, headers=header)
            web_src = urlopen(req)
            web_html = str(web_src.read())
            print('Page accessed.\n')
        except Exception as e:
            print('Error occurred: ' + str(e) + '\nReturning empty dictionary.')
            return {}

    # Parse data
    metadata_dict = {}
    try:
        metadata_dict = highwire_press_tag_parser(web_html)
    except Exception as e:
        print('Parser failed: ' + str(e) + '.')


    return metadata_dict




def metadata_dict_from_src(filename, path=''):
    '''
    Given name of html source file for journal article webpage as a string (and optional path
    to source file directory), reads he source file and parses it for article metadata

    Known issues:
        - Different metadata tagging systems (dc.Type) are not handled
    '''

    # Read file from manually downloaded html source file
    with open(path+filename, 'r') as f:
        html_src = str(f.read())

    # Parse the source file
    metadata_dict = {}
    try:
        metadata_dict = highwire_press_tag_parser(html_src)
    except Exception as e:
        print('Parser failed: ' + str(e) + '.')

    return metadata_dict
