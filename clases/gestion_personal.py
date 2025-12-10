from datetime import datetime
from clases.empleado import Empleado
from clases.registro import Registro


class GestionPersonal:
    def __init__(self):
        self.empleados = []
        self.registros = []

    def registrar_empleado(self, nombre, dpi, cargo, salario_hora, horario_entrada="08:00", horario_salida="17:00"):
        empleado = Empleado(nombre, dpi, cargo, salario_hora, horario_entrada, horario_salida)
        self.empleados.append(empleado)
        return empleado

    def buscar_empleado_por_dpi(self, dpi):
        for emp in self.empleados:
            if emp.dpi == dpi:
                return emp
        return None