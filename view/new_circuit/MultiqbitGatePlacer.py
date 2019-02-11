import wx

from view.new_circuit.constants import GATE_H_SPACE, GATE_SIZE


class MultiqbitGatePlacer:

    def __init__(self, circuit, quantumComputer):
        self.circuit = circuit
        self.controlPlaced = False
        self.controlIJ = (-1, -1)
        self.m_y = -1  # mouse_y
        self.quantumComputer = quantumComputer

    def __on_slot_selected(self, m_x, m_y, callback):
        if self.circuit.getW() > m_x > 2 * GATE_SIZE:
            if self.circuit.getH(qbitAreaOnly=True) > m_y > 0:
                i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
                callback(i, j)

    def place_control_bit(self, m_x, m_y, filled_slots):
        def init_multi(i, j):
            if not (i, j) in filled_slots:
                self.controlPlaced = True
                self.controlIJ = (i, j)
                self.circuit.Refresh()
        self.__on_slot_selected(m_x, m_y, init_multi)

    def place_target(self, m_x, m_y):
        if not self.controlPlaced:
            return
        self.cancel_drawing_control_line()
        self.__on_slot_selected(m_x, m_y, self.__on_place_target)

    def __on_place_target(self, i_target, j_target):
        if self.quantumComputer.can_put_target(*self.controlIJ, i_target, j_target):
            self.quantumComputer.put_ctrl(self.controlIJ[0], i_target, j_target)
            self.circuit.resetView()

    def update_control_line(self, event):
        if not self.controlPlaced:
            return
        _, m_y = event.GetPosition()
        if abs(m_y - self.m_y) > 5:
            self.m_y = m_y
            self.circuit.Refresh()

    def cancel_drawing_control_line(self):
        self.controlPlaced = False
        self.circuit.Refresh()

    def draw_control_line(self, dc):
        if not self.controlPlaced: return
        ctrl_x, ctrl_y = self.circuit.ij_to_xy(*self.controlIJ)
        self.__draw_control_line_from_to(dc, ctrl_x, ctrl_y, self.m_y)

    def __draw_control_line_from_to(self, dc, ctrl_x, ctrl_y, target_y):
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetBrush(wx.Brush(wx.BLACK))
        dc.DrawCircle(ctrl_x, ctrl_y, 6)
        dc.DrawLine(ctrl_x, ctrl_y, ctrl_x, target_y)

    def draw_multiqubit_gates(self, dc, multiqubit_gates):
        # multiqubit_gates: {(ctrl1, j1) -> (name_1, target_i_1), (ctrl2, j2) -> (name_2, target_i_2)...}
        for (i_ctrl,j), (_, i_target) in multiqubit_gates.items():
            ctrl_x, ctrl_y = self.circuit.ij_to_xy(i_ctrl, j)
            _, target_y = self.circuit.ij_to_xy(i_target, j)
            self.__draw_control_line_from_to(dc, ctrl_x, ctrl_y, target_y)