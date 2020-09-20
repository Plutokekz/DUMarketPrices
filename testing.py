import cv2
import numpy as np

from main import buy_orders_price_amount_square, buy_orders_market_time_square
from utils import sub_array, image_to_string, scala_image


def write_string(string, file_name):
    with open(file_name, 'w') as file:
        file.write(string)


def prep_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = scala_image(image, 4)
    img_blurred = cv2.medianBlur(image, 3)
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if np.mean(binary) > 127:
        binary = cv2.bitwise_not(img_blurred)
    return binary


while True:
    test_image = cv2.imread("images/market_place_search.png")
    price = sub_array(test_image, buy_orders_price_amount_square)
    place = sub_array(test_image, buy_orders_market_time_square)

    price = prep_image(price)
    place = prep_image(place)

    print(f"Amount and Price: {image_to_string(price, only_digits=True)}")
    print(f"Current Market Place: {image_to_string(place)}")
    cv2.imwrite("images/order_price.png", price)
    cv2.imwrite("images/order_place.png", place)
    break

    # cv2.imshow("Test 2.0", gray)
    cv2.imshow("Test 2.1", binary)

    key = cv2.waitKey(32)
    if key == ord('q'):
        cv2.destroyAllWindows()
        break
