### WaniKani wallpaper generator

Generate wallpeaper filled with colorfull kanji signs, based on your progress on [WaniKani](https://www.wanikani.com/) platform!

<p align="center">
  <img alt="img-name" src="/examples/2.png" width="300">
  <br>
    <em>WaniKani kanji order</em>
</p>

<p align="center">
  <img alt="img-name" src="/examples/1.png" width="300">
  <br>
    <em>Random kanji order</em>
</p>

#### Requirements

* python 3.6 <=

#### Installation

I recommend to use [virtualenv](https://www.pythonforbeginners.com/basics/how-to-use-python-virtualenv):
```
> virtualenv venv
> source ./venv/bin/activate
> pip install -r requirements.txt
```
But one can just do this:
```
pip install -r requirements.txt
```

#### Basic usage

```
> mv example.config.ini config.ini
> (here add your api-key to config.ini)
> python cli.py 
```

##### Available configuration cli options

| argument   | required? | default      | description         |
|------------|-----------|--------------|---------------------|
| `--config` | **no**    | _config.ini_ | path to config file |
