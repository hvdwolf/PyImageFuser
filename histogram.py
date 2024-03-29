import PySimpleGUI as sg
from PIL import Image
Image.LOAD_TRUNCATED_IMAGES = True
import sys

BAR_WIDTH = 1  # width of each bar
BAR_SPACING = 1  # space between each bar
EDGE_OFFSET = 3  # offset from the left edge for first bar
GRAPH_SIZE = DATA_SIZE = (200, 100)  # size in pixels


def draw_graph(curgraph, histogram, grcolor):
    max_histogram = max(histogram)

    curgraph.erase()
    curgraph.draw_line((0, 0), (256, 0))
    for x in range(0, 256, 25):
        curgraph.draw_line((x, -3), (x, 3))                       # tick marks
        if x != 0:
            # numeric labels
            curgraph.draw_text(str(x), (x, -10), color='black')

    #print ("max_histogram value for ", grcolor, ": ", max_histogram, "len ", len(histogram))

    for i in range(len(histogram)):
        graph_value = (histogram[i] / max_histogram * GRAPH_SIZE[1])
        curgraph.draw_rectangle(top_left=(i * BAR_SPACING + EDGE_OFFSET, graph_value),
                                bottom_right=(i * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0),
                                line_color=grcolor, fill_color=grcolor)
        #curgraph.draw_text(text=graph_value, location=(i*BAR_SPACING+EDGE_OFFSET+25, graph_value+10))



def show_histogram(window, imgpath):

    rgraph = window['-RGRAPH-']  # type: sg.Graph
    ggraph = window['-GGRAPH-']
    bgraph = window['-BGRAPH-']

    try:
        image = Image.open(imgpath)
        r, g, b = image.split()
        # print("red\n", r.histogram())

        draw_graph(rgraph, r.histogram(), "red")
        draw_graph(ggraph, g.histogram(), "green")
        draw_graph(bgraph, b.histogram(), "blue")
    except Exception as e:
        print("Error opening this image/file")
        pass



def clean_histogram(window):
    rgraph = window['-RGRAPH-']  # type: sg.Graph
    ggraph = window['-GGRAPH-']
    bgraph = window['-BGRAPH-']

    rgraph.erase()
    ggraph.erase()
    bgraph.erase()
