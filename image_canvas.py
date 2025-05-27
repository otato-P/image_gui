from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QRect
import cv2
import numpy as np
#from image_processing.roi_fitting import fit_roi_data
from image_processing.roi_fitting import fit_roi_data




class ImageCanvas(QLabel):
    def __init__(self):
        super().__init__()
        self.image = None
        self.start = None
        self.end = None
        self.rect = None
        self.drawing = False
        #self.setFixedSize(600, 400)
        self.scale_x = 1
        self.scale_y = 1
        self.offset_x = 0
        self.offset_y = 0
        

    # def setImage(self, image):
    #     self.image = image
    #     qimage = self.convertToQImage(image)
    #     #self.setPixmap(QPixmap.fromImage(qimage))
        
    #     pixmap = QPixmap.fromImage(qimage)
    #     # 缩放图片到控件大小，保持比例
    #     scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #     self.setPixmap(scaled_pixmap)

    # def setImage(self, image):
    #     self.image = image
    #     self.updatePixmap()
    def setImage(self, image):
        self.image = image
        qimage = self.convertToQImage(image)
        pixmap = QPixmap.fromImage(qimage)
        
        # 缩放图片到控件大小，保持比例
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

        # 记录缩放比例
        self.scale_x = image.shape[1] / scaled_pixmap.width()
        self.scale_y = image.shape[0] / scaled_pixmap.height()
        
        # 记录偏移（如果图像居中显示，会有边距）
        self.offset_x = (self.width() - scaled_pixmap.width()) // 2
        self.offset_y = (self.height() - scaled_pixmap.height()) // 2

    #界面坐标转为原图坐标
    def mapToOriginal(self, point):
        x = (point.x() - self.offset_x) * self.scale_x
        y = (point.y() - self.offset_y) * self.scale_y
        return int(x), int(y)


    # def updatePixmap(self):
    #     if self.image is None:
    #         return
    #     qimage = self.convertToQImage(self.image)
    #     pixmap = QPixmap.fromImage(qimage)
    #     scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #     self.setPixmap(scaled_pixmap)
    def updatePixmap(self):
        if self.image is None:
            return
        qimage = self.convertToQImage(self.image)
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_pixmap)
        # 重新计算比例和偏移，保证映射准确
        self.scale_x = self.image.shape[1] / scaled_pixmap.width()
        self.scale_y = self.image.shape[0] / scaled_pixmap.height()
        self.offset_x = (self.width() - scaled_pixmap.width()) // 2
        self.offset_y = (self.height() - scaled_pixmap.height()) // 2

    def resizeEvent(self, event):
        self.updatePixmap()
        super().resizeEvent(event)

    def convertToQImage(self, image):
        height, width, channels = image.shape
        bytes_per_line = channels * width
        return QImage(image.data, width, height, bytes_per_line, QImage.Format_BGR888)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start and self.end:
            self.drawing = False
            self.rect = QRect(self.start, self.end).normalized()
            print("Mouse released, processing selected region.")
            self.processSelectedRegion()
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton and self.start and self.end:
    #         self.drawing = False

    #         # # 假设你使用 QGraphicsView 显示图像
    #         # scene_start = self.mapToScene(self.start)
    #         # scene_end = self.mapToScene(self.end)

    #         # image_item 是你展示图像的 QGraphicsPixmapItem
    #         image_start = self.image_item.mapFromScene(scene_start)
    #         image_end = self.image_item.mapFromScene(scene_end)

    #         # 转换为整数图像坐标
    #         x1, y1 = int(image_start.x()), int(image_start.y())
    #         x2, y2 = int(image_end.x()), int(image_end.y())

    #         # 构造 ROI 区域
    #         x1, x2 = sorted([x1, x2])
    #         y1, y2 = sorted([y1, y2])

    #         print("Mouse released, processing selected region.")
    #         print(f"Selected region: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

    #         # 保存为图像 ROI 坐标供后续使用
    #         self.roi_start = (x1, y1)
    #         self.roi_end = (x2, y2)

    #         self.processSelectedRegion()

    # def processSelectedRegion(self):
    #     if self.rect and self.image is not None:
    #         x1, y1, x2, y2 = self.rect.left(), self.rect.top(), self.rect.right(), self.rect.bottom()
    #         roi = self.image[y1:y2, x1:x2]
    #         fit_roi_data(roi)
    # def processSelectedRegion(self):
    #     if self.rect and self.image is not None:
    #         # 映射到原始图像坐标
    #         top_left = self.mapToOriginal(self.rect.topLeft())
    #         bottom_right = self.mapToOriginal(self.rect.bottomRight())
    #         x1, y1 = top_left
    #         x2, y2 = bottom_right

    #         # 边界裁剪
    #         x1 = max(0, min(self.image.shape[1], x1))
    #         x2 = max(0, min(self.image.shape[1], x2))
    #         y1 = max(0, min(self.image.shape[0], y1))
    #         y2 = max(0, min(self.image.shape[0], y2))

    #         print(f"Selected region: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

    #         roi = self.image[y1:y2, x1:x2]
    #         print(f"ROI shape: {roi.shape}")

    #         # 如果尺寸为0，不处理
    #         if roi.size == 0:
    #             print("Empty ROI, skipping processing.")
    #             return

    #         fit_roi_data(roi)
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton and self.start and self.end:
    #         self.drawing = False

    #         # 将 start、end 映射到 scene 坐标
    #         scene_start = self.mapToScene(self.start)
    #         scene_end = self.mapToScene(self.end)

    #         # 将 scene 坐标映射到图像项坐标（再用于映射回图像坐标）
    #         image_start = self.image_item.mapFromScene(scene_start)
    #         image_end = self.image_item.mapFromScene(scene_end)

    #         # 更新 self.rect 为图像项坐标
    #         self.rect = QRectF(image_start, image_end).normalized()

    #         print("Mouse released, processing selected region.")
    #         self.processSelectedRegion()

    def processSelectedRegion(self):
        if self.rect and self.image is not None:
            x1, y1 = self.mapToOriginal(self.rect.topLeft())
            x2, y2 = self.mapToOriginal(self.rect.bottomRight())

            x1 = max(0, min(self.image.shape[1] - 1, x1))
            x2 = max(0, min(self.image.shape[1] - 1, x2))
            y1 = max(0, min(self.image.shape[0] - 1, y1))
            y2 = max(0, min(self.image.shape[0] - 1, y2))

            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            print(f"Selected region: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

            roi = self.image[y1:y2, x1:x2]
            print(f"ROI shape: {roi.shape}")

            if roi.size == 0:
                print("Empty ROI, skipping processing.")
                return
            if roi.shape[0] == 0 or roi.shape[1] == 0:
                print("Empty ROI due to zero width or height, skipping processing.")
                return

            fit_roi_data(roi)


    def paintEvent(self, event):
        super().paintEvent(event)
        if self.start and self.end:
        #if self.start and self.end and self.drawing:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            painter.drawRect(QRect(self.start, self.end))
