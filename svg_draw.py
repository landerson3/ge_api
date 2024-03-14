from PIL import ImageDraw
import math

def apply_svg_outline_to_image(svg_data, dest_img):
    w,h = dest_img.size
    # Extracting relevant data from the dictionary
    lines = svg_data['properties']['lines']
    # Create a draw object for the destination image
    draw = ImageDraw.Draw(dest_img)
    # Draw the lines
    for i in range(len(lines)-1):
        x1 = (lines[i]['x']/svg_data['properties']['onCreateCanvasWidth'])*w
        y1 = (lines[i]['y']/svg_data['properties']['onCreateCanvasHeight'])*h
        x2 = (lines[i+1]['x']/svg_data['properties']['onCreateCanvasWidth'])*w
        y2 = (lines[i+1]['y']/svg_data['properties']['onCreateCanvasHeight'])*h
        stroke_wid = math.floor((svg_data['properties']['stroke']/svg_data['properties']['onCreateCanvasWidth'])*w)
        draw.line((x1, y1, x2, y2), fill="red", width=stroke_wid)
    return dest_img