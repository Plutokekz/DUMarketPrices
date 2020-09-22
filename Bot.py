import time

import cv2
import pyautogui
from tqdm import tqdm

from ScreenCapture import WindowCapture
from Statics import *
from utils import sub_array, image_to_string, prep_image


class CantFindNumberError(Exception):
    def __init__(self, image, result, message="Cant get numbers of orders from the given Image"):
        self.error_path = "images/error"
        self.image = image
        self.message = message
        self.result = result
        self.save_error_image()
        super().__init__(self.message)

    def save_error_image(self):
        class_name = str(self.__class__).split("'")[1]
        cv2.imwrite(f"{self.error_path}/{class_name}_{time.time_ns()}.png", self.image)

    def __str__(self):
        return f'{self.result} -> {self.message}'


class Market:
    # TODO check scrollbar if on bottom scroll to top
    def __init__(self, window: WindowCapture):
        self.window = window
        self.path = "orders"
        self.error_path = "images/error"
        cv2.imwrite("images/screen.png", window.get_screenshot())
        if not window.manual_offset:
            window.window_to_foreground()

    def _click(self, coord):
        x, y = self.window.get_screen_position(coord)
        pyautogui.moveTo(x, y)
        pyautogui.sleep(0.1)
        pyautogui.click()

    def _clear_search_field(self):
        self._click(search_field_clear_square.center())

    def _search_search_field(self, product):
        self._click(search_field_square.center())
        pyautogui.write(product)
        pyautogui.sleep(0.4)

    def collect_orders(self, product):
        print(product)
        self._clear_search_field()
        self._search_search_field(product)

        # Buy Orders
        prices, places = self._scroll_through_orders(number_of_buy_orders_square, buy_orders_sort_by_markets_square,
                                                     buy_orders_price_amount_square, buy_orders_market_time_square,
                                                     "buy")

        self._write_to_file("buy_orders_" + product, prices, places, "buy")

        # Sell Orders
        prices, places = self._scroll_through_orders(number_of_sell_orders_square, sell_orders_sort_buy_market_square,
                                                     sell_orders_price_amount_square, sell_orders_market_time_square,
                                                     "sell")

        self._write_to_file("sell_orders_" + product, prices, places, "sell")

    def _scroll_through_orders(self, number_of_orders_square, sort_markets_square, price_amount_square,
                               place_expire_square, sell_or_buy):
        game = self.window.get_screenshot()

        # Amount of Orders
        number_of_buy_orders_image = prep_image(sub_array(game, number_of_orders_square))
        number = image_to_string(number_of_buy_orders_image, only_digits=True)
        number = number.split("\n")[0]
        try:
            number = int(number)
        except ValueError:
            raise CantFindNumberError(number_of_buy_orders_image, number)

        print(f"read in {sell_or_buy} orders: {number}")

        self._click(sort_markets_square.center())

        x, y = self.window.get_screen_position(price_amount_square.center())
        pyautogui.moveTo(x, y)
        pyautogui.sleep(0.1)
        orders_price, order_place = [], []

        for _ in tqdm(range(0, number - 5)):
            game = self.window.get_screenshot()
            buy_order_price_amount_image = sub_array(game, price_amount_square)
            buy_order_price_amount_image = prep_image(buy_order_price_amount_image)
            orders_price.append(buy_order_price_amount_image)

            buy_order_market_time_image = sub_array(game, place_expire_square)
            buy_order_market_time_image = prep_image(buy_order_market_time_image)
            order_place.append(buy_order_market_time_image)

            pyautogui.scroll(-250)

        # last 5:
        for _ in tqdm(range(1, 6)):
            price_amount_square.add_y_offset(int(30))
            x, y = self.window.get_screen_position(price_amount_square.center())
            pyautogui.moveTo(x, y)
            pyautogui.sleep(0.1)
            game = self.window.get_screenshot()
            buy_order_price_amount_image = sub_array(game, price_amount_square)
            buy_order_price_amount_image = prep_image(buy_order_price_amount_image)
            orders_price.append(buy_order_price_amount_image)

            place_expire_square.add_y_offset(int(30))
            buy_order_market_time_image = sub_array(game, place_expire_square)
            buy_order_market_time_image = prep_image(buy_order_market_time_image)
            order_place.append(buy_order_market_time_image)

        price_amount_square.reset()
        place_expire_square.reset()

        return orders_price, order_place

    def _write_to_file(self, file_name, prices, places, sell_ore_buy):
        file = open(f"{self.path}/{file_name}.csv", "w")
        print(f"Analyse {sell_ore_buy} Orders")
        for index, value in tqdm(enumerate(zip(prices, places)), total=len(prices)):
            price_image, place_image = value
            pr = image_to_string(price_image, only_digits=True).split("\n")[0].replace("\n", "")
            pl = image_to_string(place_image).split("\n")[0].replace("\n", "")
            try:
                price, amount = pr.split(" ")
                place_list = pl.split(" ")
                time = place_list[-1]
                place = " ".join(place_list[:len(place_list) - 1])
                if time == "min":
                    time = " ".join(place_list[-2:])
                    place = " ".join(place_list[:len(place_list) - 2])
                file.write(f"{price}, {amount}, {place}, {time}\n")
            except Exception as e:
                print(str(e))
                print(f"Current Image Error, write image to: {self.error_path}/price_{str(e)}_{pr}_{index}.png")
                cv2.imwrite(f"{self.error_path}/price_{str(e)}_{pr}_{index}.png", price_image)
                cv2.imwrite(f"{self.error_path}/place_{str(e)}_{index}.png", place_image)
        file.close()
