from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import numpy as np
from collections import Counter
from tqdm.notebook import tqdm
import util_methods as util


class Movie:

    def __init__(self, czech_name, rating, comments, best_movie=None, fav_movie=None):
        self.czech_name = czech_name
        self.rating = rating
        self.comments = comments
        self.best_movie = best_movie
        self.fav_movie = fav_movie
        self.hate_score = self.hate()

    def hate(self):
        if len(self.comments) == 0:
            return 0
        else:
            total = 0
            for comment in self.comments:
                total += comment.score

            return total / len(self.comments)

    def __repr__(self):
        return '{} Hodnoceni: {} Pocet nenavistnych komentaru: {}, Nenavist skore: {}'.format(self.czech_name,
                                                                                              self.rating,
                                                                                              len(self.comments),
                                                                                              round(self.hate_score, 2))


# @timing
def movie_summary(driver, url, print_command=False):
    # pridat nenavistnost spatnych komentaru
    """
    finds
    """

    if '/prehled/' in url:
        url = url.replace('/prehled/', '/')

    driver.get(url + '/komentare/?all=1')

    full_czech_name = util.get_full_czech_name(driver).text
    movie_rating = driver.find_element_by_class_name('average')
    best_movies = util.get_best_movie_score(driver)
    favourite_movies = util.get_favourite_movie_score(driver)

    if favourite_movies:
        favourite_movies = favourite_movies.text
    if best_movies:
        best_movies = best_movies.text

    comments = driver.find_elements_by_xpath('//*[starts-with(@id, "comment")]')  # jde vylepsit: seradit podle ...

    avg = []
    comment_objects = []
    for comment in tqdm(comments):
        rating = util.get_comment_rating(comment)

        if rating is not None:
            avg.append(rating)
            if rating == 0 or rating == 1:
                trash_comment = util.get_comment_text(comment)
                trash_comment = util.remove_last_line_from_string(trash_comment)  # posledni radek je datum komentare
                trash_comment = trash_comment.replace("*", "#")
                trash_comment = util.replace_in_comment(trash_comment, '**')

                author = util.get_comment_author(comment)  # author se bude nacitat jinde
                profile_link = comment.find_element_by_css_selector(".author [href]").get_attribute('href')

                comment_object = util.Comment(rating, trash_comment, 'red', full_czech_name, author=profile_link)  # FIX
                comment_objects.append(comment_object)

    comment_objects.sort(key=lambda x: x.score, reverse=True)

    movie_object = Movie(full_czech_name, movie_rating.text, comment_objects, best_movies, favourite_movies)

    #     for c in comment_objects:
    #         if c.score != 0:
    #             print(c.author, movie_rating_to_stars(c.rating), c.score)
    #             printmd(c.text)

    if print_command:
        print(full_czech_name)
        print("Hodnoceni filmu: {}".format(movie_rating.text))  # co kdyz zatim nema rating
        print("Hodnoceni pouze z komentaru: {}".format(
            int(round(np.mean(avg) * 20, 0))))  # hodnoceni lidi s komentari muze byt rozdilne od vsech hodnoceni
        print()
        if favourite_movies:
            print(favourite_movies)
        if best_movies:
            print(best_movies)

        print('Pocet komentaru: {}'.format(len(comments)))
        print('Pocet komentaru odpad nebo jedna *: {}'.format(len(comment_objects)))
        print()
        print("Vycet hodnoceni:")  # WHET
        counter = Counter(avg)
        for i in range(5, -1, -1):
            if i != 0:
                print('{:>6} {:>5}'.format(i * '*', counter[i]))
            else:
                print('{:>6} {:>5}'.format('odpad!', counter[i]))

    return movie_object


# movie_summary('https://www.csfd.cz/film/2982-prelet-nad-kukaccim-hnizdem', print_command=True)

def main():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    # driver = webdriver.Firefox() # GUI verze

    url = 'https://www.csfd.cz/film/2982-prelet-nad-kukaccim-hnizdem'
    movie_summary(driver, url, print_command=True)


if __name__ == "__main__":
    main()