from mapping import AI_TO_SHEET_MAP
import logging

class SheetManager:
    def __init__(self, sheet):
        self.logger = logging.getLogger("SheetManager")
        self.sheet = sheet
        self.logger.debug("SheetManager initialized.")

    def update_row_with_analysis(self, row_number: int, analysis_result: dict):
        self.logger.debug("Updating row %d with AI analysis...", row_number)
        updates = []
        for key, col in AI_TO_SHEET_MAP.items():
            val = analysis_result.get(key, "Ні")
            if isinstance(val, list):
                val = ", ".join(val)
            updates.append((col, val))

        data = []
        for col, val in updates:
            data.append({
                'range': f'{col}{row_number}',
                'values': [[val]]
            })

        self.sheet.batch_update(data)
        self.logger.info("Row %d updated successfully with transcript and AI analysis.", row_number)
