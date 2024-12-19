import time

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import clear_output


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    # Sum of (x, y) for top-left and bottom-right
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left
    rect[2] = pts[np.argmax(s)]  # Bottom-right

    # Difference of (x, y) for top-right and bottom-left
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right
    rect[3] = pts[np.argmax(diff)]  # Bottom-left

    return rect


def transform_perspective(input_image, rect, scaling):
    rect = np.squeeze(rect).astype(np.float32) / scaling
    rect = order_points(rect)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)  # Distance between bottom-right and bottom-left
    widthB = np.linalg.norm(tr - tl)  # Distance between top-right and top-left
    width = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)  # Distance between top-right and bottom-right
    heightB = np.linalg.norm(tl - bl)  # Distance between top-left and bottom-left
    height = int(max(heightA, heightB))

    # Destination points for the perspective transform
    dst = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
    M = cv.getPerspectiveTransform(rect, dst)

    warped = cv.warpPerspective(input_image, M, (width, height))
    return warped


def detect_rectangles(image_path=None, image=None, debug=False):
    # Load the image
    if image_path is not None:
        image = cv.imread(image_path)

    scaling = 640 / max(image.shape[:-1])
    work_image = cv.resize(image, (round(image.shape[1] * scaling), round(image.shape[0] * scaling)))

    gray = cv.cvtColor(work_image, cv.COLOR_BGR2GRAY)

    # Preprocessing
    blurred = cv.GaussianBlur(gray, (3, 3), 0)
    edges = cv.Canny(blurred, 50, 150)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    closed = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel)

    # Find contours and hierarchy
    contours, hierarchy = cv.findContours(closed, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    if hierarchy is not None:
        hierarchy = hierarchy[0]  # Get the first hierarchy level

    rectangles = []
    centers = []
    for i, contour in enumerate(contours):
        # Exclude contained shapes (contours with a parent)
        if hierarchy[i][3] == -1:  # Check if the contour has no parent
            # Approximate contour
            epsilon = 0.03 * cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, epsilon, True)

            # Check for quadrilateral
            if len(approx) == 4 and cv.isContourConvex(approx) and cv.contourArea(approx) >= 500:
                # print(cv.contourArea(approx))
                rectangles.append(approx)
                centers.append(np.divide(np.squeeze(approx).mean(axis=0)[::-1], work_image.shape[:-1]))

    if debug:
        # Draw outer rectangles on the original image
        transformed = []
        for rect in rectangles:
            cv.drawContours(work_image, [rect], -1, (0, 255, 0), 2)

            transformed.append(transform_perspective(image, rect,
                                                     scaling))  # plt.imshow(cv.cvtColor(transformed, cv.COLOR_BGR2RGB))  # print(len(rectangles))

        number = len(transformed)
        for i in range(number):
            plt.subplot(1, number, i + 1), plt.imshow(cv.cvtColor(transformed[i], cv.COLOR_BGR2RGB))
            plt.axis('off')
        clear_output()
        plt.show()
        plt.subplot(121), plt.imshow(cv.cvtColor(work_image, cv.COLOR_BGR2RGB))
        plt.axis('off')
        plt.subplot(122), plt.imshow(closed)
        plt.axis('off')
        plt.show()

    if not rectangles:
        return False, None, None

    transformed = [cv.cvtColor(transform_perspective(image, rectangle, scaling), cv.COLOR_BGR2RGB) for rectangle in
                   rectangles]

    return True, transformed, centers


if __name__ == '__main__':
    camera = cv.VideoCapture(1)
    print("connected camera")

    found = False
    while not found:
        check, image = camera.read()
        if check and image is not None and type(image) is np.ndarray:
            found, images, centers = detect_rectangles(image=image, debug=True)
            time.sleep(1)

    print("found image")

    camera.release()

    for image, position in zip(images, centers):
        plt.imshow(image)
        plt.title(str(position))
        plt.show()
