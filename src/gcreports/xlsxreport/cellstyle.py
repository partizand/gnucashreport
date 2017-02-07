from copy import copy

class CellStyle:
    def __init__(self, cell):
        self._read_from_cell(cell)
        # self.font = font
        # self.border = border
        # self.fill = fill
        # self.number_format = number_format
        # self.protection = protection
        # self.alignment = alignment

    def _read_from_cell(self, cell):
        self.font = copy(cell.font)
        self.border = copy(cell.border)
        self.fill = copy(cell.fill)
        self.number_format = copy(cell.number_format)
        self.protection = copy(cell.protection)
        self.alignment = copy(cell.alignment)
        self.value = copy(cell.value)

    def set_on_cell(self, cell):
        cell.font = copy(self.font)
        cell.border = copy(self.border)
        cell.fill = copy(self.fill)
        cell.number_format = copy(self.number_format)
        cell.protection = copy(self.protection)
        cell.alignment = copy(self.alignment)