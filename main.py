from absl import flags, app

from Bot import Market
from ScreenCapture import WindowCapture

flags.DEFINE_multi_string('product', ['Warp-Zelle'], "the product you want to search on the market")
flags.DEFINE_string('window_name', "Dual Universe", "The Window name of Dual Universe")
flags.DEFINE_boolean('use_manual_offset', False, 'Use the manual offset from --offset and not the calculated one.')
flags.DEFINE_multi_integer('offset', [0, 0], 'the x and y offset of the Dual Universe window')
flags.DEFINE_boolean('debug', False, 'Produces debugging output.')
FLAGS = flags.FLAGS


def main(argv):
    del argv
    window = WindowCapture(FLAGS.window_name, manual_offset=FLAGS.use_manual_offset, offset=FLAGS.offset)
    market = Market(window)
    for product in FLAGS.product_list:
        market.collect_orders(product)


if __name__ == '__main__':
    app.run(main)

