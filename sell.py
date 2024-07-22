from sell_style import Ui_Dialog
from PyQt5.QtWidgets import QDialog



class SellWindow(QDialog, Ui_Dialog):
    def __init__(self, sqlite, mw, category=None, product_name=None):
        super().__init__()
        self.setupUi(self)
        self.sqlite = sqlite
        self.mw = mw
        self.category = category
        self.product_name = product_name
        self.nomProduitLabel.setText(self.product_name)
        self.categorieLabel.setText(self.category)
        self.sqlite_table_name = "Sales"
        self.sqlite_database_columns = [
            "nom_du_produit",
            "quantite_vendue",
            "prix_vente",
            "nom_client",
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
        product_data = self.retrieve_purchase_details()

            # Force required selling informations on user
        if int(product_data["quantity_sold"]) == 0 or float(product_data["sale_price"]) == 0.0:
            empty_data_error_msg = f"Veuillez remplir toutes les informations requises."
            self.mw._handle_user_error(empty_data_error_msg)
            return
        
        # Update sqlite total values
        column1 = "quantite_vendue_totale"
        column2 = "total_gagne"
        column3 = "quantite_actuelle"

        select_query = f"SELECT {column1}, {column2}, {column3} FROM {self.mw.sqlite_table_name} WHERE categorie = ? AND nom_du_produit = ?"
        data = self.sqlite.db.fetch_data(select_query, (self.category, self.product_name))

        current_quantity_sold_in_total = int(data[0])
        current_sales_spendings_in_total = int(data[1])
        current_available_quantity = int(data[2])

            # Display Error if the quantity to sell > available quantity
        if int(product_data["quantity_sold"]) > current_available_quantity:
            error_msg = "Vous n'avez pas ce montant."
            self.mw._handle_user_error(error_msg)
            return

        current_quantity_sold_in_total += int(product_data['quantity_sold'])
        current_sales_spendings_in_total += float(product_data['sale_price'])
        current_available_quantity -= int(product_data['quantity_sold'])

        update_query = f"UPDATE {self.mw.sqlite_table_name} SET {column1} = ?, {column2} = ?, {column3} = ? WHERE categorie = ? AND nom_du_produit = ?"
        self.sqlite.db.insert_data(update_query, (current_quantity_sold_in_total, current_sales_spendings_in_total, current_available_quantity, self.category, self.product_name))

        self.sqlite.insert_data_sqlite(self.sqlite_table_name, self.sqlite_database_columns, list(product_data.values()))

        self.refresh_entry()
        self.mw.update_profits(self.category, self.product_name)
        self.mw.fill_product_data_to_table()
        self.mw.quantiteActuelleLineEdit.setText(str(current_available_quantity))
        self.mw.quantiteVendueTotaleLineEdit.setText(str(current_quantity_sold_in_total))

        self.close()

    def refresh_entry(self):
        self.nomProduitLabel.setText("")
        self.quantiteVendueSpinBox.setValue(0)
        self.prixVendueDoubleSpinBox.setValue(0)
        self.costumerlineEdit.setText("")
        self.categorieLabel.setText("")
        self.plainTextEdit.clear()

        today_date = self.mw.get_today_date()
        self.dateEntreeLineEdit.setText(today_date)
        

    def retrieve_purchase_details(self):
        # Retrieve data from interface
        product_name = self.nomProduitLabel.text()
        quantity_sold = self.quantiteVendueSpinBox.value()
        sale_price = self.prixVendueDoubleSpinBox.value()
        customer = self.costumerlineEdit.text()
        category = self.categorieLabel.text()
        entry_date = self.dateEntreeLineEdit.text()
        notes = self.plainTextEdit.toPlainText()

        product_data = {
            "product_name": product_name,
            "quantity_sold" : quantity_sold,
            "sale_price" : sale_price,
            "customer" : customer,
            "category": category, 
            "entry_date" : entry_date,
            "notes" : notes,
        }
        
        return product_data
    
 
