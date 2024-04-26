import requests
from bs4 import BeautifulSoup
#from PyPDF2 import PdfReader, PdfWriter


class Spell:
    def __init__(self, name, source, level, type, description, *,
                 casting_time=None,
                 components=None,
                 duration=None,
                 range=None,
                 **extras
                ):
        self.name = name
        self.source = source
        # spell type
        self.level = level
        self.type = type
        # description
        self.description = description
        # extra
        self.casting_time = casting_time
        self.components = components
        self.duration = duration
        self.range = range
        self.extras = extras

    @classmethod
    def from_link(cls, link):
        response = requests.get(link)
        soup = BeautifulSoup(response.content)
        spell_content = soup.find('div', id='page-content')

        name = soup.title.text.split('-')[0].strip()
        source, spell_type, *further, _ = soup.find_all('p')
        # source
        source = source.text.split(':')[1]
        source = source.strip()

        # type
        spell_type = spell_type.text.strip()
        level, *type = spell_type.split()
        try:
            level = int(level[0])
        except ValueError:
            # cantrip
            level, type = type[0], level
        
        # extra info
        description = []
        spell_info = {}
        for par in further:
            keys = par.find_all('strong')
            for key in keys:
                value = key.nextSibling.text.strip()
                key = ''.join(c for c in key.text.lower().strip() if c.isalpha() or c.isspace())
                key = '_'.join(key.split())
                spell_info[key] = value
            else:
                description.append(par.text)

        # description
        description = ' '.join(description)
        return cls(name, source, level, type, description, **spell_info)

    def to_form(self, form):
        reader = PdfReader(form)
        writer = PdfWriter()
        page = reader.pages[0]
        fields = reader.get_fields()
        
        writer.add_page(page)
        writer.update_page_form_filed_values(
            writer.pages[0],
            self.__dict__
        )
        filename = '_'.join(self.name.lower().split())
        with open(f'{filename}.pdf', 'wb') as output:
            writer.write(output)

    def __repr__(self):
        return f'Spell({self.name}, casting_time={self.casting_time}, range={self.range})'


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    return soup


def iter_spells(soup):
    for table in soup.find_all('table'):
        yield from table.find_all('a')


def main():
    BASE_URL = 'http://dnd5e.wikidot.com'

    soup = get_soup(BASE_URL + '/spells:cleric')
    for link in iter_spells(soup):
        print(Spell.from_link(BASE_URL + link.get('href')))


if __name__ == '__main__':
    main()
