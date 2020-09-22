import cv2
import numpy as np
import pytesseract
import win32gui
from pytesseract import Output

from Objects import Square

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def change_color(image, color_from, color_to):  # [72, 57, 34]
    mask = np.all(image == color_from, axis=-1)
    image[mask] = color_to


def sub_array(array, square: Square):
    tl_x, tl_y = square.tl
    br_x, br_y = square.br
    return array[tl_y:br_y, tl_x:br_x]


def scala_image(array, scale, interpolation=cv2.INTER_LINEAR):
    if scale == 0:
        return array
    h, w = array.shape[0], array.shape[1]
    return cv2.resize(array, (int(w + w * scale), int(h + h * scale)), interpolation=interpolation)


def concat_mag(arrays: list, offset: int, horizontal=False, scalar=0):
    if horizontal:
        height = max([x.shape[0] for x in arrays])
        if len(arrays[0].shape) == 3:
            img = np.zeros([height, sum([x.shape[1] + offset * 2 + 2 for x in arrays]), 3], dtype=np.uint8)
        else:
            img = np.zeros([height, sum([x.shape[1] + offset * 2 + 2 for x in arrays])], dtype=np.uint8)
        # fill = np.zeros((height, 2, 3), dtype=np.uint8)
        # fill.fill(255)
        x = offset
        # last_one = len(arrays) - 1
        for index, array in enumerate(arrays):
            img[0:array.shape[0], x:x + array.shape[1]] = array
            x = x + array.shape[1] + offset
            # if index != last_one:
            # img[0:height, x:x + 2] = fill
            #    x = x + 7
        return scala_image(img, scalar)
    else:
        width = max([x.shape[1] for x in arrays])
        if len(arrays[0].shape) == 3:
            img = np.zeros([sum([x.shape[0] + offset for x in arrays]), width, 3], dtype=np.uint8)
        else:
            img = np.zeros([sum([x.shape[0] + offset for x in arrays]), width], dtype=np.uint8)
        y = offset
        for array in arrays:
            img[y: y + array.shape[0], 0:array.shape[1]] = array
            y = y + array.shape[0] + offset
        return scala_image(img, scalar)


def keep_only_white(array):
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    cv2.imwrite("images/all_orders_image_gray_scale.png", gray)
    # threshhold
    ret, bin = cv2.threshold(gray, 22, 44, cv2.THRESH_BINARY)
    # closing
    kernel = np.ones((1, 1), np.uint8)
    closing = cv2.morphologyEx(bin, cv2.MORPH_CROSS, kernel)

    # invert black/white
    inv = cv2.bitwise_not(closing)
    return inv


def hist_norm(x, bin_edges, quantiles, inplace=False):
    """
    Linearly transforms the histogram of an image such that the pixel values
    specified in `bin_edges` are mapped to the corresponding set of `quantiles`

    Arguments:
    -----------
        x: np.ndarray
            Input image; the histogram is computed over the flattened array
        bin_edges: array-like
            Pixel values; must be monotonically increasing
        quantiles: array-like
            Corresponding quantiles between 0 and 1. Must have same length as
            bin_edges, and must be monotonically increasing
        inplace: bool
            If True, x is modified in place (faster/more memory-efficient)

    Returns:
    -----------
        x_normed: np.ndarray
            The normalized array
    """

    bin_edges = np.atleast_1d(bin_edges)
    quantiles = np.atleast_1d(quantiles)

    if bin_edges.shape[0] != quantiles.shape[0]:
        raise ValueError('# bin edges does not match number of quantiles')

    if not inplace:
        x = x.copy()
    oldshape = x.shape
    pix = x.ravel()

    # get the set of unique pixel values, the corresponding indices for each
    # unique value, and the counts for each unique value
    pix_vals, bin_idx, counts = np.unique(pix, return_inverse=True,
                                          return_counts=True)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution function (which maps pixel
    # values to quantiles)
    ecdf = np.cumsum(counts).astype(np.float64)
    ecdf /= ecdf[-1]

    # get the current pixel value corresponding to each quantile
    curr_edges = pix_vals[ecdf.searchsorted(quantiles)]

    # how much do we need to add/subtract to map the current values to the
    # desired values for each quantile?
    diff = bin_edges - curr_edges

    # interpolate linearly across the bin edges to get the delta for each pixel
    # value within each bin
    pix_delta = np.interp(pix_vals, curr_edges, diff)

    # add these deltas to the corresponding pixel values
    pix += pix_delta[bin_idx]

    return pix.reshape(oldshape)


def prep_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = scala_image(image, 4)
    img_blurred = cv2.medianBlur(image, 3)
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if np.mean(binary) > 127:
        binary = cv2.bitwise_not(img_blurred)
    return binary


def write_string(string, file_name):
    with open(file_name, 'w') as file:
        file.write(string)


def image_to_string(image, only_digits=False):
    if only_digits:
        return pytesseract.image_to_string(image, output_type=Output.STRING, lang='eng',
                                           config='--psm 6 -c tessedit_char_whitelist=0123456789.')
    return pytesseract.image_to_string(image, output_type=Output.STRING, lang='eng',
                                       config='--psm 6 -c '
                                              'user-patterns=tesseract/eng.user-patterns user-words=tesseract/eng.user-words')

