import configparser
import os
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


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.ini')

@click.command()
@click.option('--config-path', default=DEFAULT_CONFIG_PATH, help='Path to .ini config file')
@click.option('--out-path', default=f'./image.png', help='Where to put ')
def main(config_path, out_path):
    config = get_config_obj(config_path)
    wallpaper_gen = WallpaperFactory(config)
    img = wallpaper_gen.generate()
    img.save(out_path)


if __name__ == '__main__':
    main()
