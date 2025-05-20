import state
from misc.other_func import note_str_from_db
from state.linedrug_states.new_linedrug_list import NewLineDrugListStateItem
from state.linedrug_states.old_linedrug_list import OldLineDrugListStateItem

LineDrugListStateItem = OldLineDrugListStateItem | NewLineDrugListStateItem
LineDrugListState = (
    list[NewLineDrugListStateItem]
    | list[OldLineDrugListStateItem]
    | list[NewLineDrugListStateItem | OldLineDrugListStateItem]
)


# class LineDrugState:
#     def __get__(self, obj: "state.main_state.State", _) -> LineDrugListStateItem | None:
#         return obj._linedrug

#     def __set__(
#         self, obj: "state.main_state.State", value: LineDrugListStateItem | None
#     ) -> None:
#         obj._linedrug = value
#         match value:
#             case None:
#                 self.onUnset(obj)
#             case item:
#                 self.onSet(obj, item)

#     def onSet(self, obj: "state.main_state.State", item: LineDrugListStateItem) -> None:
#         mv = obj.mv
#         page = mv.order_book.prescriptionpage
#         obj.warehouse = obj.all_warehouse[item.warehouse_id]
#         page.times.ChangeValue(str(item.times))
#         page.dose.ChangeValue(item.dose)
#         page.quantity.ChangeValue(str(item.quantity))
#         page.note.ChangeValue(
#             note_str_from_db(
#                 obj.warehouse.usage,
#                 item.times,
#                 item.dose,
#                 obj.warehouse.usage_unit,
#                 item.usage_note,
#             )
#         )

#     def onUnset(
#         self,
#         obj: "state.main_state.State",
#     ) -> None:
#         mv = obj.mv
#         page = mv.order_book.prescriptionpage
#         obj.warehouse = None
#         page.times.Clear()
#         page.dose.Clear()
#         page.quantity.Clear()
#         page.note.Clear()
class LineDrugState:
    def __get__(self, obj: "state.main_state.State", _) -> LineDrugListStateItem | None:
        return obj._linedrug

    def __set__(self, obj: "state.main_state.State", value: LineDrugListStateItem | None) -> None:
        old_item = obj._linedrug
        new_item = value

        # 1. Nếu trước đó đã có một dòng thuốc cũ, phải trả lại kho cho nó
        if old_item is not None:
            old_wh = obj.all_warehouse[old_item.warehouse_id]
            old_wh.stock_quantity += old_item.quantity

        # 2. Nếu đang set một dòng thuốc mới (không phải None), trừ kho cho nó
        if new_item is not None:
            new_wh = obj.all_warehouse[new_item.warehouse_id]
            # Kiểm tra đủ hàng
            if new_wh.stock_quantity < new_item.quantity:
                raise ValueError(f"Hết hàng: chỉ còn {new_wh.stock_quantity}, bạn kê {new_item.quantity}")
            new_wh.stock_quantity -= new_item.quantity

        # 3. Gán giá trị mới và cập nhật UI
        obj._linedrug = new_item
        match new_item:
            case None:
                self.onUnset(obj)
            case item:
                self.onSet(obj, item)

    def onSet(self, obj: "state.main_state.State", item: LineDrugListStateItem) -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage

        # Đồng bộ warehouse hiện tại
        wh = obj.all_warehouse[item.warehouse_id]
        obj.warehouse = wh

        # Cập nhật UI với giá trị dòng thuốc
        page.times.ChangeValue(str(item.times))
        page.dose.ChangeValue(item.dose)
        page.quantity.ChangeValue(str(item.quantity))
        page.note.ChangeValue(
            note_str_from_db(
                wh.usage,
                item.times,
                item.dose,
                wh.usage_unit,
                item.usage_note,
            )
        )

    def onUnset(self, obj: "state.main_state.State") -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage

        # Khi unset UI, chỉ reset form (kho đã được trả lại ở __set__)
        obj.warehouse = None
        page.times.Clear()
        page.dose.Clear()
        page.quantity.Clear()
        page.note.Clear()
