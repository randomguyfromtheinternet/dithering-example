from PIL import Image
import numpy as np
import math

# Read test PNG Image into Array
image_path = "test.png"
image = Image.open(image_path).convert("L") # import as greyscale
image_array = np.array(image)
print("Image shape: ", image_array.shape)

image_height = image_array.shape[0]
image_width = image_array.shape[1]

# convert to black and white image
bw_image = image_array.copy()
threshold = 128
for x in range(image_width):
    for y in range(image_height):
        if bw_image[y, x] > threshold:
            bw_image[y, x] = 255
        else:
            bw_image[y, x] = 0

writefile = Image.fromarray(bw_image)
writefile.save("bw.png")

# dithering general
dither_length = 3
dither_values = dither_length ** 2
step_width = 256 / dither_values
step_width_center = step_width / 2

dither_thresholds = [i * step_width + step_width_center for i in range(dither_values)]

def index_from_pos(x, y, width, height):
    if x > width or x < 0:
        return -1
    if y > height or y < 0:
        return -1
    
    return x + y * width

def xy_chunks(width, height, chunk_size):
    x_chunks = math.ceil(width / chunk_size)
    y_chunks = math.ceil(height / chunk_size)
    return (x_chunks, y_chunks)

def total_chunks(width, height, chunk_size):
    num_xy_chunks = xy_chunks(width, height, chunk_size)
    return num_xy_chunks[0] * num_xy_chunks[1]

def access_chunk(chunk, index, width, height, chunk_size):
    if(index >= chunk_size ** 2 or index < 0):
        return (-1, -1)

    num_xy_chunks = xy_chunks(width, height, chunk_size)
    num_chunks = total_chunks(width, height, chunk_size)

    if(chunk >= num_chunks or chunk < 0):
        return (-1, -1)

    start_x = chunk % num_xy_chunks[0] * chunk_size
    start_y = math.floor(chunk / num_xy_chunks[0]) * chunk_size

    x = start_x + index % chunk_size
    y = start_y + math.floor(index / chunk_size)

    if(x >= width or x < 0):
        x = -1
    if(y >= height or y < 0):
        y = -1

    return(x, y)


image_chunks = total_chunks(image_width, image_height, dither_length)

#ordered dithering
dithered_ordered_image = image_array.copy()

for chunk in range(image_chunks):
    for index in range(dither_values):
        coordinates = access_chunk(chunk, index, image_width, image_height, dither_length)
        if(coordinates[1] > 0 and coordinates[0] > 0):
            if dithered_ordered_image[coordinates[1], coordinates[0]] >= dither_thresholds[index]:
                dithered_ordered_image[coordinates[1], coordinates[0]] = 255
            else:
                dithered_ordered_image[coordinates[1], coordinates[0]] = 0

writefile = Image.fromarray(dithered_ordered_image)
writefile.save("dithered-ordered.png")

# unordered dithering
dithered_unordered_image = image_array.copy()
for chunk in range(image_chunks):
    
    # Shuffle dither table
    np.random.shuffle(dither_thresholds) 

    for index in range(dither_values):
        coordinates = access_chunk(chunk, index, image_width, image_height, dither_length)
        if(coordinates[1] > 0 and coordinates[0] > 0):
            if dithered_unordered_image[coordinates[1], coordinates[0]] >= dither_thresholds[index]:
                dithered_unordered_image[coordinates[1], coordinates[0]] = 255
            else:
                dithered_unordered_image[coordinates[1], coordinates[0]] = 0

writefile = Image.fromarray(dithered_unordered_image)
writefile.save("dithered-unordered.png")