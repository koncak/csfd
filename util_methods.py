from time import time
from functools import wraps
import re

from selenium.common.exceptions import NoSuchElementException

from IPython.display import Markdown, display


RATING_SYSTEM = {"film c0": "white",
                 "film c1": "red",
                 "film c2": "blue",
                 "film c3": "black"}

EVIL_WORDS = {"sračk", 'stupidní', 'kretén', "kokot", "zkurvenec", 'hovno', 'hovna', 'čurák', 'hajzl', 'kurv', 'po*rať',
              'prdel', 'propaganda', 'idiot', 'buzny', 'buzna', 'hnus', 'ho*no', 'hnus', 'mrtka',
              'blití', 'fuj', 'sra*ka', 'posrat', 'demenci', 'pí*ovina', 'píčovina', 'kravin',
              'vymrdaných', 'shit', 'stád', 'pí..vina', 'dement', 'zasvin', 'prase', 'úch*l', 'poser',
              'blb', 'magor', 'sračku', 'mrd*ka', 'držka', 'debil', 'retard', 'neger', "hovnům",
              'pi*ovina', 'kund', 'piče', 'piči', 'mrd', 'pičo', 'píče', 'negr', 'pičus', 'sran', 'buzerant'}


class Comment:
    def __init__(self, rating, text, approximate_movie_rating, movie_name, author=None, movie_rating=None):
        self.rating = rating
        self.text = text
        self.approximate_movie_rating = approximate_movie_rating
        self.movie_rating = movie_rating
        self.movie_name = movie_name
        self.author = author
        self.score = self.evil_score()

    def add_author(self, author):
        self.author = author

    def evil_score(self):
        score = 0
        for word in self.text.split():
            for EVIL in EVIL_WORDS:
                if EVIL in word.lower():
                    score += 2

            repeated_char, number_of_repeats = maxRepeating(word)
            if number_of_repeats > 2:  # 0,33 zvoleno jen tak for fun
                number_of_repeats = 5 if number_of_repeats > 5 else number_of_repeats
                score += 0.33 * number_of_repeats
                if repeated_char == "!":
                    score += 0.33 * number_of_repeats

            if caps_lock(word):
                score += 0.5

        return score

    def to_dict(self):
        return {
            'author': self.author,
            'rating': self.rating,
            'text': self.text,
            'hate_score': self.score,
            'movie_name': self.movie_name,
            'movie_rating_apr': self.approximate_movie_rating,
            'movie_rating': self.movie_rating
        }


class User: # zatim nic
    def __init__(self, link):
        self.link = link


def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print('Elapsed time: {}'.format(end - start))
        return result

    return wrapper


def printmd(string):
    display(Markdown(string))


def get_best_movie_score(driver):
    """
    Vetsina filmu nema skore nejlepsich filmu
    """
    try:
        return driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[2]/div[1]/p/a[1]')
    except:
        return None


def get_favourite_movie_score(driver):
    """
    Vetsina filmu nema skore oblibenosti
    """
    try:
        return driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[2]/div[1]/p/a[2]')
    except:
        return None


def get_full_czech_name(driver):
    return driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/h1')


def get_comment_text(comment):
    return comment.find_element_by_class_name('post').text


def get_comment_author(comment):
    return comment.find_element_by_class_name('author')


def get_czech_name_in_comment(comment):
    return comment.find_element_by_class_name('author').text


def get_comment_rating(comment):
    """
    return None pro komentar bez hodnoceni
           0 pro komentar typu odpad!
           pocet hvezdicek jinak
    """
    try:
        author_rating = comment.find_element_by_class_name('rating').get_attribute('alt')
    except:
        return None

    if not author_rating:
        return 0

    return len(author_rating)


def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]


def count_in_string(string, char):
    return string.count(char)


def movie_rating_to_stars(rating):
    if rating == 0:
        return "odpad!"
    else:
        return rating * "*"


def get_approx_movie_rating_from_comment(comment):
    """ Z komentare v profilu nalezne priblizne hodnoceni filmu podle barvy ikony

    Parameters:
        comment(webdriver.element?): comment inside users profile

    Returns:
        string:color of movie icon

    """
    movie_rating = comment.find_element_by_class_name("film")
    return RATING_SYSTEM[movie_rating.get_attribute("class")]


def profile_comments(driver):
    current = driver.current_url
    driver.get(current + 'komentare/podle-rating/')

    try:
        pages = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[2]/div[1]/div[3]/div[3]').text

    except NoSuchElementException:  # pokud ma pouze jednu stranku komentaru
        comment_objects = profile_comments_on_page(driver, current + 'komentare/podle-rating/')
        list(map(lambda c: c.add_author(current), comment_objects))
        return comment_objects

    pages = re.findall(r'\d+', pages)[-1]  # hack, posledni cislo v seznamu, potrebuje poradne otestovat(vypada OK)
    try:
        pages = int(pages)
    except:
        raise ValueError("Neco divneho s typem")

    next_run = True
    comment_objects = []
    while next_run:
        local_comments = profile_comments_on_page(driver, current + 'komentare/podle-rating/strana-' + str(pages))
        if len(local_comments) == 0:  # pokud nejsou zadne komentare s 0 nebo 1 hvezdou
            next_run = False
            break

        local_comments = [c for c in local_comments if c is not None]
        list(map(lambda c: c.add_author(current), local_comments))

        comment_objects = comment_objects + local_comments
        pages -= 1

    return [c for c in comment_objects if c is not None]  # nevim proc


def profile_comments_on_page(driver, url):
    driver.get(url)
    comments = driver.find_elements_by_class_name("post")

    out = []
    for comment in comments:
        comment_rating = get_comment_rating(comment)
        if comment_rating is None:
            out.append(None)  # HACK
            continue
        if comment_rating > 1:
            continue

        comment_text = comment.text.split('\n')[1:][0]  # hack, prvni radek neni text komentare
        comment_text = comment_text.replace("*", "#")  # nahrazeni hvezdicek, ktere se v komentari vyskytuji

        movie_approx = get_approx_movie_rating_from_comment(comment)
        movie_name = get_czech_name_in_comment(comment)

        comment_object = Comment(comment_rating, comment_text, movie_approx, movie_name)
        out.append(comment_object)

    return out


def maxRepeating(string):
    n = len(string)
    count = 0
    res = string[0]
    cur_count = 1

    for i in range(n):
        if (i < n - 1 and string[i] == string[i + 1]):
            cur_count += 1

        else:
            if cur_count > count and string[i] != ".":
                count = cur_count
                res = string[i]
            cur_count = 1
    return res, count


def caps_lock(string):
    if len(string) > 2 and string.isupper():
        return True


def comment_split(comment_text):  # pouzite jen k vytvoreni counteru slov
    words = []
    for word in comment_text.split():
        if word[-1] == "," or word[-1] == ".":
            word = word[0:-1]

        word = word.lower()
        words.append(word)

    return words


def replace_in_comment(comment_text, replace):
    words = comment_text.split()
    for i, word in enumerate(words):
        for EVIL in EVIL_WORDS:
            if EVIL in word.lower():
                words[i] = replace + word + replace
    return " ".join(words)


# profile_comments('https://www.csfd.cz/uzivatel/363-woody', driver)
def profile_ratings(driver):
    current = driver.current_url
    driver.get(current + '/hodnoceni/')

    ratings = driver.find_elements_by_class_name('rating')

    all_ratings = []
    for rating in ratings:
        rating = rating.get_attribute('alt')
        if not rating:
            all_ratings.append(0)
        else:
            all_ratings.append(len(rating))
    #         print(rating.get_attribute('alt'))

    next_run = True
    i = 2
    print("Prochazim stranky s hodnocenim")
    while next_run:
        driver.get(current + 'hodnoceni/strana-' + str(i) + '/')
        ratings = driver.find_elements_by_class_name('rating')
        i += 1

        if len(ratings) == 0:  # prazdna stranka
            next_run = False
            continue

        for rating in ratings:
            rating = rating.get_attribute('alt')
            if not rating:
                all_ratings.append(0)
            else:
                all_ratings.append(len(rating))

    return all_ratings