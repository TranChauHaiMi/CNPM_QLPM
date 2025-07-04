import wx
import datetime as dt

import db
from db import Gender, Patient, Queue, Visit
from misc import Config, vn_weekdays
from state import State
from ui.generics import DateTextCtrl, PhoneTextCtrl, ReadonlyVNAgeCtrl
from ui.mainview_widgets import (
    DaysCtrl,
    DaysCtrlWithAutoChangePrescriptionQuantity,
    Follow,
    GetWeightBtn,
    NewVisitBtn,
    NoRecheckBtn,
    OrderBook,
    PatientBook,
    PriceCtrl,
    RecheckCtrl,
    SaveBtn,
    UpdateQuantityBtn,
    VisitListCtrl,
    WeightCtrl,
    TemperatureCtrl,
    HeightCtrl
)
from ui.menubar import MyMenuBar



class MainView(wx.Frame):
    def __init__(self, connection: "db.Connection"):
        super().__init__(
            parent=None, pos=(0, 20), title="PHẦN MỀM PHÒNG TƯ AN BÌNH"
        )
        self.patients = []

        self.connection = connection
        self.config = Config.load()
        self.state = State(self)

        self.SetFont(wx.Font(wx.FontInfo(self.config.app_font_size)))

        if self.config.maximize_at_start:
            self.Maximize()

        self.patient_book = PatientBook(self)
        self.visit_list = VisitListCtrl(self)
        self.name = wx.TextCtrl(
            self,
            size=self.config.header_size(0.1),
            name="Họ tên:",
            style=wx.TE_READONLY,
        )
        self.gender = wx.TextCtrl(
            self,
            size=self.config.header_size(0.025),
            name="Giới:",
            style=wx.TE_READONLY,
        )
        self.birthdate = DateTextCtrl(
            self,
            size=self.config.header_size(0.06),
            name="Ngày sinh:",
            style=wx.TE_READONLY,
        )
        self.age = ReadonlyVNAgeCtrl(
            self,
            size=self.config.header_size(0.055),
            name="Tuổi:",
        )
        self.address = wx.TextCtrl(self, name="Địa chỉ:", style=wx.TE_READONLY)
        self.phone = PhoneTextCtrl(
            self,
            size=self.config.header_size(0.055),
            name="Điện thoại:",
            style=wx.TE_READONLY,
        )
        self.past_history = wx.TextCtrl(
            self, style=wx.TE_MULTILINE, name="Bệnh nền, dị ứng:"
        )
        self.diagnosis = wx.TextCtrl(self, name="Chẩn đoán:")
        self.vnote = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Bệnh sử:")
        self.temperature = TemperatureCtrl(self, max=45, name="Nhiệt độ:")
        self.weight = WeightCtrl(self, max=200, name="Cân nặng (kg):")
        self.get_weight_btn = GetWeightBtn(self)
        self.height = HeightCtrl(self, max=200, name="Chiều cao (cm):")
        if self.config.autochange_prescription_quantity_on_day_spin:
            self.days = DaysCtrlWithAutoChangePrescriptionQuantity(
                self, name="Số ngày cho toa:"
            )
            self.updatequantitybtn = UpdateQuantityBtn(self)
            self.updatequantitybtn.Hide()
        else:
            self.days = DaysCtrl(self, name="Số ngày cho toa:")
            self.updatequantitybtn = UpdateQuantityBtn(self)
        self.recheck_weekday = wx.StaticText(
            self, label=vn_weekdays(self.config.default_days_for_prescription)
        )
        self.order_book = OrderBook(self)
        self.recheck = RecheckCtrl(self, name="Số ngày tái khám:")
        self.norecheck = NoRecheckBtn(self)
        self.price = PriceCtrl(self, name="Giá thu:", size=self.config.header_size(0.1))
        self.follow = Follow(self, name="Lời dặn:")
        self.newvisitbtn = NewVisitBtn(self)
        self.savebtn = SaveBtn(self)

        def widget(w, p=0, r=5):
            return (w, p, wx.EXPAND | wx.RIGHT | wx.DOWN, r)

        def widget_with_name(w, p=0, r=5):
            return (
                (
                    wx.StaticText(self, label=w.Name),
                    0,
                    wx.ALIGN_CENTER | wx.RIGHT ,
                    2,
                ),
                widget(w, p, r),
            )

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.AddMany(
            [
                (self.patient_book, 10, wx.EXPAND),
                (wx.StaticText(self, label="Lượt khám cũ:"), 0, wx.EXPAND | wx.ALL, 10),
                (self.visit_list, 4, wx.EXPAND),
            ]
        )
        name_row = wx.BoxSizer(wx.HORIZONTAL)
        name_row.AddMany(
            [
                *widget_with_name(self.name, 1),
                *widget_with_name(self.gender),
                *widget_with_name(self.birthdate),
                *widget_with_name(self.age),
            ]
        )
        addr_row = wx.BoxSizer(wx.HORIZONTAL)
        addr_row.AddMany(
            [*widget_with_name(self.address, 1), *widget_with_name(self.phone)]
        )
        diag_row = wx.BoxSizer(wx.HORIZONTAL)
        diag_row.AddMany([*widget_with_name(self.diagnosis, 1)])
        weight_row = wx.BoxSizer(wx.HORIZONTAL)
        weight_row.AddMany(
            [
                *widget_with_name(self.temperature),
                *widget_with_name(self.weight),
                widget(self.get_weight_btn),
                *widget_with_name(self.height),
                *widget_with_name(self.days),
                (wx.StaticText(self, label="\u21D2"), 0, wx.RIGHT | wx.ALIGN_CENTER, 0),
                (self.recheck_weekday, 0, wx.RIGHT | wx.ALIGN_CENTER, 30),
                widget(self.updatequantitybtn),
            ]
        )
        recheck_row = wx.BoxSizer(wx.HORIZONTAL)
        recheck_row.AddMany(
            [
                *widget_with_name(self.recheck),
                widget(self.norecheck),
                (0, 0, 1),
                *widget_with_name(self.price),
            ]
        )
        follow_up_row = wx.BoxSizer(wx.HORIZONTAL)
        follow_up_row.AddMany(widget_with_name(self.follow, 1))
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddMany(
            [
                widget(self.newvisitbtn),
                widget(self.savebtn),
            ]
        )
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.AddMany(
            [
                (name_row, 0, wx.EXPAND),
                (addr_row, 0, wx.EXPAND),
                (wx.StaticText(self, label=self.past_history.Name), 0, wx.EXPAND),
                widget(self.past_history, 1),
                (diag_row, 0, wx.EXPAND),
                (wx.StaticText(self, label=self.vnote.Name), 0, wx.EXPAND),
                widget(self.vnote, 1),
                (weight_row, 0, wx.EXPAND),
                widget(self.order_book, 6),
                (recheck_row, 0, wx.EXPAND),
                (follow_up_row, 0, wx.EXPAND),
                (btn_row, 0, wx.EXPAND),
            ]
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany(
            [
                (left_sizer, 2, wx.EXPAND | wx.ALL, 10),
                (right_sizer, 3, wx.EXPAND | wx.ALL, 10),
            ]
        )
        self.SetSizerAndFit(sizer)
        self.SetMenuBar(MyMenuBar())
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.refresh_color()
        self.state.refresh_all()

    def onClose(self, e: wx.CloseEvent):
        print("close sqlite3 connection")
        self.connection.close()
        e.Skip()

    def check_diag_wt_filled(self) -> bool:
        diagnosis: str = self.diagnosis.Value
        weight = self.weight.GetWeight()
        if diagnosis.strip() == "":
            wx.MessageBox("Chưa nhập chẩn đoán", "Lỗi")
            return False
        elif weight == 0:
            wx.MessageBox("Cân nặng = 0", "Lỗi")
            return False
        else:
            return True

    def refresh_color(self):
        for widget, name in [
            (self, "mainview"),
            (self.name, "name"),
            (self.gender, "gender"),
            (self.birthdate, "birthdate"),
            (self.age, "age"),
            (self.address, "address"),
            (self.phone, "phone"),
            (self.diagnosis, "diagnosis"),
            (self.past_history, "past_history"),
            (self.vnote, "visit_note"),
            (self.days, "days"),
            (self.recheck, "recheck"),
            (self.price, "price"),
            (self.weight, "weight"),
            (self.follow, "follow"),
            (self.visit_list, "visit_list"),
            (self.patient_book.queuelistctrl, "queue"),
            (self.patient_book.seentodaylistctrl, "seentoday"),
            (self.patient_book.appointmentlistctrl, "appointment"),
            (self.order_book.prescriptionpage.drug_list, "drug_list"),
            (self.order_book.prescriptionpage.drug_picker, "drug_picker"),
            (self.order_book.prescriptionpage.times, "drug_times"),
            (self.order_book.prescriptionpage.dose, "drug_dose"),
            (self.order_book.prescriptionpage.quantity, "drug_quantity"),
            (self.order_book.prescriptionpage.note, "drug_note"),
            (self.order_book.procedurepage.procedure_picker, "procedure_picker"),
            (self.order_book.procedurepage.procedure_list, "procedure_list"),
        ]:
            widget.SetBackgroundColour(self.config.get_background_color(name))

    def load_visit_details(self, visit: Visit):
        # Lấy thông tin bệnh nhân đầy đủ từ database bằng connection.select
        patient = self.connection.select(Patient, visit.patient_id)

        if patient is None:
            wx.MessageBox(f"Không tìm thấy bệnh nhân với ID {visit.patient_id}", "Lỗi dữ liệu")
            return

        # # --- Debugging: Kiểm tra dữ liệu bệnh nhân --- #
        # print(f"Patient loaded: {patient.name}")
        # print(f"Birthdate: {patient.birthdate}")
        # # print(f"Age: {patient.age}") # Bỏ dòng debug age
        # print(f"Phone: {patient.phone}")
        # print(f"Address: {patient.address}")
        # #print(f"Medical History: {patient.medical_history}")
        # # ------------------------------------------- #

        # Cập nhật thông tin bệnh nhân lên UI sử dụng thuộc tính của đối tượng Patient
        self.name.SetValue(patient.name)
        self.gender.SetValue(str(patient.gender) if patient.gender else "") # Chuyển đổi sang string
        # Chuyển đổi ngày sinh sang định dạng dd/mm/YYYY nếu có
        self.birthdate.SetValue(patient.birthdate.strftime("%d/%m/%Y") if patient.birthdate else "")
        self.phone.SetValue(patient.phone or "")
        self.address.SetValue(patient.address or "")
        # Tính toán và hiển thị tuổi
        if patient.birthdate:
            today = dt.date.today()
            age = today.year - patient.birthdate.year - ((today.month, today.day) < (patient.birthdate.month, patient.birthdate.day))
            self.age.SetValue(str(age))
        else:
            self.age.SetValue("")

        # Cập nhật thông tin bệnh sử từ thuộc tính medical_history
        #self.past_history.SetValue(patient.medical_history or "")

        # Cập nhật thông tin phiếu khám
        self.diagnosis.SetValue(visit.diagnosis or "")
        #self.vnote.SetValue(visit.medical_note or "")

        # Cập nhật thông tin đo lường
        self.weight.SetValue(str(visit.weight) if visit.weight else "")
        self.height.SetValue(str(visit.height) if visit.height else "")
        self.temperature.SetValue(str(visit.temperature) if visit.temperature else "")
        self.days.SetValue(str(visit.days) if visit.days else "")

        # Cập nhật thông tin đơn thuốc
        #self.order_book.prescriptionpage.load(visit.prescriptions)

        # Cập nhật thông tin điều trị
        if hasattr(self, "treatmentPanel"):
            self.treatmentPanel.load(visit.treatments)

        # Cập nhật thông tin tái khám
        #self.recheck.SetValue(str(visit.revisit_days or 0))
        #self.follow.SetValue(visit.doctor_note or "")
        #self.price.SetValue(str(visit.fee or "0"))

        # Cập nhật state
        self.state.patient = patient
        self.state.visit = visit


