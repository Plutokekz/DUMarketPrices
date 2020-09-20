import cv2
import pyautogui
from tqdm import tqdm

from Objects import Square
from ScreenCapture import WindowCapture
from utils import sub_array, image_to_string, prep_image, read_offset_config

x_off, y_off = read_offset_config()

window = WindowCapture(1920, 1080, (x_off, y_off))

search_field_square = Square((412, 129), (680, 162))
search_field_clear_square = Square((656, 140), (668, 152))

number_of_buy_orders_square = Square((881, 195), (1001, 212))
buy_orders_sort_by_markets_square = Square((1319, 249), (1366, 256))
buy_orders_price_amount_square = Square((735, 271), (1110, 300))
buy_orders_market_time_square = Square((1321, 271), (1577, 300))

number_of_sell_orders_square = Square((937, 625), (1056, 642))
sell_orders_sort_buy_market_square = Square((1320, 679), (1365, 688))
sell_orders_price_amount_square = Square((735, 701), (1109, 730))
sell_orders_market_time_square = Square((1320, 701), (1576, 730))


def collect_orders(product):
    x, y = window.get_screen_position(search_field_clear_square.center())
    pyautogui.moveTo(x, y)
    pyautogui.sleep(1)
    pyautogui.click()

    x, y = window.get_screen_position(search_field_square.center())
    pyautogui.moveTo(x, y)
    pyautogui.sleep(1)
    pyautogui.click()
    pyautogui.sleep(1)
    pyautogui.write(product)
    pyautogui.sleep(1)

    prices, places = scroll_through_orders(number_of_buy_orders_square, buy_orders_sort_by_markets_square,
                                           buy_orders_price_amount_square, buy_orders_market_time_square)

    write_to_file("buy_orders_" + product, prices, places)

    game = window.get_screenshot()
    cv2.imwrite("images/number_of_sell_orders.png", sub_array(game, number_of_sell_orders_square))

    prices, places = scroll_through_orders(number_of_sell_orders_square, sell_orders_sort_buy_market_square,
                                           sell_orders_price_amount_square, sell_orders_market_time_square)

    write_to_file("sell_orders_" + product, prices, places)


def scroll_through_orders(number_of_orders_square, sort_markets_square, price_amount_square, place_expire_square):
    game = window.get_screenshot()

    # Amount of Orders
    number_of_buy_orders_image = sub_array(game, number_of_orders_square)
    number = image_to_string(prep_image(number_of_buy_orders_image), only_digits=True)

    try:
        number = int(number)
    except Exception as e:
        print(str(e))
        number = 700  # Some random number
    print(f"Currently {number} Buy Orders")

    x, y = window.get_screen_position(sort_markets_square.center())
    pyautogui.moveTo(x, y)
    pyautogui.click()

    x, y = window.get_screen_position(price_amount_square.center())
    pyautogui.moveTo(x, y)
    pyautogui.sleep(1)
    orders_price = []
    order_place = []

    game = window.get_screenshot()
    cv2.imwrite("images/screen.png", game)

    for _ in tqdm(range(0, number - 5)):
        game = window.get_screenshot()
        buy_order_price_amount_image = sub_array(game, price_amount_square)
        buy_order_price_amount_image = prep_image(buy_order_price_amount_image)
        orders_price.append(buy_order_price_amount_image)

        buy_order_market_time_image = sub_array(game, place_expire_square)
        buy_order_market_time_image = prep_image(buy_order_market_time_image)
        order_place.append(buy_order_market_time_image)

        pyautogui.scroll(-250)

    # last 5:
    for i in tqdm(range(1, 6)):
        price_amount_square.add_y_offset(int(30))
        x, y = window.get_screen_position(price_amount_square.center())
        pyautogui.moveTo(x, y)
        pyautogui.sleep(0.1)
        game = window.get_screenshot()
        buy_order_price_amount_image = sub_array(game, price_amount_square)
        buy_order_price_amount_image = prep_image(buy_order_price_amount_image)
        orders_price.append(buy_order_price_amount_image)

        place_expire_square.add_y_offset(int(30))
        buy_order_market_time_image = sub_array(game, place_expire_square)
        buy_order_market_time_image = prep_image(buy_order_market_time_image)
        order_place.append(buy_order_market_time_image)

        cv2.imwrite(f"images/price_{i}.png", buy_order_price_amount_image)
        cv2.imwrite(f"images/place_{i}.png", buy_order_market_time_image)
    price_amount_square.reset()
    place_expire_square.reset()

    return orders_price, order_place


def write_to_file(file_name, prices, places):
    file = open(f"orders/{file_name}.csv", "w")
    for index, value in tqdm(enumerate(zip(prices, places))):
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
            cv2.imwrite(f"images/error/price_{str(e)}_{pr}_{index}.png", price_image)
            cv2.imwrite(f"images/error/place_{str(e)}_{index}.png", place_image)
    file.close()


for product in ["Warp-Zelle"]:
    collect_orders(product)
