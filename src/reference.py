from scraper import metadata_dict_from_url
from scraper import metadata_dict_from_src
import re

'''
UPDATED: 6 August 2020, Nick Yama

DESCRIPTION:
    This module contains the Reference class, which is the basic object of the
    Reference Manager, as well as several general and helper methods for creating
    Reference classes.

FUTURE WORK:
    - Complete Bibtex citation
    - Functions to open references
    - Function to create general citations in .rtf format
'''


class Reference:
    '''
    The Reference class represents a single article.
    '''
    def __init__(self, name):
        self.name = str(name)
        self.title = ''
        self.authors = [('','','')]
        self.type = ''

        self.publisher = ''
        self.pub_date = ('','','')
        self.doi = ''

        # Journal metadata
        self.journal = ''
        self.journal_abbrv = ''
        self.volume = ''
        self.issue = ''
        self.firstpage = ''
        self.lastpage = ''

        # Conference metadata
        self.conference = ''
        self.conference_abbrv = ''
        self.conference_location = ''
        self.proceedings = ''
        self.paper_number = ''

        # ArXiv metadata
        self.arxiv_id = ''
        self.arxiv_url = ''

        self.pdf_name = ''
        self.lib_path = ''
        self.tags = set()

        # Holds the dictionary used to build Reference
        self.dict = {}



    def add_tags(self, new_tags):
        '''
        Add tags to a Reference object.

        Args:
            - new_tags: list of strings or string of tags to add
        '''
        if isinstance(new_tags, list):
            self.tags.update(new_tags)
        elif isinstance(new_tags, str):
            self.tags.add(new_tags)
        else:
            raise TypeError('Tags must be passed as a list or string')


    def remove_tags(self, rem_tags):
        '''
        Removes tags from a Reference object.

        Args:
            - rem_tags: list of strings or string of tags to remove
        '''
        if isinstance(rem_tags, list):
            for tag in rem_tags:
                try:
                    self.tags.remove(tag)
                except:
                    raise ValueError('Unable to remove tag: \'' + str(tag) + '\' ')
        elif isinstance(rem_tags, str):
            try:
                self.tags.remove(rem_tags)
            except:
                raise ValueError('Unable to remove \'' + str(rem_tags) + '\'')
        else:
            raise TypeError('Tags must be passed as a list or string')



    def bibtex_author_list(self):
        '''
        Returns the author list as a string in the Bibtex format
            'first_1 middle_1 last_1 and first_2 middle_2 last_2 ...'
        '''
        authors = []
        for author in self.authors:
            name = ''
            name = name + author[0] + ' '
            if len(author[1]) != 0:
                name = name + author[1] + ' '
            name = name + author[2]
            authors.append(name)
        return ' and '.join(authors)



    def generate_bibtex(self):
        '''
        Returns a string of the Bibtex entry for the Reference
        '''
        bib_items = []
        if self.type == 'journal':
            bib_items.append('@article{' + self.name)
            bib_items.append('\tauthor  = \"' + self.bibtex_author_list() + '\"')
            bib_items.append('\ttitle   = \"' + self.title + '\"')
            bib_items.append('\tyear    = \"' + self.pub_date[0] + '\"')
            bib_items.append('\tmonth   = \"' + self.pub_date[1] + '\"')
            bib_items.append('\tjounral = \"' + self.journal + '\"')
            bib_items.append('\tvolume  = \"' + self.volume + '\"')
            bib_items.append('\tnumber  = \"' + self.issue + '\"')

            if self.lastpage == '':
                pages_str = '\tpages   = \"' + self.firstpage + '\"'
            else:
                pages_str = '\tpages   = \"' + self.firstpage + '--' + self.lastpage + '\"'


            bib_items.append(pages_str)

        elif self.type == 'conference':
            pass

        else:
            pass

        return ',\n'.join(bib_items) + '\n}'


    def set_pdf_name(self, name):
        '''
        Sets the pdf name for the Reference pdf on a local hard drive.
        '''
        self.pdf_name = str(name)




'''
General and helper methods for working with References
'''

def make_author_list(author_list):
    '''
    Given a list of author names as strings ['first middle last', '...'],
    returns a list of author names as tuples [('first', 'middle', 'last'), (...)]

    Args:
        - author_list: List of author names as single string
    '''
    authors = []
    for author in author_list:
        first = re.findall(r'^(\S+?) ', author)[0]
        try:
            middle = re.findall(r'^\S+?\s+(\S+?)\s+\S+?$', author)[0]
        except:
            middle = ''
        last = re.findall(r' (\S+?)$', author)[0]
        authors.append((first, middle, last))

    return authors


def get_fancy_date(date_str):
    '''
    Given a date as a string 'YYYY/MM/DD', returns the corresponding date as
    a tuple ('year', 'month', 'day').
    '''
    months = {'01': 'Jan.', '02': 'Feb.', '03': 'Mar.', '04': 'Apr.', '05': 'May', '06': 'Jun.',
            '07': 'Jul.', '08': 'Aug.', '09': 'Sep.', '10': 'Oct.', '11': 'Nov.', '12': 'Dec.'}

    try:
        year = re.findall(r'(\d{2,4})/', date_str)[0]

        try:
            month = months[re.findall(r'/(\d{2})', date_str)[0]]
        except:
            month = ''

        try:
            day = re.findall(r'/\d{2}/(\d{2})', date_str)[-1]
        except:
            day = ''

        return (year, month, day)
    except:
        year = re.findall(r'(\d{2,4})-', date_str)[0]

        try:
            month = months[re.findall(r'-(\d{2})', date_str)[0]]
        except:
            month = ''

        try:
            day = re.findall(r'-\d{2}-(\d{2})', date_str)[-1]
        except:
            day = ''

        return (year, month, day)


def remove_duplicates(seq):
    '''
    Given an ordered list with duplicates, returns the ordered list without duplicates

    Fast method via Stack Overflow:
    https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
    '''
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]



def reference_from_dict(ref_dict, name, tags=set()):
    '''
    Given a dictionary of metadata name:value pairs, returns a Reference object
    corresponding to the dictionary. The ref_dict dictionary must have keys
    in the form of Highwire Press metadata tags.
    '''
    ref = Reference(name)

    if ref_dict == {}:
        raise ValueError('Provided dictionary is empty')

    try:
        ref.title = ref_dict['title']
        #ref.authors = make_author_list(ref_dict['author'])
        ref.authors = remove_duplicates(make_author_list(ref_dict['author']))
    except:
        raise ValueError('Sufficient data not found')

    try:
        # Journal metadata
        ref.journal = ref_dict['journal_title']
        ref.journal_abbrv = ref_dict['journal_title']
        ref.volume = ref_dict['volume']
        ref.issue = ref_dict['issue']
        ref.publisher = ref_dict['publisher']
        ref.doi = ref_dict['doi']
        ref.firstpage = ref_dict['firstpage']
        ref.pub_date = get_fancy_date(ref_dict['publication_date'])
        try:
            ref.lastpage = ref_dict['lastpage']
        except:
            pass


        ref.type = 'journal'
        print('Journal reference found.')
    except:
        try:
            # Conference metadata
            ref.conference = ref_dict['conference_title']
            try:
                ref.conference_abbrv = ref_dict['conference_abbreviation']
            except:
                pass
            ref.conference_location = ref_dict['location']
            ref.proceedings = ref_dict['proceedings']
            ref.publisher = ref_dict['publisher']
            ref.doi = ref_dict['doi']
            ref.pub_date = ref_dict['publication_date']
            try:
                ref.paper_number = ref_dict['firstpage']
            except:
                pass

            ref.type = 'conference'
            print('Conference reference found.')
        except:
            try:
                # ArXiv metadata
                ref.arxiv_id = ref_dict['arxiv_id']
                ref.arxiv_url = ref_dict['pdf_url']

                ref.type = 'arxiv'
                print('ArXiv reference found.')
            except:
                raise ValueError('Sufficient data not found')


    ref.pdf_name = ''
    ref.tags = tags

    ref.dict = ref_dict

    return ref



def reference_from_url(name, url, tags=set()):
    '''
    Given URL for online article and an optional set of tags, returns Reference
    object corresponding to the article.
    '''
    ref_dict = metadata_dict_from_url(url)
    ref = reference_from_dict(ref_dict, name, tags)
    return ref

def reference_from_src(name, filename, path='', tags=set()):
    '''
    Given filename, path to library, and an optional set of tags, returns Reference
    object corresponding to the article.
    '''
    if path == '':
        ref_dict = metadata_dict_from_src(filename)
    else:
        ref_dict = metadata_dict_from_src(filename, path)

    ref = reference_from_dict(ref_dict, name, tags)
    return ref