clone repo

``pip install -r requirements.txt``

install tesseract\
https://tesseract-ocr.github.io/tessdoc/Home.html

Change Dual Universe to Windows mode and set the resolution 1920x1080 (If your Screen resolution is 1920x1080 change the Window mode to Borderless and set the offset to 0 0)\
If your Screen is bigger locate the pixel where the red lines are pointing, which you can see in the Image Below. Write the x and y values to the ``offset.config`` file. The first line is for the x value the second for the y value.

![t](https://i.imgur.com/DldbJJU.png)

Open the ``main.py`` script und scroll down where you can change for what products you want to search in the market
for just one product use:
````python 
collect_orders("Bauxit")
````
for a list of products use:
````python
for product in ["Warp-Zelle", "Hämatit", "Quarz"]:
    collect_orders(product)
````
