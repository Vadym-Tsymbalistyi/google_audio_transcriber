from mapping import AI_TO_SHEET_MAP

class SheetManager:
    def __init__(self, sheet):
        self.sheet = sheet

    def update_row_with_analysis(self, row_number: int, analysis_result: dict):
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
        print(f"Row {row_number} updated with transcript and AI analysis.")
