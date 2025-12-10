from datetime import datetime

class Registro:
    def __init__(self, fecha, hora_entrada, hora_salida=None):
        self.fecha = fecha
        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida
        self.horas_normales = 0.0
        self.horas_extras = 0.0
        self.salario_hora = 0.0
        self.pago_total = 0.0

    def calcular_horas_trabajadas(self, salario_hora, max_horas_normales=8):
        formato = "%H:%M"
        entrada = datetime.strptime(self.hora_entrada, formato)
        salida = datetime.strptime(self.hora_salida, formato)
        diferencia = (salida - entrada).seconds / 3600

        self.horas_normales = min(diferencia, max_horas_normales)
        self.horas_extras = max(diferencia - max_horas_normales, 0)
        self.salario_hora = salario_hora
        self.pago_total = (
            self.horas_normales * salario_hora +
            self.horas_extras * salario_hora * 1.5
        )

    def to_dict(self):
        return {
            "fecha": self.fecha,
            "hora_entrada": self.hora_entrada,
            "hora_salida": self.hora_salida,
            "horas_normales": round(self.horas_normales, 2),
            "horas_extras": round(self.horas_extras, 2),
            "salario_hora": self.salario_hora,
            "pago_total": round(self.pago_total, 2)
        }

    @classmethod
    def from_dict(cls, data):
        registro = cls(
            fecha=data["fecha"],
            hora_entrada=data["hora_entrada"],
            hora_salida=data.get("hora_salida")
        )
        registro.horas_normales = data.get("horas_normales", 0.0)
        registro.horas_extras = data.get("horas_extras", 0.0)
        registro.salario_hora = data.get("salario_hora", 0.0)
        registro.pago_total = data.get("pago_total", 0.0)
        return registro