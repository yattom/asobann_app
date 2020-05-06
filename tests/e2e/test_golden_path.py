import pytest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .helper import compo_pos, Rect, GameHelper, TOP



def test_golden_path(server, browser: webdriver.Firefox, another_browser: webdriver.Firefox):
    host = GameHelper(browser)
    host.go(TOP)
    host.menu.import_jsonfile(str(Path(__file__).parent / "./table_for_e2etests.json"))
    host.should_have_text("you are host")

    # handle cards
    card = host.component(3)
    assert Rect(left=150, top=175) == card.pos()
    host.drag(card, x=300, y=50)
    assert Rect(left=450, top=225) == card.pos()
    assert "voice_back.png" in card.element.find_element_by_tag_name('img').get_attribute('src')
    host.double_click(card)
    assert "v02.jpg" in card.element.find_element_by_tag_name('img').get_attribute('src')

    # open another browser and see the same cards
    another = GameHelper(another_browser)
    another.go(browser.current_url)
    another.menu.join("Player 2")
    card_on_another_browser = another.component(3)
    assert Rect(left=450, top=225) == card_on_another_browser.pos()
    assert "v02.jpg" in card_on_another_browser.element.find_element_by_tag_name('img').get_attribute('src')


def test_table_host_invite_friend(server, browser: webdriver.Firefox, another_browser: webdriver.Firefox):
    host = GameHelper(browser)
    host.go(TOP)
    host.menu.import_jsonfile(str(Path(__file__).parent / "./table_for_e2etests.json"))

    host.should_have_text("you are host")

    # host can move cards
    card = host.component(nth=4)
    card_pos = card.pos()
    host.drag(card, x=200, y=50)
    card_pos_on_host = card.pos()
    assert card_pos.left + 200 == card_pos_on_host.left and  card_pos.top + 50 == card_pos_on_host.top
    face = card.face()
    host.double_click(card)
    assert face != card.face()

    # invite someone
    host.menu.copy_invitation_url.click()
    # in test ignore clipboard as it might get ugly on running environment
    invitation_url = host.menu.invitation_url.value

    # new player is invited
    player = GameHelper(another_browser)
    player.go(invitation_url)
    player.should_have_text("you are observing")

    # new player cannot move cards before joining
    players_card = player.component(nth=4)
    players_card_pos = players_card.pos()
    player.drag(players_card, x=200, y=50)
    assert players_card_pos == players_card.pos(), "not moved"

    # new player name herself and join
    player.menu.join("Player A")
    player.should_have_text("you are Player A")

    # now new player can move cards
    players_card_pos = players_card.pos()
    assert card_pos_on_host == players_card_pos, "seeing same table"
    player.drag(players_card, x=200, y=50)
    assert players_card_pos != players_card.pos(), "moved"


if __name__ == '__main__':
    test_golden_path()
