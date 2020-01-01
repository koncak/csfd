from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from tqdm.notebook import tqdm

from selenium.common.exceptions import NoSuchElementException


class leaderboard_item:

    def __init__(self, order, name, link, rating, number_of_ratings):
        self.order = order
        self.name = name
        self.link = link
        self.rating = rating
        self.number_of_ratings = number_of_ratings

    def __repr__(self):
        return '{} {}, {}, {}'.format(self.order, self.name, self.rating, self.number_of_ratings)


def csfd_leaderboards(driver, type_of_board):
    url = ('https://www.csfd.cz/zebricky/' + type_of_board + '?show=complete')
    driver.get(url)
    items = driver.find_elements_by_xpath('/html/body/div[2]/div[3]/div[2]/table/tbody/tr')

    leaderboard_items = []
    for item in tqdm(items):

        try:
            order = item.find_element_by_class_name('order').text
            name = item.find_element_by_class_name('film').text
            link = item.find_element_by_css_selector(".film [href]").get_attribute('href')
            rating = item.find_element_by_class_name('average').text
            number_of_ratings = item.find_element_by_class_name('count').text

            board_item = leaderboard_item(order, name, link, rating, number_of_ratings)
            leaderboard_items.append(board_item)

        except NoSuchElementException:  # pravdepodobne prazdny <tr> element
            continue

    return leaderboard_items


# leaders = csfd_leaderboards('nejlepsi-filmy/')

def main():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    # driver = webdriver.Firefox() # GUI verze

    boards = csfd_leaderboards(driver, 'nejlepsi-filmy/')
    for b in boards:
        print(b)

if __name__ == "__main__":
    main()