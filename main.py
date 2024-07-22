import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QDialog, QDesktopWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from database import Sqlite
from buy import BuyWindow
from sell import SellWindow
from category_settings import CategorieSettings
import interface_images
from datetime import date, datetime
from PyQt5.uic import loadUi
from main_style import Ui_MainWindow
from freemium_over import Ui_Dialog



class MainWindow(QMainWindow, Ui_MainWindow):   
    def __init__(self):
        super().__init__()
        loadUi("styles/main.ui", self)
        self.setupUi(self)
        self.sqlite = Sqlite()
        self.sqlite_table_name = "Products"
                  
        self.sqlite_database_columns = [
            'nom_du_produit',
            'quantite_actuelle',
            'quantite_achetee_totale',
            'quantite_vendue_totale',
            'categorie',
            'prix_achat',
            'prix_vente',
            'date_dentree',
            'notes',
            'image_path',
            'total_depense',
            'total_gagne',
            'benefices'
        ]

        self.current_product_data = None

        self.acheteeButton.setVisible(False) 
        self.vendueButton.setVisible(False)

        today_date = self.get_today_date()
        self.dateEntreeLineEdit.setText(today_date)

        self.buy_window = BuyWindow(self.sqlite, self)
        self.sell_window = SellWindow(self.sqlite, self)


        self.tableWidget.itemClicked.connect(self.on_table_item_clicked)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.tableWidget.itemSelectionChanged.connect(self.selection_changed)

        self.rechercherCategorieComboBox.currentTextChanged.connect(self.sort_categorie)

        # Fills category combo boxes
        self.update_category_combos()

        self.ajouterCategorieButton.clicked.connect(self.open_categories_window)
        
        # Bottom Buttons
        self.nouveauButton.clicked.connect(self.refresh_product_entry)
        self.enregistrerButton.clicked.connect(self.save)
        self.precedentButton.clicked.connect(self.previous)
        self.suivantButton.clicked.connect(self.next)
        self.modifierButton.clicked.connect(self.modify)
        self.annulerButton.clicked.connect(self.cancel)
        self.supprimerButton.clicked.connect(self.delete)

        self.selection_enabled = False

        # Purchase and Sell buttons
        self.acheteeButton.clicked.connect(self.open_buy_window)
        self.vendueButton.clicked.connect(self.open_sell_window)

        # Left Container Buttons
        self.ajouterImageButton.clicked.connect(self.insert_image)
        
        self.selected_image_path = None
        self.current_row_count = -1
        self.searched_categorie = "----------TOUT----------"

        self.fill_product_data_to_table()
        self.tableWidget.resizeColumnsToContents()


    def open_buy_window(self):
        self.buy_window = BuyWindow(self.sqlite, self, self.current_product_data["category"], self.current_product_data["product_name"])
        if self.selected_image_path is None:
            self.buy_window.imageLabel.setVisible(False)
        else:
            self.buy_window.imageLabel.setPixmap(QPixmap(self.selected_image_path))
        self.buy_window.exec_()

    def open_sell_window(self):
        self.sell_window = SellWindow(self.sqlite, self, self.current_product_data["category"], self.current_product_data["product_name"])
        if self.selected_image_path is None:
            self.sell_window.imageLabel.setVisible(False)
        else:
            self.sell_window.imageLabel.setPixmap(QPixmap(self.selected_image_path))
        self.sell_window.exec_()

    def fetch_all_data_by_column_name(self, table_name, column_name):
        # Retrieve All Categories
        sqlite_table_name = table_name
        column_to_fetch_data_from = column_name
        select_query = f"SELECT {column_to_fetch_data_from} FROM {sqlite_table_name}"
        data = self.sqlite.db.fetch_all_data(select_query)
        data = [category[0] for category in data]
        return data

    def open_categories_window(self):
        categories = self.fetch_all_data_by_column_name("Categories", "category")
        self.categories_window = CategorieSettings(self, self.sqlite, categories) 
        self.categories_window.exec_()


    def _handle_user_error(self, msg):
        QMessageBox.warning(None, "ERROR 303", msg)

    def on_tab_changed(self, index):
        tab_text = self.tabWidget.tabText(index)
        if tab_text == "Produits":
            pass
        elif tab_text == "Achats":
            self.update_achat_table()
        elif tab_text == "Ventes":
            self.update_vente_table()


    def refresh_product_entry(self):
        # Reset the current row and the selection mode 
        self.current_row_count = self.tableWidget.rowCount()
        self.tableWidget.clearSelection()

        # Clear the products Entry
        self.nomProduitLineEdit.setText("")
        self.prixAchatSpinBox.setValue(0)
        self.prixVenteSpinBox.setValue(0)
        self.quantiteAchatTotaleLineEdit.setText("0")
        self.quantiteActuelleLineEdit.setText("0")
        self.quantiteVendueTotaleLineEdit.setText("0")
        self.plainTextEdit.clear()
        self.productPictureLabel.setPixmap(QPixmap())
        self.selected_image_path = None

        today_date = self.get_today_date()
        self.dateEntreeLineEdit.setText(today_date)

                  
        self.acheteeButton.setVisible(False) 
        self.vendueButton.setVisible(False)

    def product_is_unique(self, data_tuple):   
        unique = True
        query = "SELECT categorie, nom_du_produit FROM Products"
        data = self.sqlite.db.fetch_all_data(query)
        data_length = len(data)
        count = 0
        while unique == True and count < data_length:
            unique = data[count] != data_tuple
            count += 1
        return unique

    def retrieve_product_details(self):
        # Retrieve data from interface
        product_name = self.nomProduitLineEdit.text()
        category = self.categorieComboBox.currentText()
        # This case if he has 0 categories
        if category == "": 
            category = "Non catégorisé"
        total_quantity_purchased = int(self.quantiteAchatTotaleLineEdit.text())
        quantity_current = int(self.quantiteActuelleLineEdit.text())
        total_quantity_sold = int(self.quantiteVendueTotaleLineEdit.text())
        selling_price = self.prixVenteSpinBox.value()
        buying_price = self.prixAchatSpinBox.value()
        entry_date = self.dateEntreeLineEdit.text()
        notes = self.plainTextEdit.toPlainText()
        image_path = self.selected_image_path

        product_data = {
            "product_name" : product_name,
            "total_quantity_purchased" : total_quantity_purchased,
            "quantity_current" : quantity_current,
            "total_quantity_sold" : total_quantity_sold,
            "category" : category,
            "buying_price": buying_price,
            "selling_price": selling_price,
            "entry_date" : entry_date,
            "notes" : notes,
            "image_path" : image_path,
            "benefices" : 0
        }

        return product_data

    def update_achat_table(self):
        # clear before inserting 
        self.achatTableWidget.setRowCount(0)
        # Fetch sqlite data and insert to Achat Tab 
        columns_to_fetch_data_from = self.buy_window.sqlite_database_columns
        all_data = self.sqlite.fetch_data_sqlite(self.buy_window.sqlite_table_name, columns_to_fetch_data_from)

        row_count = len(all_data)
        column_count = len(self.buy_window.sqlite_database_columns)

        for row_index in range(row_count):
            self.achatTableWidget.insertRow(row_index)
            for column_index in range(column_count):
                if len(str(all_data[row_index][column_index])) != 0:
                    cell_data = str(all_data[row_index][column_index])
                else:
                    cell_data = "-"

                self.achatTableWidget.setItem(row_index, column_index, QTableWidgetItem(cell_data))

        self.achatTableWidget.resizeColumnsToContents()        


    def update_vente_table(self):
        # clear before inserting 
        self.venteTableWidget.setRowCount(0)
        # Fetch sqlite data and insert to Vente Tab 
        columns_to_fetch_data_from = self.sell_window.sqlite_database_columns
        all_data = self.sqlite.fetch_data_sqlite(self.sell_window.sqlite_table_name, columns_to_fetch_data_from)

        row_count = len(all_data)
        column_count = len(self.sell_window.sqlite_database_columns)

        for row_index in range(row_count):
            self.venteTableWidget.insertRow(row_index)
            for column_index in range(column_count):
                if len(str(all_data[row_index][column_index])) != 0:
                    cell_data = str(all_data[row_index][column_index])
                else:
                    cell_data = "-"

                self.venteTableWidget.setItem(row_index, column_index, QTableWidgetItem(cell_data))

        self.venteTableWidget.resizeColumnsToContents()   

    def modify(self):
        if self.selection_enabled == True:
            warning_message = f'Êtes-vous sûr de vouloir appliquer les modifications ?'
            reply = QMessageBox.question(
            self,
            "Modifier le produit",
            warning_message,
            QMessageBox.Ok | QMessageBox.Cancel,  
            QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                entry_check = self.entry_check("modify")
                if entry_check == False: return
                product_data = self.retrieve_product_details()
                update_query = f"""
                    UPDATE Products 
                    SET categorie=?, nom_du_produit=?, prix_vente=?, prix_achat=?, quantite_actuelle=?, quantite_achetee_totale=?, quantite_vendue_totale=?, notes=?, image_path=?
                    WHERE categorie=? AND nom_du_produit=?
                """
                self.sqlite.db.insert_data(update_query, (product_data["category"], product_data["product_name"], product_data["selling_price"], product_data["buying_price"], product_data["quantity_current"], product_data["total_quantity_purchased"], product_data["total_quantity_sold"], product_data["notes"], product_data["image_path"], self.current_product_data["category"], self.current_product_data["product_name"]))
                self.fill_product_data_to_table()
                self.current_product_data = self.retrieve_product_details()
            else:
                pass
        else:
            select_to_delete_message = "Veuillez sélectionner le produit que vous souhaitez modifier."
            self._handle_user_error(select_to_delete_message)
        
    def entry_check(self, method=None):
        product_data = self.retrieve_product_details()

        if not self.product_is_unique((product_data["category"], product_data["product_name"])):
            if not(method == "modify" and (product_data["product_name"] == self.current_product_data["product_name"] and self.current_product_data["category"] == product_data["category"])):
                unique_error_msg = f"Un produit existe déjà avec le nom ({product_data['product_name']}) dans la catégorie ({product_data['category']}) !"
                self._handle_user_error(unique_error_msg)
                return False

        # Force required product informations on user
        if len(product_data["product_name"]) == 0 or product_data["buying_price"] == 0.0 or product_data["selling_price"] == 0.0:
            empty_data_error_msg = f"Veuillez remplir toutes les informations requises."
            self._handle_user_error(empty_data_error_msg)
            return False
        
    def save(self):
        product_data = self.retrieve_product_details()
        product_data["total_sales"] = 0
        product_data["total_gains"] = 0

        entry_check = self.entry_check()
        if entry_check == False: return

        self.sqlite.insert_data_sqlite(self.sqlite_table_name, self.sqlite_database_columns, list(product_data.values()))

        self.fill_product_data_to_table()

        self.refresh_product_entry()
        self.tableWidget.selectRow(self.current_row_count)

    def sort_categorie(self):
        self.searched_categorie = self.rechercherCategorieComboBox.currentText()
        self.fill_product_data_to_table()

    def fill_product_data_to_table(self):
        # Fetch All data from sqlite db then insert it to product details tab
        columns_to_fetch_data_from = [
            'nom_du_produit',
            'quantite_actuelle',
            'quantite_achetee_totale',
            'quantite_vendue_totale',
            'total_depense',
            'total_gagne',
            'benefices',
            'categorie',
            'date_dentree',
            'notes',
            'benefices'
        ]

        # Fetch data sqlite
        all_data = self.sqlite.fetch_data_sqlite(self.sqlite_table_name, columns_to_fetch_data_from)

        # Insert all data into the table widget
        self.tableWidget.setRowCount(0)
        row_count = len(all_data)
        column_count = len(columns_to_fetch_data_from)

        row_index = 0
        row_index_sorted = 0

        while row_index < row_count:
            if all_data[row_index][7] == self.searched_categorie or self.searched_categorie == "----------TOUT----------":
                self.tableWidget.insertRow(row_index_sorted)
                for i in range(column_count):
                    self.tableWidget.setItem(row_index_sorted, i, QTableWidgetItem(str(all_data[row_index][i])))
                row_index_sorted += 1
            row_index += 1

        self.update_profit_colors()

        self.current_row_count = self.tableWidget.rowCount()
        self.tableWidget.resizeColumnsToContents()
    
    def update_category_combos(self):
        top_text_search_category = "----------TOUT----------"
        top_text_selected_category = "Non catégorisé"
        table_name = "Categories"
        column_name = "category"
        categories = self.fetch_all_data_by_column_name(table_name, column_name)
        search_categories = categories + [top_text_search_category]
        selection_categories = categories + [top_text_selected_category]

        # Select category combo box
        self.categorieComboBox.clear()
        self.categorieComboBox.addItems(selection_categories)

        # Search category combo box
        self.rechercherCategorieComboBox.clear()
        self.rechercherCategorieComboBox.addItems(search_categories)
        self.rechercherCategorieComboBox.setCurrentText(top_text_search_category)


    def previous(self):
        if self.current_row_count > 0 :
            self.current_row_count -= 1
            self.tableWidget.selectRow(self.current_row_count)
            self.acheteeButton.setVisible(True) 
            self.vendueButton.setVisible(True)
            self.fill_product_details(self.current_row_count)

    def next(self):
        if self.current_row_count < self.tableWidget.rowCount()-1:
            self.current_row_count += 1
            self.tableWidget.selectRow(self.current_row_count)
            self.acheteeButton.setVisible(True) 
            self.vendueButton.setVisible(True)
            self.fill_product_details(self.current_row_count)

    def cancel(self):
        if self.selection_enabled:
            self.fill_product_details(self.current_row_count)

    def delete(self):
        if self.selection_enabled == True:
            try:
                product_name = self.tableWidget.item(self.current_row_count, 0).text()
                category = self.tableWidget.item(self.current_row_count, 7).text()
                # Confirm deletion
                reply = QMessageBox.question(self, 'Confirmer la Suppression.', 
                                                f"Êtes-vous sûr de vouloir supprimer le produit '{product_name}' de la catégorie '{category}' ?",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    deleting_query = f"DELETE FROM {self.sqlite_table_name} WHERE nom_du_produit = ? AND categorie = ?"
                    self.sqlite.db.delete_data(deleting_query, (product_name, category))
                    self.tableWidget.removeRow(self.current_row_count)
                    self.tableWidget.clearSelection()
                    self.refresh_product_entry()
                else:
                    pass
            except: 
                pass
        else:
            select_to_delete_message = "Veuillez sélectionner le produit que vous souhaitez supprimer."
            self._handle_user_error(select_to_delete_message)

    def delete_by_category(self, category):
        deleting_query = f"DELETE FROM {self.sqlite_table_name} WHERE categorie = ?"
        self.sqlite.db.delete_data(deleting_query, (category,))
        self.refresh_product_entry()


    def insert_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_name:
            self.productPictureLabel.setPixmap(QPixmap(file_name))
            self.selected_image_path = file_name

    def fill_product_details(self, current_row_count):
        try:
            selected_row_data = []
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(current_row_count, column)
                selected_row_data.append(item.text())
            
            self.nomProduitLineEdit.setText(selected_row_data[0])
            self.quantiteActuelleLineEdit.setText(selected_row_data[1])
            self.quantiteAchatTotaleLineEdit.setText(selected_row_data[2])
            self.quantiteVendueTotaleLineEdit.setText(selected_row_data[3])
            self.categorieComboBox.setCurrentText(selected_row_data[7])
            self.dateEntreeLineEdit.setText(selected_row_data[8])
            self.plainTextEdit.setPlainText(selected_row_data[9])

            # Fetch product buying & selling price then display it 
            query = "SELECT prix_vente, prix_achat FROM Products WHERE categorie=? AND nom_du_produit=?" 
            prix_achat_vente = self.sqlite.db.fetch_all_data(query, (selected_row_data[7], selected_row_data[0]))[0]
            
            prix_vente = prix_achat_vente[0]
            prix_achat = prix_achat_vente[1]

            self.prixVenteSpinBox.setValue(prix_vente)
            self.prixAchatSpinBox.setValue(prix_achat)

            # Fetch picture path from sqlite db
            query = "SELECT image_path FROM Products WHERE categorie = ? AND nom_du_produit = ?"
            self.selected_image_path = self.sqlite.db.fetch_data(query, (selected_row_data[7], selected_row_data[0]))[0]
            
            if self.selected_image_path is None:
                self.productPictureLabel.setPixmap(QPixmap()) 
            else:
                self.productPictureLabel.setPixmap(QPixmap(self.selected_image_path)) 
            
            self.current_product_data = self.retrieve_product_details()
        except:
            pass

    def selection_changed(self):
        selected_items = self.tableWidget.selectedItems()
        if selected_items:
            self.selection_enabled = True
        else:
            self.selection_enabled = False
        
        
    def on_table_item_clicked(self, item):
        self.current_row_count = item.row()
        self.fill_product_details(self.current_row_count)
        self.acheteeButton.setVisible(True) 
        self.vendueButton.setVisible(True)
        
    def closeEvent(self, event): 
        self.sqlite.db.close_connection()
        event.accept()
        
    def update_profits(self, category, product_name):
        select_query = f"SELECT benefices, total_depense, total_gagne FROM {self.sqlite_table_name} WHERE categorie = ? AND nom_du_produit = ?"
        data = self.sqlite.db.fetch_data(select_query, (category, product_name))

        benefices = data[0]
        total_depense = data[1]
        total_gagne = data[2]

        benefices = total_gagne - total_depense

        update_query = f"UPDATE {self.sqlite_table_name} SET benefices = ? WHERE categorie = ? AND nom_du_produit = ?"
        self.sqlite.db.insert_data(update_query, (benefices, category, product_name))

        self.update_profit_colors()


    def update_profit_colors(self):
        category_column_index = 6
        category_target = "Bénéfices (dt)"
        for column_index in range(self.tableWidget.columnCount()):
            if self.tableWidget.horizontalHeaderItem(column_index).text() == category_target: 
                for row_index in range(self.tableWidget.rowCount()):
                    profit = self.tableWidget.item(row_index, category_column_index)
                    # Checking if the profit is good or nah
                    if int(profit.text()) > 0:
                        profit.setBackground(QColor(134, 255, 120))
                    elif int(profit.text()) < 0:
                        profit.setBackground(QColor(255, 82, 85))
                    elif int(profit.text()) == 0:
                        profit.setBackground(QColor(190, 190, 190))
            else:
                for row_index in range(self.tableWidget.rowCount()):
                    item = self.tableWidget.item(row_index, column_index)
                    try:
                        item.setBackground(QColor(190, 190, 190))
                    except:
                        pass
    
    def get_today_date(self):
        today = datetime.today()
        formatted_date = today.strftime("%d/%m/%Y")
        return formatted_date


class Freemium:
    def __init__(self, mainwindow):
        self.sqlite = Sqlite()
        self.mw = mainwindow
        self.start_date_table_name = "emit"
        self.today_date = None
        self.start_date = None
        self.end_date = None
        self.freemium_is_over = False
        self.warning_not_mentioned = True
        self.today_date = date.today()
        self.store_start_date(self.start_date_table_name)
        self.timer = QTimer()
        self.check_if_freemium_is_over()
        self.timer.timeout.connect(self.check_if_freemium_is_over)
        self.timer.start(1000000)

    def check_if_freemium_is_over(self):
        self.freemium_is_over = self.check_freemium_plan(self.start_date, self.today_date)
        if self.freemium_is_over and self.warning_not_mentioned:
            self.mw.setEnabled(False)
            freeOverWindow = FreeOver()
            freeOverWindow.show()
            freeOverWindow.exec_()
            self.warning_not_mentioned = False
        else: 
            pass
    
    def store_start_date(self, table_name):
        query = f"SELECT {table_name} FROM Emit"
        self.start_date = self.sqlite.db.fetch_data(query)[0]
        if self.start_date is None:
            self.start_date = self.today_date
            query = f"""UPDATE Emit
                        SET {table_name} = ?
                        """
            self.start_date = self.encrypt(str(self.start_date))
            self.sqlite.db.insert_data(query, (self.start_date,))
        else: 
            pass
        self.start_date = self.decrypt(str(self.start_date))

    
    def check_freemium_plan(self, start_date, today_date):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        date_difference = today_date - start_date
        days_between = date_difference.days

        query = "SELECT syad FROM Emit"
        freemium_period = self.sqlite.db.fetch_data(query)[0]
        freemium_period = freemium_period // (28 * 12 * 2002)

        return days_between > freemium_period
    
    def encrypt(self, text):
        encrypted_text = ""
        for letter in text:
            encrypted_text += chr(ord(letter) + 19)
        return encrypted_text

    def decrypt(self, text):
        dycrypted_text = ""
        for letter in text:
            dycrypted_text += chr(ord(letter) - 19)
        return dycrypted_text


class FreeOver(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        # loadUi("styles/freemium_over.ui", self)
        self.setupUi(self)

        
        

if __name__ == "__main__":
    print("here i come from mac os lol")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setWindowIcon(QIcon('diamond.png'))
    window.resize(1100, 880)
    # Centering the window on the screen
    screen = QDesktopWidget().screenGeometry()
    x = (screen.width() - window.width()) // 2
    y = 0
    window.move(x, y)
    freemium = Freemium(window)
    sys.exit(app.exec_())
