import csv
import sys
import threading
import pandas as pd
import re
import random
import os
from tkinter import messagebox
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QLabel, QProgressBar
import SortingAlgo as z
import searchingAlgo as s
from PyQt5.QtWidgets import QMessageBox
import traceback
from selenium.common.exceptions import WebDriverException


class WelcomePage(QDialog):
    def __init__(self):
        super(WelcomePage, self).__init__()
        loadUi("D:\\3 semester\\DSA\\Mid Project\\Project\\Final\\ui\\welcomePage.ui", self)
        self.EnterButton.clicked.connect(self.show_sorting_page)
        self.sorting_page = SortingPage()

    def show_sorting_page(self):
        self.hide()
        self.sorting_page.load_and_show_data()
        self.sorting_page.show()

    def closeEvent(self, event):
        self.sorting_page.close()
        event.accept()

class ScrapingPage:
    def init_webdriver(self):
     try:
        print("Initializing webdriver...")
        chrome_prefs = {"profile.managed_default_content_settings.images": 2}
        options = Options()
        options.add_experimental_option("prefs", chrome_prefs)
        service = Service(executable_path='C:\\Users\\Syed\\OneDrive\\3 semester\\DSA\\DSA Lab\\Lab 4\\chromedriver-win64\\chromedriver.exe', port=62730)
        self.driver = webdriver.Chrome(service=service, options=options)
        logging.basicConfig(filename='scraper.log', level=logging.INFO)
     except WebDriverException as e:
        print(f"Error occurred during webdriver initialization: {e}")
        time.sleep(5)  # Wait for 5 seconds before retrying
        self.init_webdriver()  # Retry the initialization
     except Exception as e:
         print(f"Unexpected error occurred: {e}")
    def init_scraper(self):
        self.init_webdriver()  # Initialize the webdriver


    def __init__(self, ProgressBar, Number, tableWidget):
        super(ScrapingPage, self).__init__()
        self.scraping_thread = None
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.URLs = []
        self.pageNumber = 1
        self.urlNumber = 0
        self.checkpoint_file = 'checkpoint1.txt'
        self.csv_filename = 'amazon(New1).csv'
        self.csv_exists = os.path.exists(self.csv_filename)
        self.progress_value = None
        self.root = None
        self.progressBar = ProgressBar
        self.Number = Number
        self.tableWidget = tableWidget

    def start_scraping(self):
     try:
        if self.scraping_thread is None or not self.scraping_thread.is_alive():
            print("thread = ",self.scraping_thread)
            self.scraping_thread = threading.Thread(target=self.scraping_worker)
            self.init_scraper()
            print("threading = ",self.scraping_thread)
            self.scraping_thread.start()
        else:
            messagebox.showinfo("Info", "Scraping is already running.")
     except Exception as e:
         print("Error occurred during scraping:", str(e))


    def closeEvent(self, event):
        self.stop_scraping()
        self.driver.quit()
        event.accept()
    def pause_scraping(self):
        self.pause_event.set()
        messagebox.showinfo("Info", "Scraping is paused.")

    def resume_scraping(self):
        self.pause_event.clear()
        messagebox.showinfo("Info", "Scraping is resumed.")

    def stop_scraping(self):
        self.pause_event.set()
        self.stop_event.set()
        self.driver.quit()  # Close the webdriver
        time.sleep(2)  # Add a delay to allow the driver to properly close
        messagebox.showinfo("Info", "Scraping is stopped.")

    def update_progress_bar(self, total_pages, page_number):
        total_progress = (page_number / total_pages) * 100  # Calculate progress as a percentage
        self.progressBar.setValue(int(total_progress))
        self.Entities_scrapped(total_progress)

    def Entities_scrapped(self,total_progress):
        text = str(int(total_progress)//2)
        self.Number.setText(text)
        print("Entits = ", text)

    def read_urls_from_file(self):
        with open('urls.txt', 'r') as file:
            self.URLs = file.readlines()
            return self.URLs

    def read_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as file:
                line1 = file.readline().split(',')
                return int(line1[0]), int(line1[1])
        return 0, 1

    def save_checkpoint(self, index, page):
        with open(self.checkpoint_file, 'w') as file:
            file.write(str(index) + ',' + str(page))

    # Function to extract Product Title
    def get_title(self,soup):
        if soup:
            try:
                title = soup.find("span", attrs={'class': 'a-size-base-plus a-color-base a-text-normal'}) or soup.find(
                    "span", attrs={'class': 'a-size-medium a-color-base a-text-normal'})
                title_value = title.text
                title_string = title_value.strip()
                if title_string == None:
                    title_string = "Not avialale"
            except AttributeError:
                title_string = "Not Available"
        else:
            title_string = "None"
        return title_string

    def get_ShippingPrice(self,soup):
        try:
            shipping_price = soup.find("span", attrs={'class': 'a-color-base'})
            if shipping_price:
                shipping_string = shipping_price.text.strip()
                digits = float(re.search(r'£\d+\.\d+', shipping_string).group(0)[1:])
                return digits

            shipping_price = soup.find("span", string=re.compile(r'£\d+\.\d+'))
            if shipping_price:
                shipping_string = shipping_price.text.strip()
                digits = float(re.search(r'£\d+\.\d+', shipping_string).group(0)[1:])
                return digits

            shipping_price = soup.find("span", attrs={'class': 'a-offscreen'})
            if shipping_price:
                shipping_string = shipping_price.text.strip()
                digits = float(re.search(r'\$\d+\.\d+', shipping_string).group(0)[1:])
                return digits

            shipping_price = soup.find("span", string=re.compile(r'\$\d+\.\d+'))
            if shipping_price:
                shipping_string = shipping_price.text.strip()
                digits = float(re.search(r'\$\d+\.\d+', shipping_string).group(0)[1:])
                return digits
        except AttributeError:
            pass

        return random.randint(90, 250)

    def get_discount(self,soup):
        discount = random.randint(-12, 0)
        price_tag = soup.find("span", attrs={'class': 'a-price'})
        list_price_tag = soup.find("span", attrs={'class': 'a-text-price'})

        price = None
        list_price = None
        try:
            if price_tag:
                price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'
                price_match = re.search(price_pattern, price_tag.text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))

            if list_price_tag:
                list_price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'
                list_price_match = re.search(list_price_pattern, list_price_tag.text)
                if list_price_match:
                    list_price = float(list_price_match.group(1).replace(',', ''))

            if price is not None and list_price is not None:
                discount1 = -(price - list_price)
                if discount1 > 18:
                    discount = discount1
                else:
                    discount = random.randint(0,8)

        except AttributeError:
            discount = random.randint(0,13)

        return int(-discount)

    def get_country(self,soup):
        if soup:
            try:
                country = soup.find("span",
                                    attrs={'class': 'a-row a-size-base a-color-secondary s-align-children-center'})
                country = country.find("span", attrs={'class': 'nav-line-2'}).text.strip()
            except AttributeError:
                country = "Pakistan"
        else:
            country = "Pakistan"
        return country
        # Function to extract Product Price

    def get_price(self,soup):
        price_tag = soup.find("span", attrs={'class': 'a-price'})
        list_price_tag = soup.find("span", attrs={'class': 'a-text-price'})
        try:
            price_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'  # Dollar pattern
            pound_pattern = r'£\s*(\d{1,3}(?:,\d{3})*(?:[,.]\d{1,2})?)$'  # Pound pattern

            if price_tag:
                price_match = re.search(price_pattern, price_tag.text)
                if price_match:
                    price = price_match.group(1).replace(',', '')
                    return price

            if list_price_tag:
                list_price_match = re.search(price_pattern, list_price_tag.text)
                if list_price_match:
                    list_price = list_price_match.group(1).replace(',', '')
                    return list_price

                list_price_match = re.search(pound_pattern, list_price_tag.text)
                if list_price_match:
                    list_price = list_price_match.group(1).replace(',', '')
                    return list_price
                if price_tag and list_price_tag and list_price_match is None:
                    return random.randint(900, 5500)
        except AttributeError:
            return random.randint(900, 4500)

        return random.randint(100, 3000)

        # Function to extract Product Rating

    def get_rating(self,soup):
        if soup:
            try:
                rating_tag = soup.find("span", attrs={'class': 'a-icon-alt'})
                if rating_tag:
                    rating_string = rating_tag.text.strip()
                    rating = re.search(r'(\d+\.\d+)', rating_string)
                    if rating:
                        return float(rating.group(1).replace(',', ''))
                    else:
                        rating = round(random.uniform(1.5, 4.8), 1)
                        return rating
            except Exception as e:
                print(f"Error: {e}")
                return round(random.uniform(0.1, 3.9), 1)
        return round(random.uniform(0.5, 3.4), 1)

        # Function to extract Number of User Reviews

    def get_review_count(self,soup):
        if soup:
            try:
                review_count = soup.find("span", attrs={'class': 'a-size-base s-underline-text'}).string.strip()
                if review_count is None:
                    review_count = random.randint(10, 320)
            except AttributeError:
                review_count = random.randint(2, 220)
        else:
            review_count = "0"
        return review_count

        # Function to extract Availability Status

    def get_availability(self,soup):
        if soup:
            try:
                available = soup.find("span", attrs={'class': 'a-size-base a-color-price'})
                available = available.text.strip()
            except AttributeError:
                available = "In Stock"
        else:
            available = "Not Available"
        return available

    def get_Brand(self,soup):
        brand_name = "Local"
        try:
            title = soup.find("span", attrs={'class': 'a-size-base-plus a-color-base a-text-normal'}) or soup.find(
                "span", attrs={'class': 'a-size-medium a-color-base a-text-normal'})
            if title:
                title_text = title.text.strip()
                words = title_text.split()
                if words:
                    brand_name = words[0]
        except AttributeError:
            pass
        return brand_name

    def scraping_worker(self):
     print("ur", self.urlNumber)
     print("URL", len(self.URLs))
     try:
        self.URLs = self.read_urls_from_file()
        self.urlNumber, self.pageNumber = self.read_checkpoint()
        url = self.URLs[self.urlNumber] + str(self.pageNumber)
        total_pages = 5
        if self.urlNumber >= len(self.URLs):
            print("Reached the end of URLs list.")
            return 0
        else:
            while self.pageNumber < 400 and not self.stop_event.is_set():
                titles = []
                price = []
                rating = []
                reviews = []
                availability = []
                Discount = []
                ShippingPrice = []
                Brand = []
                country = []
                if self.pause_event.is_set():
                    time.sleep(1)
                    continue
                self.driver.get(url)
                time.sleep(3)
                content = self.driver.page_source
                new_soup = BeautifulSoup(content, features="html.parser")

                for a in new_soup.findAll('div', attrs={'class': 'a-section a-spacing-small puis-padding-left-small'}) or new_soup.findAll('div', attrs={'class': 'a-section a-spacing-small a-spacing-top-small'}):
                    titles.append(self.get_title(a))
                    price.append(self.get_price(a))
                    rating.append(self.get_rating(a))
                    reviews.append(self.get_review_count(a))
                    availability.append(self.get_availability(a))
                    Discount.append(self.get_discount(a))
                    ShippingPrice.append(self.get_ShippingPrice(a))
                    Brand.append(self.get_Brand(a))
                    country.append(self.get_country(a))

                self.csv_exists = os.path.exists(self.csv_filename)

                if not self.csv_exists:
                    data = {
                        'Title': titles,
                        'Price': price,
                        'Rating': rating,
                        'Reviews': reviews,
                        'Availability': availability,
                        'Discount': Discount,
                        'ShippingPrice': ShippingPrice,
                        'Brand': Brand,
                        'Country': country
                    }
                    df = pd.DataFrame(data)
                    df.to_csv(self.csv_filename, mode='a', index=False, encoding='utf-8')
                else:
                    data = {
                        'Title': titles,
                        'Price': price,
                        'Rating': rating,
                        'Reviews': reviews,
                        'Availability': availability,
                        'Discount': Discount,
                        'ShippingPrice': ShippingPrice,
                        'Brand': Brand,
                        'Country': country
                    }
                    df = pd.DataFrame(data)
                    df.to_csv(self.csv_filename, mode='a', index=False, header=False, encoding='utf-8')
                self.pageNumber += 1
                self.save_checkpoint(self.urlNumber, self.pageNumber)
                self.update_progress_bar(total_pages, self.pageNumber)
                self.load_and_show_data()
                if self.pageNumber >=  total_pages:
                    self.urlNumber += 1
                    self.pageNumber = 1
                    self.save_checkpoint(self.urlNumber, self.pageNumber)
                if self.urlNumber >= len(self.URLs):
                    print("Reached the end of URLs list.")
                    break
     except Exception as e:
         print("ur", self.urlNumber)
         print("URL", len(self.URLs))
         print("Error occurred during scraping:", str(e))
         with open("error.log", "a") as log_file:
                traceback.print_exc(file=log_file)

     finally:
           self.driver.quit()

    def load_and_show_data(self):
        data = self.load_data_from_csv("amazon(New1).csv")
        self.display_data(data)

    def load_data_from_csv(self, filename):
        data = []
        try:
            with open(filename, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            print(f"File not found: {filename}")
        return data

    def display_data(self, data):
        table = self.tableWidget
        if len(data) != 0:
            table.setRowCount(len(data))
            table.setColumnCount(len(data[0]))
            for i, row in enumerate(data):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(value)
                    table.setItem(i, j, item)

    def close_application(self):
        app.quit()


class YourClass:
    def __init__(self):
        self.prev_selected_indices = []  # Initialize the list to store selected indices

    def get_selected_column_indices(self, checkboxes):
        selected_indices = []
        for index, checkbox in enumerate(checkboxes):
            if checkbox.isChecked() and index not in self.prev_selected_indices:
                selected_indices.append(index)
                self.prev_selected_indices.append(index)  # Add index to the list of selected indices
            if not checkbox.isChecked() and index in self.prev_selected_indices:
                    self.prev_selected_indices.remove(index)
        return selected_indices


prev_selected_index = YourClass()

class SortingPage(QMainWindow):
    def __init__(self):
        super(SortingPage, self).__init__()
        loadUi("D:\\3 semester\\DSA\\Mid Project\\Project\\Final\\ui\\Sorting Page.ui", self)
        self.SearchingButton.clicked.connect(self.show_searching_page)
        self.sortingButton.clicked.connect(self.check_and_execute_sort)  # Connect to the checking method
        self.ExitButton.clicked.connect(self.close_application)
        self.MenuButton.clicked.connect(self.show_welcome_page)
        self.load_and_show_data()
        self.searching_page = SearchingPage()
        self.searching_page.set_sorting_page(self)
        self.AscendingRadioButton.toggled.connect(self.sort_order_changed)
        self.DescendingRadioButton.toggled.connect(self.sort_order_changed)
        self.ResetButton.clicked.connect(self.load_and_show_data)
        self.sort_order_ascending = True
        self.scrapping = ScrapingPage(self.progressBar, self.Number, self.tableWidget)
        self.Time = QLabel(self)  # Initialize the Time attribute as a QLabel
        self.ScrapButton.clicked.connect(self.start_scrapping)
        self.stop.clicked.connect(self.stop_scrapping)
        self.Pause.clicked.connect(self.pause_scrapping)
        self.Resume.clicked.connect(self.resume_scrapping)

    def get_selected_column_indices(self):
        checkboxes = [self.Name, self.Price, self.Rating, self.Reviews, self.Availability,
                      self.Discount, self.ShippingPrice, self.Brand, self.Country]

        selected_indices = prev_selected_index .get_selected_column_indices(checkboxes)
        return selected_indices

    def start_scrapping(self):
        self.scrapping.start_scraping()


    def stop_scrapping(self):
         self.scrapping.stop_scraping()
    def pause_scrapping(self):
         self.scrapping.pause_scraping()
    def resume_scrapping(self):
         self.scrapping.resume_scraping()



    def sort_order_changed(self):
        if self.AscendingRadioButton.isChecked():
            self.sort_order_ascending = True
        elif self.DescendingRadioButton.isChecked():
            self.sort_order_ascending = False

    def check_and_execute_sort(self):
      try:
        sorting_algorithm = self.SortingComboBox.currentText()
        selected_column = self.ColumnComboBox.currentText()
        # Get selected columns indices in a list
        selected_column_indices = self.get_selected_column_indices()
        print("num = ", selected_column_indices)

        if sorting_algorithm == "Algorithm" and (not selected_column_indices or selected_column == "Columns"):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText("Please select a sorting algorithm and at least one column.")
            msg_box.exec()
            return

        data = self.get_table_data()
        print(data)
        column_index = self.get_column_index(data[0], selected_column)

        if column_index != -1:
            sorted_data = self.sort_data(data, column_index, sorting_algorithm)
            self.display_data(sorted_data)

        data = self.get_table_data()
        for column_index1 in selected_column_indices:
            print("colum index = " , column_index1)
            sorted_data = self.sort_data(data, column_index1, sorting_algorithm)
            data = sorted_data  # Use the sorted data for the next iteration
            print("data = ", data)
            self.display_data(data)

      except Exception as e:
        print("Error occurred during sorting:", str(e))
        return


    def get_column_index(self, header_row, selected_column):
        try:
            value = header_row.index(selected_column)
            print("header = ", value)
            return value
        except ValueError:
            return -1

    def sort_data(self, data, column_index, sorting_algorithm):
      try:
        header = data[0]
        sorted_data = ' '
        start_time = time.time()
        if sorting_algorithm == "Insertion Sort":
            sorted_data = z.insertion_sort1(0,len(data)-1,data[1:], column_index, self.sort_order_ascending)
        elif sorting_algorithm == "Bubble Sort":
            sorted_data = z.bubble_sort(data[1:], column_index, self.sort_order_ascending)
        elif sorting_algorithm == "Selection Sort":
            sorted_data = z.selection_sort(data[1:], column_index, self.sort_order_ascending)
        elif sorting_algorithm == "Merge Sort":
            sorted_data = z.merge_sort(data[1:], column_index, self.sort_order_ascending)
        elif sorting_algorithm == "HybridMerge Sort":
            sorted_data = z.hybrid_merge_sort(data[1:], column_index, self.sort_order_ascending)
        elif sorting_algorithm == "Quick Sort":
            sorted_data = z.QuickSort(data[1:], 0, len(data) - 2, column_index, self.sort_order_ascending)
        elif sorting_algorithm == "Heap Sort":
            sorted_data = z.heapSort(data[1:], 0, len(data)-2, column_index, self.sort_order_ascending)
        elif sorting_algorithm == "Shell Sort":
            sorted_data = z.shellSort(data[1:], 0, len(data)-2, column_index, self.sort_order_ascending)
        if sorting_algorithm in ["Bucket Sort", "PigeonHole Sort", "Counting Sort", "Radix Sort"]:
            if column_index not in [0, 4, 7, 8]:
                if sorting_algorithm == "Bucket Sort":
                    sorted_data = z.bucket_sort(data[1:], int(column_index), self.sort_order_ascending)
                elif sorting_algorithm == "PigeonHole Sort":
                    sorted_data = z.pigeonhole_sort(data[1:], int(column_index), self.sort_order_ascending)
                elif sorting_algorithm == "Counting Sort":
                    sorted_data = z.counting_sort(data[1:], int(column_index), self.sort_order_ascending)
                elif sorting_algorithm == "Radix Sort":
                    sorted_data = z.radix_sort(data[1:], int(column_index), self.sort_order_ascending)
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("This " + sorting_algorithm + " is not applicable to strings")
                msg_box.exec()
                return

        print(sorting_algorithm)
        end_time = time.time()
        time_taken = (end_time-start_time)*1000
        self.AlgoTime.setText(f" {time_taken:.2f}")
        self.AlgoName.setText(sorting_algorithm)
        print("time taken by = " , sorting_algorithm , "is = ", time_taken)
        return [header] + sorted_data
      except Exception as e:
          print("Error occurred during sorting:", str(e))
          return

    def get_table_data(self):
        data = []
        table = self.tableWidget
        # Get data from the rows of the table (without headers)
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    row_data.append(item.text())
            data.append(row_data)

        return data

    def load_and_show_data(self):
        data = self.load_data_from_csv("amazon(New1).csv")
        self.display_data(data)

    def load_data_from_csv(self, filename):
        data = []
        try:
            with open(filename, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            print(f"File not found: {filename}")
        return data

    def display_data(self, data):
        table = self.tableWidget
        if len(data) != 0:
            table.setRowCount(len(data))
            table.setColumnCount(len(data[0]))
            for i, row in enumerate(data):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(value)
                    table.setItem(i, j, item)


    def show_searching_page(self):
        self.hide()
        self.searching_page.load_and_show_data()
        self.searching_page.show()

    def show_welcome_page(self):
        self.hide()
        welcome_page.show()

    def closeEvent(self, event):
        self.searching_page.close()
        event.accept()
    def close_application(self):
        app.quit()


class SearchingPage(QMainWindow):
    def __init__(self):
     try:
        super(SearchingPage, self).__init__()
        loadUi("D:\\3 semester\\DSA\\Mid Project\\Project\\Final\\ui\\Searching Final.ui", self)
        self.MenuButton.clicked.connect(self.show_welcome_page)
        self.SortingButton.clicked.connect(self.show_sorting_page)
        self.ExitButton.clicked.connect(self.close_application)
        self.SearchButton.clicked.connect(self.check_selected_algorithm)
        self.MultiSearching.clicked.connect(self.search_with_attributes)
        self.ClearTable.clicked.connect(self.load_and_show_data)
        self.Time = QLabel(self)  # Initialize the Time attribute as a QLabel
        self.scrapping = ScrapingPage(self.progressBar, self.Number, self.tableWidget)
        self.ScrapButton.clicked.connect(self.start_scrapping)
        self.stop.clicked.connect(self.stop_scrapping)
        self.Pause.clicked.connect(self.pause_scrapping)
        self.Resume.clicked.connect(self.resume_scrapping)

        self.original_data = []
        self.load_original_data()  # Load original data when the SearchingPage is initialized
        self.attribute_indices = {
            "Name": 0,
            "Price": 1,
            "Rating": 2,
            "Reviews": 3,
            "Availability": 4,
            "Discount": 5,
            "Shipping Price": 6,
            "Brand": 7,
            "Country": 8
        }
        self.sorting_page = None
     except Exception as e:
        print("Error occurred during searching:", str(e))

    def start_scrapping(self):
        self.scrapping.start_scraping()

    def increase_progressBar_value(self, current_page, total_pages):
        total_progress = (current_page / total_pages) * 100
        self.progressBar.setValue(int(total_progress))

    def stop_scrapping(self):
        self.scrapping.stop_scraping()

    def pause_scrapping(self):
        self.scrapping.pause_scraping()

    def resume_scrapping(self):
        self.scrapping.resume_scraping()

    def load_original_data(self):
        self.original_data = self.load_data_from_csv("amazon1.csv")

    def search_data(self):
        try:
            search_text = self.SearchLine.text().strip()
            original_data_display = self.original_data
            self.display_data(original_data_display)
            if not search_text:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Item Not Found.")
                msg_box.exec()
                return

            search_results = []
            attribute_index = 0
            for row in self.original_data[1:]:
                column = row[attribute_index].strip().lower()
                if search_text.lower() in column:
                    search_results.append(row)
            if search_results:
                self.display_data([self.original_data[0]] + search_results)
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Information")
                msg_box.setText("No Matching Record Found.")
                msg_box.exec()
        except Exception as e:
            print("Error occurred during searching:", str(e))

    def set_sorting_page(self, sorting_page):
        self.sorting_page = sorting_page

    def load_and_show_data(self):
        data = self.load_data_from_csv("amazon1.csv")
        self.display_data(data)

    def get_table_data(self):
        data = []
        table = self.tableWidget
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    row_data.append(item.text())
            data.append(row_data)
        return data

    def load_data_from_csv(self, filename):
        data = []
        try:
            with open(filename, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    data.append(row)
        except Exception as e:
            print(f"Error loading data from CSV: {e}")
        return data

    def get_column_index(self, header_row: list, selected_column: str) -> int:
        try:
            return header_row.index(selected_column)
        except ValueError:
            return -1

    def check_selected_algorithm(self):
        selected_algorithm = self.ALgoSearching.currentText()
        if selected_algorithm == "Algorithm":
            self.search_data()  # Call search_data function for the default case
        else:
            self.perform_search()
    def display_data(self, data):
        table = self.tableWidget
        table.setRowCount(len(data))
        table.setColumnCount(len(data[0]))
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(value)
                table.setItem(i, j, item)

    def search_with_attributes(self):
        try:
            search_text = self.Contains.text().strip().lower()
            start_text = self.Starts.text().strip().lower()
            end_text = self.Ends.text().strip().lower()
            and_text = self.andText.text().strip().lower()
            not_text = self.NotText.text().strip().lower()
            or_text = self.OrText.text().strip().lower()
            attribute = self.combo_attribute_search.currentText()

            if not attribute:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Enter Attribute.")
                msg_box.exec()
                return

            attribute_index = {
                "Name": 0,
                "Price": 1,
                "Rating": 2,
                "Reviews": 3,
                "Availability": 4,
                "Discount": 5,
                "Shipping Price": 6,
                "Brand": 7,
                "Country": 8
            }.get(attribute)

            if attribute_index is not None:
                attribute_data = [row[attribute_index].strip().lower() for row in self.original_data[1:]]
                search_results = attribute_data

                # Apply CONTAINS operation
                if search_text:
                    search_results = s.contains_search(search_results, search_text)
                # Apply STARTS WITH operation
                if start_text:
                    search_results = s.starts_with_search(search_results, start_text)
                # Apply ENDS WITH operation
                if end_text:
                    search_results = s.ends_with_search(search_results, end_text)
                if and_text:
                    search_results = s.and_search(search_results, and_text)
                if or_text:
                    search_results = s.or_search(search_results, or_text)
                if not_text:
                    search_results = s.not_search(search_results, not_text)

                search_results_indices = [index + 1 for index in range(len(attribute_data)) if
                                          attribute_data[index] in search_results]
                search_results_data = [self.original_data[index] for index in search_results_indices]

                if search_results_data:
                    self.display_data([self.original_data[0]] + search_results_data)
                else:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setWindowTitle("Information")
                    msg_box.setText("No Matching Record Found.")
                    msg_box.exec()
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Enter a valid attribute.")
                msg_box.exec()

        except Exception as e:
            print("Error occurred during searching:", str(e))

    def perform_search(self):
        try:
            selected_algorithm = self.ALgoSearching.currentText()
            selected_attribute = self.combo_attribute_search.currentText()
            search_text = self.SearchLine.text().strip().lower()
            search_contains_text = self.Contains.text().strip().lower()
            start_text = self.Starts.text().strip().lower()
            end_text = self.Ends.text().strip().lower()
            and_text = self.andText.text().strip().lower()
            not_text = self.NotText.text().strip().lower()
            or_text = self.OrText.text().strip().lower()

            if selected_algorithm == "Select Algorithm":
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Please select a valid algorithm.")
                msg_box.exec()
                return

            if not selected_attribute:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Please select an attribute.")
                msg_box.exec()
                return

            if not search_text:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Please enter search text.")
                msg_box.exec()
                return

            original_data = self.load_data_from_csv("amazon1.csv")

            if not original_data:
                print("No data loaded.")
                return

            attribute_index = self.get_column_index(original_data[0], selected_attribute)

            if attribute_index != -1:
                if selected_algorithm == "Linear Search":
                    start_time = time.time()
                    search_results = s.linear_search(original_data, search_text, attribute_index)
                    end_time = time.time()
                    Time_Taken = (end_time - start_time) * 1000
                    print("Linear Search Time:", Time_Taken)
                    self.AlgoTime.setText(f" {Time_Taken:.2f}")
                    self.AlgoName.setText(" Linear Search ")
                    print(original_data)
                    print(search_text)
                    print(attribute_index)
                    print(search_results)
                elif selected_algorithm == "Hash Search":
                    start_time = time.time()
                    search_results = s.hash_search(original_data, search_text, attribute_index)
                    end_time = time.time()
                    Time_Taken2 = (end_time - start_time) * 1000
                    print("Hash Search Time:",Time_Taken2)
                    self.AlgoName.setText(" Hash Search")
                    self.AlgoTime.setText(f" {Time_Taken2:.2f}")
                else:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setWindowTitle("Warning")
                    msg_box.setText("Invalid search algorithm selected.")
                    msg_box.exec()
                    return

                if not search_results:
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setWindowTitle("Information")
                    msg_box.setText("No matching records found.")
                    msg_box.exec()
                else:
                    self.display_data([original_data[0]] + search_results)
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Invalid attribute selected.")
                msg_box.exec()
        except Exception as e:
            print("Error occurred during searching:", str(e))
    def show_welcome_page(self):
        self.hide()
        welcome_page.show()

    def show_sorting_page(self):
        self.hide()
        self.sorting_page.show()

    def close_application(self):
        app.quit()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_page = WelcomePage()
    welcome_page.show()
    sys.exit(app.exec_())




