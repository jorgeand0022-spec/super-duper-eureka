class CalculadoraSalario:
    @staticmethod
    def calcular_pago(horas_normales, horas_extras, salario_hora):
        pago_normal = horas_normales * salario_hora
        pago_extra = horas_extras * salario_hora * 1.5
        return pago_normal + pago_extra