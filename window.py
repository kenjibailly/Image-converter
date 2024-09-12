from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QApplication, QFileDialog, QPushButton, QProgressBar, QSizePolicy
from PyQt6.QtCore import Qt
from convert import convert, acceptable
import time

# Hardcoded from pillow docs
SUPPORTED_INPUTS = {"jpeg", "jpg", "png", "heic", "ppm", "blp", "bmp", "dds", "dib", "eps", "gif", "icns", "ico", "im", "msp", "pcx", "tiff", "sgi", "spider", "tga", "xbm", "webp", "avif"}
SUPPORTED_OUTPUTS = sorted(["JPG", "PNG", "HEIC", "PDF", "TIFF", "PPM", "WEBP"])

class StatusLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("\n\nAccepting Images\n\n")
        self.setMaximumHeight(100)

class ImageLabel(QLabel):
    def __init__(self, status, image_count_label):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("\n\nDrop Image(s) Here\n\n")
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')
        self.status = status  # Store the status label
        self.image_count_label = image_count_label  # Store the image count label
        self.images = []  # List to keep track of dropped images
        
        # Set size policy to allow expansion
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def mousePressEvent(self, event) -> None:
        event.accept()
    
    def mouseReleaseEvent(self, event) -> None:
        event.accept()
        urls = QFileDialog.getOpenFileUrls(self, "Open files")[0]
        urls = [url.toLocalFile() for url in urls]
        if acceptable(urls, SUPPORTED_INPUTS):
            self.images.extend(urls)  # Add new images to the list
            self.image_count_label.setText(f"Images added: {len(self.images)}")  # Update the image count label
            self.status.setText("Images added. Press 'Convert Images' to start processing.")
            self.status.repaint()
            QApplication.processEvents()
        else:
            self.status.setText("File formats not supported")
            self.status.repaint()
            QApplication.processEvents()
            time.sleep(2)
        self.status.setText("\n\nAccepting Images\n\n")

    def get_images(self):
        return self.images
    
    def clear_images(self):
        self.images = []  # Clear the list of images

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Converter")
        self.setGeometry(500, 200, 600, 400)
        self.setAcceptDrops(True)
        self.status = StatusLabel()
        self.image_count_label = QLabel("Images added: 0")  # Label to show the image count
        self.imgLabel = ImageLabel(self.status, self.image_count_label)  # Pass the image count label
        self.dropdown = self.create_comboBox()
        self.convertButton = self.create_convert_button()  # Add convert button
        self.progressBar = self.create_progress_bar()  # Add progress bar
        self.clearButton = self.create_clear_button()  # Add clear button
        self.target = SUPPORTED_OUTPUTS[0]  # Default target
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.dropdown)
        mainLayout.addWidget(self.imgLabel)
        mainLayout.addWidget(self.convertButton)  # Add button to layout
        mainLayout.addWidget(self.progressBar)  # Add progress bar to layout
        mainLayout.addWidget(self.image_count_label)  # Add image count label to layout
        mainLayout.addWidget(self.clearButton)  # Add clear button to layout
        mainLayout.addWidget(self.status)
        self.setLayout(mainLayout)

    def create_convert_button(self):
        button = QPushButton("Convert Images")
        button.clicked.connect(self.convert_images)  # Connect button to conversion function
        return button
    
    def create_clear_button(self):
        button = QPushButton("Clear Images")
        button.clicked.connect(self.clear_images)  # Connect button to clear function
        return button

    def create_progress_bar(self):
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        return progress_bar

    def convert_images(self):
        images = self.imgLabel.get_images()  # Get the images from ImageLabel
        if images:
            if acceptable(images, SUPPORTED_INPUTS):
                self.status.setText("Images added. Processing...")
                self.status.repaint()
                QApplication.processEvents()
                total_images = len(images)
                self.progressBar.setMaximum(total_images)
                for index, url in enumerate(images):
                    convert(url, self.target)  # Use the class attribute 'self.target'
                    self.progressBar.setValue(index + 1)  # Update progress bar
                    QApplication.processEvents()  # Ensure UI updates
                self.status.setText("\n\nAccepting Images\n\n")
                self.progressBar.setValue(total_images)  # Ensure progress bar reaches 100%
            else:
                self.status.setText("File formats not supported")
                self.status.repaint()
                QApplication.processEvents()
                time.sleep(2)
                self.status.setText("\n\nAccepting Images\n\n")
        else:
            self.status.setText("No images to process")
            self.status.repaint()
            QApplication.processEvents()
            time.sleep(2)
            self.status.setText("\n\nAccepting Images\n\n")

    def clear_images(self):
        self.imgLabel.clear_images()  # Clear images from ImageLabel
        self.image_count_label.setText("Images added: 0")  # Update the image count label

    def change_target(self, text):
        self.target = text  # Update the class attribute 'self.target'
    
    def create_comboBox(self):
        combobox = QComboBox()
        combobox.setMaximumWidth(200)
        combobox.addItems(SUPPORTED_OUTPUTS)
        combobox.currentTextChanged.connect(self.change_target)
        return combobox
    
    def dragEnterEvent(self, event):
        event.accept()
        urls = event.mimeData().urls()
        urls = [url.toLocalFile() for url in urls]
        if acceptable(urls, SUPPORTED_INPUTS):
            self.status.setText("Images detected, release to start")
        else:
            self.status.setText("File formats not supported")
    
    def dragLeaveEvent(self, event):
        event.accept()
        self.status.setText("\n\nAccepting Images\n\n")
    
    def dropEvent(self, event):
        event.accept()
        urls = event.mimeData().urls()
        urls = [url.toLocalFile() for url in urls]
        if acceptable(urls, SUPPORTED_INPUTS):
            self.imgLabel.images.extend(urls)  # Add dropped images to the list
            self.image_count_label.setText(f"Images added: {len(self.imgLabel.get_images())}")  # Update the image count label
            self.status.setText("Images added. Press 'Convert Images' to start processing.")
            self.status.repaint()
            QApplication.processEvents()
        else:
            self.status.setText("File formats not supported")
            self.status.repaint()
            QApplication.processEvents()
            time.sleep(2)
        self.status.setText("\n\nAccepting Images\n\n")

if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
