

class AchatsTab:
    def __init__(self, sqlite, mw):
        super().__init__()
        self.sqlite = sqlite
        self.mw = mw
        self.sqlite_table_name = "Purchases"
        self.selection_enabled = False
        self.current_row_count = -1
        self.rows_count = self.mw.achatTableWidget.rowCount()  

        
        self.product_name_coloumn_number = 0
        self.category_coloumn_number = 4

        self.mw.achatTableWidget.itemSelectionChanged.connect(self.selection_changed)
        self.mw.achatTableWidget.itemClicked.connect(self.on_table_item_clicked)
        self.mw.achatSuivantButton.clicked.connect(self.next)
        self.mw.achatPrecedentButton.clicked.connect(self.previous)



        self.mw.achatSupprimerButton.clicked.connect(self.delete_purchase_record)
        # self.mw.achatModifierButton.clicked.connect(self.modify)
        # self.mw.achatSuivantButton.clicked.connect(self.suivant)
        # self.mw.achatPrecedentButton.clicked.connect(self.precedent)

    def delete_purchase_record(self):
        self.mw.delete(self.mw.achatTableWidget, self.sqlite_table_name, self.selection_enabled, self.product_name_coloumn_number, self.category_coloumn_number)
        

    def selection_changed(self):
        selected_items = self.mw.achatTableWidget.selectedItems()
        self.selection_enabled = bool(selected_items)
    
    def on_table_item_clicked(self, item):
        self.current_row_count = item.row()

    def previous(self):
        if self.current_row_count <= 0:
            self.current_row_count = self.mw.achatTableWidget.rowCount()

        self.current_row_count -= 1
        self.mw.achatTableWidget.selectRow(self.current_row_count)


    def next(self):
        if self.current_row_count >= self.mw.achatTableWidget.rowCount()-1:
            self.current_row_count = -1
        self.current_row_count += 1
        self.mw.achatTableWidget.selectRow(self.current_row_count)



 
