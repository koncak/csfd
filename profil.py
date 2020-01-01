from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import pandas as pd
from collections import Counter
import util_methods as util

from selenium.common.exceptions import NoSuchElementException


# co kdyz csfd odmitne request
# hodnoceni s komentarem je zahrnoto v hodnocenich bez komentaru
# nechapu .. hodnoceni, videli ... stejny film, hvezdicku ... za -- regex

# pocet vykricniku



# @timing
def profile_summary(driver, url):

    driver.get(url)

    try:
        error = driver.find_element_by_id('pg-web-error')  # nejake divne
        if error:
            #             print(error.text)
            raise ValueError("Neplatna url adresa")
    except NoSuchElementException:
        pass

    comments = util.profile_comments(driver)
    print("Profile:", url)
    print("Nenavistne komentare u filmu/serialu s vetsim hodnocenim nez 70%")
    print()

    evil_comments = Counter()
    sum_of_comment_score = 0
    for comment in comments:

        #         sum_of_comment_score += comment.score # bud tady pro vsechny filmy
        if comment.approximate_movie_rating == "red":  # pokud hodnoti cerveny film odpadem nebo 1 hvezdou

            comment_text = comment.text

            printed = False
            comment_text = util.replace_in_comment(comment_text, '**')
            if "**" in comment_text:
                printed = True

            if printed:
                sum_of_comment_score += comment.score  # nebo tady pro spatne hodnocene
                print(comment.movie_name, util.movie_rating_to_stars(comment.rating), comment.score)
                print(comment_text)
                print()

            comment_words = util.comment_split(comment.text)
            for word in comment_words:
                evil_comments[word] += 1

    frame = pd.DataFrame.from_records(
        [comment.to_dict() for comment in comments if comment.rating < 2 and comment.approximate_movie_rating == "red"])
    #     from_frame = [(Comment(row.HourOfDay,row.Percentage)) for index, row in df.iterrows() ]

    print("Skore profilu:", round(sum_of_comment_score, 1))
    print("Pomer unikatnich a vsech slov", len(evil_comments) / sum(evil_comments.values()))


# profile_summary('https://www.csfd.cz/uzivatel/229421-oskiii') # posledni dve stranky komentare bez hodnoceni
# profile_summary('https://www.csfd.cz/uzivatel/1088margh/') # test nefunkcniho odkazu
# profile_summary('https://www.csfd.cz/uzivatel/545723-arsenal83/')

def main():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    # driver = webdriver.Firefox() # GUI verze

    url = 'https://www.csfd.cz/uzivatel/545723-arsenal83/'
    profile_summary(driver, url)


if __name__ == "__main__":
    main()