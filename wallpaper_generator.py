 # import hashlib
import logging
import math
import os
# import pickle
import random
from pathlib import Path
from typing import Dict, List, NewType, Optional, Tuple, TypedDict, Union

import requests
from PIL import Image, ImageDraw, ImageFont

# logger stuff
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
consoleHandler.setFormatter(formatter)

# (R, G, B)
Color = Tuple[int, int, int]

# (top, right, bottom, left)
Margins = Tuple[int, int, int, int]

# (widht, height)
Screen = Tuple[int, int]

# 'wk_order' | 'random'
KanjiOrder = NewType('KanjiOrder', Union['wk_order', 'random'])

DEFAULT_FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')


class Config(TypedDict):
    api_key: str
    colors: Dict[str, Color]
    margins: Margins
    screen: Screen
    seed: int
    kanji_order: KanjiOrder


class WallpaperFactory:
    def __init__(self, config: Config, store_path: Optional[Union[Path, str]] = None):
        self.api_key = config['api_key']
        self.colors = config['colors']
        self.screen = config['screen']
        self.margins = config['margins']
        self.random_seed = config['seed']
        self.kanji_order = config['kanji_order']
        if store_path:
            logger.debug(f"using store at '{store_path}'")
            self.store_path = store_path
        else:
            dir = os.path.dirname(__file__)
            self.store_path = os.path.join(dir, 'store')
            if not os.path.isdir(self.store_path):
                os.mkdir(self.store_path)
                logger.info(f"Created store directory at '{self.store_path}'")

    def generate(self, force_refresh=False) -> Image:
        # key_id = hashlib.sha224(self.api_key.encode('utf-8')).hexdigest()
        # logger.debug(f"api key hash: {key_id}")
        # load or get user data
        all_kanjis, progress = self._get_api_data()
        kanji_count = len(all_kanjis)

        # determine order
        kanji_ordered: List[Tuple[int, str, int]] = self._get_kanji_order(all_kanjis)

        # get rectangle size and count
        square_size, no_rows, no_cols = self._calc_rect_size(kanji_count)

        # get font
        font = self._get_font('ipag', square_size)

        logger.info(f"drawing {kanji_count} kanjis")

        # create empty image
        out_img = Image.new("RGB", self.screen, self.colors["background"])
        d = ImageDraw.Draw(out_img)

        # draw kanjis
        m_top, m_right, m_bottom, m_left = self.margins
        counter = 0

        y = m_top
        for row in range(no_rows):
            x = m_left
            for col in range(no_cols):
                id, kanji_char, _ = kanji_ordered[counter]
                color = self.colors[str(progress[id])]
                # d.rectangle([x, y, x+square_size, y+square_size], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                d.text((x, y), kanji_char, font=font, fill=color)
                x += square_size
                counter += 1
                if counter >= kanji_count:
                    break
            y += square_size

        # return image
        return out_img

    def _load_user_kanji(self, path: Union[Path, str]):
        pass

    def _save_user_kanji(self, path: Union[Path, str]):
        pass

    def _validate_api_key(self, key):
        pass

    def _get_kanji_order(self, kanji_dict: Dict[int, Tuple[str, int]]) -> List[Tuple[int, str, int]]:
        kanji_list = [(k, v[0], v[1]) for k, v in kanji_dict.items()]

        if self.kanji_order == 'wk_order':
            kanji_list = sorted(kanji_list, key=lambda x: x[2])
        else:
            random.seed(self.random_seed)
            random.shuffle(kanji_list)

        return kanji_list

    def _get_font(self, name: str, size: int) -> ImageFont:
        return ImageFont.truetype(f'{DEFAULT_FONT_DIR}/{name}.ttf', size)

    def _calc_rect_size(self, no_symbols: int) -> Tuple[int, int, int]:
        # get width and height of final area where we can draw rectangles with kanji
        # area_width = screen_width - margin_right - margin_left
        width = self.screen[0] - self.margins[1] - self.margins[3]
        # area_height = screen_height - margin_top - margin_bottom
        height = self.screen[1] - self.margins[0] - self.margins[2]

        # w try to minimize horizontal leftover space by gradually decressing single square size until all rectangles (kanjis) will fit target area
        leftover_y = -1
        single_square_area = math.floor(width * height / no_symbols)
        size = math.floor(math.sqrt(single_square_area))
        while(leftover_y < 0):
            columns = math.floor(width / size)
            rows = math.ceil(no_symbols / columns)
            leftover_y = height - rows * size
            if leftover_y < 0:
                size -= 1
        return (size, rows, columns)

    def _get_api_data(self):
        next_url = "https://api.wanikani.com/v2/subjects?types=kanji"

        # kanji_id: (kanij_char, kanji_level)
        kanji_dict: Dict[int, Tuple[str, int]] = {}

        # kanji_id: kanji_level
        progress_dict: Dict[int, int] = {}
        headers = {'Wanikani-Revision': '20170710',
                   'Authorization': f"Bearer {self.api_key}"}

        # get kanji data
        while next_url:
            logger.debug(f"> GET request on {next_url}")
            response = requests.get(next_url, headers=headers)
            if response.status_code != 200:
                response.raise_for_status()

            response_body = response.json()
            next_url = response_body['pages']['next_url']
            for kanji in response_body['data']:
                kanji_dict[kanji['id']] = (kanji['data']["characters"], kanji['data']['level'])
                progress_dict[kanji['id']] = 'unknown'

        # get user progress data
        next_url = 'https://api.wanikani.com/v2/assignments?subject_types=kanji'

        while next_url:
            logger.debug(f"> GET request on {next_url}")
            response = requests.get(next_url, headers=headers)
            if response.status_code != 200:
                response.raise_for_status()

            response_body = response.json()
            next_url = response_body['pages']['next_url']
            for asg in response_body['data']:
                stage_name = asg['data']['srs_stage']
                kanji_id = asg['data']['subject_id']
                progress_dict[kanji_id] = stage_name

        return kanji_dict, progress_dict
