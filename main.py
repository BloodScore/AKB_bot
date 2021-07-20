import requests
from bs4 import BeautifulSoup


RANDOM_URL = 'https://baneks.site/random'
LIKES_SORTING = '?s=likes'
SELECTOR = 'block-content mdl-card__supporting-text mdl-color--grey-300 mdl-color-text--grey-900'


def short_url(url):
    url = requests.post('https://clck.ru/--', params={'url': url}).text
    return url


def format_text(text):
    text = text.replace(
        '<p>', ''
    ).replace(
        '</p>', ''
    ).replace(
        '<br>', '\n'
    ).replace(
        '</br>', '\n'
    ).replace(
        '<br/>', '\n'
    )
    return text


def get_random_anek_page(url=None):
    if not url:
        anek = requests.get(RANDOM_URL)
        url = anek.url + LIKES_SORTING
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    return soup, url


def get_single_anek(soup):
    div = soup.find('div', {'class': SELECTOR})
    text = str(div.find('p'))

    return format_text(text)


def get_comments(soup):
    aneks = []

    for div in soup.find_all('div', {'class': SELECTOR}, limit=4):
        aneks.append(div.find('p'))

    i = 1

    while i < len(aneks):
        aneks[i] = format_text(str(aneks[i]))
        i += 1

    return aneks[1:]


def main():
    soup, url = get_random_anek_page()

    print(f'\n{url}\n')

    print(f'Анекдот:\n\n{get_single_anek(soup)}')

    comments = input('\nВы хотели бы увидеть топ-3 комментария (да/нет)? ')
    print()

    if comments == 'да':
        for comment in get_comments(soup):
            print(f'{comment}\n')


if __name__ == '__main__':
    main()
