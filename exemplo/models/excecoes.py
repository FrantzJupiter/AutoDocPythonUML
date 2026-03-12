class PlanoInvalidoException(Exception):
    def __init__(self, plano):
        super().__init__(f"Plano inválido: '{plano}'. Utilize 'basic' ou 'premium'.")

