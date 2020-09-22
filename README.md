# Dual Universe read in Market Prices
## Installtion

clone repo

``pip install -r requirements.txt``

install tesseract\
https://tesseract-ocr.github.io/tessdoc/Home.html

Change Dual Universe to window mode and set the resolution to 1920x1080 (If your Screen resolution is 1920x1080 change the window mode to borderless). And set the Language to German.
##Usage
````cmd
cd DUMarketPrices
````
Now you can run
````cmd
python main.py
````
use the flag:\
``--product``\
the product you want to search on the market, repeat this option to specify a list of values

for more flags nad information use\
``-help``

### Manuel Offset
Make a Screenshot with Dual Universe open (with the right setting).
Open it in any software that shows you pixel coordinates
locate the pixel where the red lines are pointing (which you can see in the Image Below) and get the ``x`` and ``y`` coordinates of it.\
``python main.py --use_manual_offset true --offset x --offset y --product yourproduct``

![t](https://i.imgur.com/DldbJJU.png)

