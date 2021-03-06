from pathlib import Path
import pytest
from selenium import webdriver
from ..helper import GameHelper, TOP


def upload_kit(host, filename, image_filenames=[]):
    host.menu.open_toolbox.execute()
    host.toolbox.use(host.toolbox.upload_kit)
    host.toolbox.upload_kit.select_json_file(str(Path(__file__).parent / filename))
    if image_filenames:
        image_paths = [str(Path(__file__).parent / fn) for fn in image_filenames]
        host.toolbox.upload_kit.select_image_files('\n'.join(image_paths))
    host.toolbox.upload_kit.upload()
    host.toolbox.upload_kit.accept_success_alert()


@pytest.mark.usefixtures("server")
@pytest.mark.usefixtures("default_kits_and_components")
class TestUploadKit:
    def test_success(self, browser: webdriver.Firefox):
        host = GameHelper.player(browser)
        upload_kit(host, 'test_menu_kit.json')

        host.menu.add_kit.execute()
        host.menu.should_see_kit("Test Kit")

    def test_cancel(self, browser: webdriver.Firefox):
        host = GameHelper.player(browser)

        host.menu.open_toolbox.execute()
        host.toolbox.use(host.toolbox.upload_kit)
        host.toolbox.upload_kit.cancel()

        host.menu.add_kit.execute()
        host.menu.should_not_see_kit("Test Kit")

    def test_no_jsonfile(self, browser: webdriver.Firefox):
        host = GameHelper.player(browser)

        host.menu.open_toolbox.execute()
        host.toolbox.use(host.toolbox.upload_kit)
        host.toolbox.upload_kit.upload()
        host.toolbox.upload_kit.accept_failure_alert()

        host.menu.add_kit.execute()
        host.menu.should_not_see_kit("Test Kit")

    class TestUploadImage:
        def test_one_image(self, browser: webdriver.Firefox):
            host = GameHelper.player(browser)
            upload_kit(host, 'test_menu_kit_with_one_image.json', ['example.png'])

            host.menu.add_kit.execute()
            host.menu.add_kit_from_list("Test Kit")
            host.menu.add_kit_done()

            assert '/images/uploaded/example.png' in host.component_by_name('Test Component').face()

        @pytest.mark.skip
        def test_image(self, browser: webdriver.Firefox):
            pass

        @pytest.mark.skip
        def test_faceup_image(self, browser: webdriver.Firefox):
            pass

        @pytest.mark.skip
        def test_facedown_image(self, browser: webdriver.Firefox):
            pass

        @pytest.mark.skip
        def test_multiple_images(self, browser: webdriver.Firefox):
            pass

