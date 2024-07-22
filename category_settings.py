from PyQt5.QtWidgets import QInputDialog, QMessageBox
from PyQt5.QtWidgets import QDialog
from category_settings_style import Ui_Dialog
import copy



class CategorieSettings(QDialog, Ui_Dialog):
    def __init__(self, main_window, sqlite, categories):
        super().__init__()
        self.setupUi(self)
        
        self.init_ui(main_window, sqlite, categories)

    def init_ui(self, main_window, sqlite, categories):
        self.mw = main_window
        self.sqlite = sqlite
        
        self.original_categories = categories
        self.categories = copy.deepcopy(self.original_categories)

        self.sqlite_table_name = "Categories"

        self.to_remove_categories = []

        self.display_categories()

        self.addCategoryButton.clicked.connect(self.add_category)
        self.removeCategoryButton.clicked.connect(self.remove_category)
        
        self.annulerButton.clicked.connect(self.cancel_changes)
        self.enregistrerButton.clicked.connect(self.save_changes)

        self.annulerButton.clicked.connect(self.close_window)


    def close_window(self):
        self.close()

    def display_categories(self):
        self.listWidget.clear()
        for category in self.categories:
            self.listWidget.addItem(category)

    def add_category(self):
        category, ok = QInputDialog.getText(self, "Aoujter categorie", "Categorie")
        category = " ".join(category.split())

        try:
            # this makes sure to remove the category from the bin(self.to_remove_categories) incase user changes his mind by entering it again after removing it at the same time
            if category in self.to_remove_categories:
                self.to_remove_categories.remove(category)

            if ok and self.category_input_verification(category):
                self.listWidget.addItem(category)
                self.categories.append(category)
        except Exception as e:
            self.show_error_message(f"Error adding category: {e}")

    def category_input_verification(self, category):
        condition_1 = 0 < len(category) < 20
        condition_2 = category not in self.categories
        condition_3 = True
        x = 0
        while condition_3 == True and x < len(category):
            condition_3 = 'a' <= category[x] <= 'z' or 'A' <= category[x] <= 'Z' or category[x] == ' '
            x += 1
        return condition_1 and condition_2 and condition_3
    
    def remove_category(self):
        selcted_category = self.listWidget.currentItem()
        try:
            if selcted_category != None:
                if selcted_category.text() in self.original_categories:
                    warning_message = f'Êtes-vous sûr de vouloir supprimer "{selcted_category.text()}" de la liste des catégories ?\nToutes les données associées à "{selcted_category.text()}" seront également supprimées.\n(Cette action n est pas recommandée)'
                    reply = QMessageBox.question(
                    self,
                    "Remove Category",
                    warning_message,
                    QMessageBox.Ok | QMessageBox.Cancel,  
                    QMessageBox.Cancel
                    )
                    if reply == QMessageBox.Ok:
                        self.listWidget.takeItem(self.listWidget.row(selcted_category))
                        # add the category to the trash can
                        self.to_remove_categories.append(selcted_category.text())
                        self.categories.remove(selcted_category.text())
                    else:
                        pass

                # Remove the category if he has just insert it (there is no actual data for it.)
                else:
                    self.listWidget.takeItem(self.listWidget.row(selcted_category))
                    self.categories.remove(selcted_category.text())
        except Exception as e:
            self.show_error_message(f"Error removing category: {e}")

    def save_changes(self):
        # inserting new categories to the database
        for category in self.categories:
            if category not in self.original_categories:
                insert_query = f"INSERT INTO {self.sqlite_table_name} (category) VALUES (?)"
                self.sqlite.db.insert_data(insert_query, (category,))

        # deleting categories from the database
        for category in self.to_remove_categories:
            deletion_query = f"DELETE FROM {self.sqlite_table_name} WHERE category = ?"
            self.sqlite.db.delete_data(deletion_query, (category,))

            # deleting all products with the category removed  sqlite db
            self.mw.delete_by_category(category)
            
        # updating categories related
        self.original_categories = copy.deepcopy(self.categories) # this is responsible for making self.original_categories identical with self.categories in case of adding a new category to database
        self.mw.update_category_combos()
        self.to_remove_categories.clear()
        self.mw.refresh_product_entry()
        self.close()
    
    def cancel_changes(self):
        self.to_remove_categories.clear()
        self.categories = copy.deepcopy(self.original_categories)
        self.display_categories()
        self.close()

    def closeEvent(self, event):
        self.cancel_changes()
        event.accept()

    # For handling errors
    def show_error_message(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()
    