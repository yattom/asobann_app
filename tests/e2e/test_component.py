import pytest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import NoSuchElementException

from .helper import compo_pos, Rect, GameHelper, TOP


def rect(element):
    return {
        'top': element.location["y"],
        'left': element.location["x"],
        'bottom': element.location["y"] + element.size["height"],
        'right': element.location["x"] + element.size["width"],
        'height': element.size["height"],
        'width': element.size["width"],
    }


def test_add_and_move_hand_area(server, browser: webdriver.Firefox):
    host = GameHelper(browser)
    host.go(TOP)
    host.menu.import_jsonfile(str(Path(__file__).parent / "./table_for_e2etests.json"))

    host.should_have_text("you are host")

    host.menu.add_my_hand_area.click()

    # move and resize hand area
    hand_area = host.hand_area(owner="host")
    host.drag(hand_area, 0, 200)
    size = hand_area.size()
    host.drag(hand_area, 200, 30, pos='lower right corner')
    assert size.width + 200 == hand_area.size().width and size.height + 30 == hand_area.size().height


def test_put_cards_in_hand(server, browser: webdriver.Firefox, another_browser: webdriver.Firefox):
    host = GameHelper(browser)
    host.go(TOP)
    host.menu.import_jsonfile(str(Path(__file__).parent / "./table_for_e2etests.json"))

    host.should_have_text("you are host")
    host.menu.add_my_hand_area.click()

    # creating and joining new game
    WebDriverWait(browser, 5).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "div.component:nth-of-type(5)")))

    hand_area = browser.find_element_by_css_selector(".component:nth-of-type(5)")
    ActionChains(browser).move_to_element(hand_area).click_and_hold().move_by_offset(0, 50).release().perform()
    hand_area_rect = rect(hand_area)
    card = browser.find_element_by_css_selector(".component:nth-of-type(3)")
    card_rect = rect(card)
    ActionChains(browser).move_to_element(card).click_and_hold().move_by_offset(
        hand_area_rect["left"] - card_rect["left"], hand_area_rect["top"] - card_rect["left"]).release().perform()

    another = GameHelper(another_browser)
    another.go(browser.current_url)
    another.menu.join("Player 2")
    WebDriverWait(another_browser, 5).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "div.component:nth-of-type(5)")))
    card_on_another = another_browser.find_element_by_css_selector(".component:nth-of-type(3)")
    card_pos_before_drag = compo_pos(another_browser, card_on_another)
    ActionChains(another_browser).move_to_element(card_on_another).click_and_hold().move_by_offset(50, 50).perform()
    assert card_pos_before_drag == compo_pos(another_browser, card_on_another), "not moved"


@pytest.mark.usefixtures("server")
class TestHandArea:
    def put_one_card_each_on_2_hand_areas(self, host, another):
        host.go(TOP)
        host.should_have_text("you are host")

        host.menu.add_my_hand_area.click()
        host.move_card_to_hand_area(host.component_by_name('S01'), 'host')

        another.go(host.current_url)
        another.menu.join("Player 2")
        another.should_have_text("you are Player 2")

        another.menu.add_my_hand_area.click()
        another.move_card_to_hand_area(another.component_by_name('S02'), 'Player 2')

        host.double_click(host.component_by_name('S01'))
        another.double_click(another.component_by_name('S02'))

    def test_cards_in_hand_are_looks_facedown(self, browser: webdriver.Firefox, another_browser: webdriver.Firefox):
        host = GameHelper(browser)
        another = GameHelper(another_browser)
        self.put_one_card_each_on_2_hand_areas(host, another)

        # assert text
        assert '♠A' in host.component_by_name('S01').face()
        assert '♠A' not in another.component_by_name('S01').face()
        assert '♠2' not in host.component_by_name('S02').face()
        assert '♠2' in another.component_by_name('S02').face()

        # assert image
        assert 'card_up.png' in host.component_by_name('S01').face()
        assert 'card_back.png' in another.component_by_name('S01').face()
        assert 'card_back.png' in host.component_by_name('S02').face()
        assert 'card_up.png' in another.component_by_name('S02').face()

    def test_up_card_in_my_hand_become_down_when_moved_to_others_hand(self, browser: webdriver.Firefox, another_browser: webdriver.Firefox):
        host = GameHelper(browser)
        another = GameHelper(another_browser)
        self.put_one_card_each_on_2_hand_areas(host, another)

        # assert text
        assert '♠A' not in host.component_by_name('S01').face()
        assert '♠A' in another.component_by_name('S01').face()
        assert '♠2' in host.component_by_name('S02').face()
        assert '♠2' not in another.component_by_name('S02').face()

        # assert image
        assert 'card_back.png' in host.component_by_name('S01').face()
        assert 'card_up.png' in another.component_by_name('S01').face()
        assert 'card_up.png' in host.component_by_name('S02').face()
        assert 'card_back.png' in another.component_by_name('S02').face()

    def test_cards_on_hand_area_follows_when_hand_are_is_moved(self, browser: webdriver.Firefox, another_browser: webdriver.Firefox):
        host = GameHelper(browser)
        another = GameHelper(another_browser)
        self.put_one_card_each_on_2_hand_areas(host, another)

        host_card = host.component_by_name('S01')
        host_card_pos = host_card.pos()
        hand_area = host.hand_area(owner="host")
        host.drag(host_card, -100, 0)
        host.drag(hand_area, 600, 100)
        assert host_card_pos.left + 600 == host_card.pos().left
        assert host_card_pos.top + 100 == host_card.pos().top

        # host_card is still owned by host
        assert '♠A' in host.component_by_name('S01').face()
        assert '♠A' not in another.component_by_name('S01').face()

        host.double_click(host_card)
        assert '♠A' not in host.component_by_name('S01').face()
        assert '♠A' not in another.component_by_name('S01').face()

        host.double_click(host_card)
        assert '♠A' in host.component_by_name('S01').face()
        assert '♠A' not in another.component_by_name('S01').face()


@pytest.mark.usefixtures("server")
class TestDice:
    def test_add_dice_from_menu(self, browser: webdriver.Firefox):
        host = GameHelper(browser)
        host.go(TOP)
        host.should_have_text("you are host")

        host.menu.add_component.execute()
        host.menu.add_component_from_list("Dice (Blue)")

        assert host.component_by_name("Dice (Blue)")

    def test_show_number_of_dices_on_the_table(self, browser: webdriver.Firefox):
        host = GameHelper(browser)
        host.go(TOP)
        host.should_have_text("you are host")
        host.menu.add_component.execute()

        host.menu.add_component_from_list("Dice (Blue)")
        host.should_have_text("1 on the table")

        host.menu.add_component_from_list("Dice (Blue)")
        host.should_have_text("2 on the table")

    @pytest.mark.skip
    def test_add_by_dragging(self, browser: webdriver.Firefox):
        pass

    @pytest.mark.skip
    def test_roll(self, browser: webdriver.Firefox):
        pass

    @pytest.mark.skip
    def test_remove_dice_from_table(self, browser: webdriver.Firefox):
        pass
