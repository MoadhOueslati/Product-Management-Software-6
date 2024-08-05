from buy_style import Ui_Dialog
from PyQt5.QtWidgets import QDialog



class BuyWindow(QDialog, Ui_Dialog):
    def __init__(self, sqlite, mw, category=None, product_name=None):
        super().__init__()
        self.setupUi(self)
        self.sqlite = sqlite
        self.mw = mw
        self.category = category
        self.product_name = product_name
        self.nomProduitLabel.setText(self.product_name)
        self.categorieLabel.setText(self.category)
        self.sqlite_table_name = "Purchases"
        self.sqlite_database_columns = [
            "record_id",
            "nom_du_produit",
            "quantite_achetee",
            "prix_achat",
            "fournisseurs",
            "categorie",
            "date_dentree",
            "notes"
        ]

        self.enregistrerButton.clicked.connect(self.save_changes)
        self.annulerButton.clicked.connect(self.close_window)


        today_date = self.mw.get_today_date()
        self.dateEntreeLineEdit.setText(today_date)
    
    def close_window(self):
        self.close()

    def save_changes(self):
        # Insert data to sqlite
        self.mw.achats_tab.rows_count += 1
        product_data = self.retrieve_purchase_details()

        # Force required buying informations on user
        if int(product_data["quantity_purchased"]) == 0 or float(product_data["purchase_price"]) == 0.0:
            empty_data_error_msg = f"Veuillez remplir toutes les informations requises."
            self.mw._handle_user_error(empty_data_error_msg)
            return
        
        
        self.sqlite.insert_data_sqlite(self.sqlite_table_name, self.sqlite_database_columns, list(product_data.values()))

        # Update sqlite total values
        column1 = "quantite_achetee_totale"
        column2 = "total_depense"
        column3 = "quantite_actuelle"

        select_query = f"SELECT {column1}, {column2}, {column3} FROM {self.mw.sqlite_table_name} WHERE categorie = ? AND nom_du_produit = ?"
        data = self.sqlite.db.fetch_data(select_query, (self.category, self.product_name))

        current_quantity_purchased_in_total = int(data[0])
        current_purchase_spendings_in_total = int(data[1])
        current_available_quantity = int(data[2])

        current_quantity_purchased_in_total += int(product_data['quantity_purchased'])
        current_purchase_spendings_in_total += float( product_data['purchase_price'])
        current_available_quantity += int(product_data['quantity_purchased'])

        update_query = f"UPDATE {self.mw.sqlite_table_name} SET {column1} = ?, {column2} = ?, {column3} = ? WHERE categorie = ? AND nom_du_produit = ?"
        self.sqlite.db.insert_data(update_query, (current_quantity_purchased_in_total, current_purchase_spendings_in_total, current_available_quantity, self.category, self.product_name))

        self.refresh_entry()
        self.mw.update_profits(self.category, self.product_name)
        self.mw.fill_product_data_to_table()
        self.mw.quantiteActuelleLineEdit.setText(str(current_available_quantity))
        self.mw.quantiteAchatTotaleLineEdit.setText(str(current_quantity_purchased_in_total))

        self.close()

    def refresh_entry(self):
        self.nomProduitLabel.setText("")
        self.quantiteAchatSpinBox.setValue(0)
        self.prixAchatDoubleSpinBox.setValue(0)
        self.fournisseurlineEdit.setText("")
        self.categorieLabel.setText("")
        self.plainTextEdit.clear()

        today_date = self.mw.get_today_date()
        self.dateEntreeLineEdit.setText(today_date)
        

    def retrieve_purchase_details(self):
        # Retrieve data from interface
        product_name = self.nomProduitLabel.text()
        quantity_purchased = self.quantiteAchatSpinBox.value()
        purchase_price = self.prixAchatDoubleSpinBox.value()
        supplier = self.fournisseurlineEdit.text()
        category = self.categorieLabel.text()
        entry_date = self.dateEntreeLineEdit.text()
        notes = self.plainTextEdit.toPlainText()

        record_id = self.mw.achats_tab.rows_count 

        print(f"product bought new id : {record_id}")

        product_data = {
            'record_id' : record_id,
            "product_name": product_name,
            "quantity_purchased" : quantity_purchased,
            "purchase_price" : purchase_price,
            "supplier" : supplier,
            "category": category, 
            "entry_date" : entry_date,
            "notes" : notes,
        }
        
        return product_data