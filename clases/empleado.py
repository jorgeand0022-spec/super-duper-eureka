import re

class Empleado:
    def __init__(self, nombre, dpi, cargo, salario_hora):
        # Validar campos
        if not self.validar_nombre(nombre):
            raise ValueError("El nombre contiene caracteres inválidos.")
        if not self.validar_dpi(dpi):
            raise ValueError("El DPI contiene caracteres inválidos.")
        if not self.validar_cargo(cargo):
            raise ValueError("El cargo contiene caracteres inválidos.")

        self.nombre = nombre
        self.dpi = dpi
        self.cargo = cargo
        self.salario_hora = salario_hora

    @staticmethod
    def validar_nombre(nombre):
        """Permite letras, espacios y apóstrofes"""
        return bool(re.match(r"^[a-zA-Z\sáéíóúÁÉÍÓÚñÑ]+$", nombre))

    @staticmethod
    def validar_dpi(dpi):
        """Permite solo números y ciertos caracteres específicos (opcional)"""
        return bool(re.match(r"^\d+$", dpi))

    @staticmethod
    def validar_cargo(cargo):
        """Permite letras, espacios y apóstrofes"""
        return bool(re.match(r"^[a-zA-Z\sáéíóúÁÉÍÓÚñÑ]+$", cargo))

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "dpi": self.dpi,
            "cargo": self.cargo,
            "salario_hora": self.salario_hora,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data.get("nombre", ""),
            dpi=data.get("dpi", ""),
            cargo=data.get("cargo", ""),
            salario_hora=data.get("salario_hora", 0.0),
        
        )