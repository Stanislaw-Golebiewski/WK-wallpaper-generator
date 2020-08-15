import configparser
from pathlib import Path
from typing import Tuple, Union

import click

from wallpaper_generator import Config, WallpaperFactory


def _cfg_str_to_tuple(text: str) -> Tuple:
    return tuple(map(int, text[1:-1].split(', ')))


def get_config_obj(path: Union[Path, str]) -> Config:
    out_cfg: Config = {}
    config = configparser.ConfigParser()
    config.read_file(open(path, "r", encoding='utf-8'))
    cfg_main = config['main']
    out_cfg['api_key'] = cfg_main['api_key']
    out_cfg['margins'] = _cfg_str_to_tuple(cfg_main['margins'])
    out_cfg['screen'] = _cfg_str_to_tuple(cfg_main['screen'])
    out_cfg['seed'] = int(cfg_main['random_seed'])
    out_cfg['kanji_order'] = cfg_main['kanji_order']
    out_cfg['colors'] = {k: _cfg_str_to_tuple(v) for k, v in config['colors'].items()}
    return out_cfg


@click.command()
@click.option('--config-path', default='./config.ini', help='Path to .ini config file')
def main(config_path):
    config = get_config_obj(config_path)
    wallpaper_gen = WallpaperFactory(config)
    img = wallpaper_gen.generate()
    img.show()


if __name__ == '__main__':
    main()
