"""
Core Enigma Machine Logic for MicroPython
"""

class Rotor:
    """Rotor of the Enigma Machine"""
    
    def __init__(self, numero, cableado, notch):
        self.numero = numero
        self.cableado = cableado
        self.alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.notch = notch
        self.posicion = 0
        
    def cifrar_adelante(self, letra):
        """Encrypts a letter passing through the rotor from right to left"""
        indice = (self.alfabeto.index(letra) + self.posicion) % 26
        letra_cifrada = self.cableado[indice]
        indice_salida = (self.alfabeto.index(letra_cifrada) - self.posicion) % 26
        return self.alfabeto[indice_salida]
    
    def cifrar_atras(self, letra):
        """Encrypts a letter on the return path"""
        indice = (self.alfabeto.index(letra) + self.posicion) % 26
        letra_ajustada = self.alfabeto[indice]
        indice_cableado = self.cableado.index(letra_ajustada)
        indice_salida = (indice_cableado - self.posicion) % 26
        return self.alfabeto[indice_salida]
    
    def avanzar(self):
        """Advances the rotor by one position"""
        self.posicion = (self.posicion + 1) % 26
        return self.alfabeto[self.posicion] == self.notch
    
    def set_posicion(self, letra):
        """Sets the initial position of the rotor"""
        self.posicion = self.alfabeto.index(letra)


class Reflector:
    """Reflector that inverts the signal"""
    
    def __init__(self, cableado):
        self.cableado = cableado
        
    def reflejar(self, letra):
        indice = ord(letra) - ord('A')
        return self.cableado[indice]


class MaquinaEnigma:
    """Main engine of the Enigma Machine"""
    
    ROTORES_DISPONIBLES = {
        'I': {'cableado': 'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'notch': 'Q'},
        'II': {'cableado': 'AJDKSIRUXBLHWTMCQGZNPYFVOE', 'notch': 'E'},
        'III': {'cableado': 'BDFHJLCPRTXVZNYEIWGAKMUSQO', 'notch': 'V'},
        'IV': {'cableado': 'ESOVPZJAYQUIRHXLNFTGKDCMWB', 'notch': 'J'},
        'V': {'cableado': 'VZBRGITYUPSDNHLXAWMJQOFECK', 'notch': 'Z'}
    }
    
    REFLECTOR_B = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'
    
    def __init__(self, seleccion_rotores, posiciones_iniciales='AAA'):
        """Initializes the Enigma Machine"""
        if len(seleccion_rotores) < 3 or len(seleccion_rotores) > 5:
            raise ValueError("Must select between 3 and 5 rotors")
        
        self.rotores = []
        for i, num_rotor in enumerate(seleccion_rotores):
            if num_rotor not in self.ROTORES_DISPONIBLES:
                raise ValueError("Rotor {} no válido".format(num_rotor))
            
            config = self.ROTORES_DISPONIBLES[num_rotor]
            rotor = Rotor(num_rotor, config['cableado'], config['notch'])
            
            if i < len(posiciones_iniciales):
                rotor.set_posicion(posiciones_iniciales[i])
            
            self.rotores.append(rotor)
        
        self.reflector = Reflector(self.REFLECTOR_B)
    
    def cifrar_letra(self, letra):
        """Encrypts a single letter"""
        # Simple check for MicroPython compatibility (no isalpha on all platforms sometimes, but usually ok)
        if not (letra >= 'A' and letra <= 'Z') and not (letra >= 'a' and letra <= 'z'):
            return letra
        
        letra = letra.upper()
        self._avanzar_rotores()
        
        for rotor in reversed(self.rotores):
            letra = rotor.cifrar_adelante(letra)
        
        letra = self.reflector.reflejar(letra)
        
        for rotor in self.rotores:
            letra = rotor.cifrar_atras(letra)
        
        return letra
    
    def _avanzar_rotores(self):
        """Advances the rotors according to Enigma mechanics"""
        avanzar_siguiente = self.rotores[-1].avanzar()
        
        for i in range(len(self.rotores) - 2, -1, -1):
            if avanzar_siguiente:
                avanzar_siguiente = self.rotores[i].avanzar()
            else:
                break
    
    def cifrar_mensaje(self, mensaje):
        """Encrypts a complete message"""
        resultado = []
        for letra in mensaje:
            resultado.append(self.cifrar_letra(letra))
        return ''.join(resultado)
