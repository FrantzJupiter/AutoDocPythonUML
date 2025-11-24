# Auto-Documentação: teste01.py
> Arquivo analisado: `teste01.py`

## 🚀 Fluxo de Execução Global
```mermaid
graph TD
%% Estilos Transparentes
classDef main fill:none,stroke:#9c27b0,stroke-width:2px;
classDef func fill:none,stroke:#2196f3,stroke-width:2px;
classDef cls fill:none,stroke:#ffc107,stroke-width:2px;
Start([__main__])
class Start main
Start --> SmartThermostat
audit_log[[audit_log]]
class audit_log func
scan_network_devices[[scan_network_devices]]
class scan_network_devices func
scan_network_devices --> SmartThermostat
scan_network_devices -.-> SmartDevice
scan_network_devices -.-> SmartThermostat
class SmartThermostat cls
```

## 🏗️ Estrutura de Classes (Por Contexto)
### Contexto: SmartDevice
```mermaid
classDiagram
direction TB
class DeviceMetadata {
  <<Dataclass>>
  +firmware_version : str
  +installation_date : str
  +manufacturer : str
}
class IoTConnectionError {
}
Exception <|-- IoTConnectionError
class SmartDevice {
  <<Abstract>>
  +_is_on : bool
  +device_id
  +is_active : bool
  +metadata : Optional[DeviceMetadata]
  +name
  +__init__(device_id: str, name: str)
  +connect*(protocol: str) : bool
}
ABC <|-- SmartDevice
SmartDevice "1" o-- "1" DeviceMetadata : agregação
class SmartThermostat {
  +_is_on : bool
  +_target_temp : float
  +__init__(device_id: str, name: str)
  +connect(protocol: str) : bool
  +set_temperature(temp: float) : None
}
SmartDevice <|-- SmartThermostat
SmartThermostat ..> IoTConnectionError : usa
```
#### 📍 Navegação Detalhada
- 🟡 **[DeviceMetadata](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:9)** (Linha 9)
  - 🔹 [firmware_version](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:11) `(str)`
  - 🔹 [installation_date](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:12) `(str)`
  - 🔹 [manufacturer](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:10) `(str)`
- 🟡 **[IoTConnectionError](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:14)** (Linha 14)
- 🟡 **[SmartDevice](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:26)** (Linha 26)
  - 🔹 [_is_on](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:30) `(bool)`
  - 🔹 [device_id](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:28)
  - 🔹 [is_active](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:34) `(bool)`
  - 🔹 [metadata](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:31) `(Optional[DeviceMetadata])`
  - 🔹 [name](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:29)
  - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:27)
  - 🔸 [connect*()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:38)
- 🟡 **[SmartThermostat](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:41)** (Linha 41)
  - 🔹 [_is_on](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:53) `(bool)`
  - 🔹 [_target_temp](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:47) `(float)`
  - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:45)
  - 🔸 [connect()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:50)
  - 🔸 [set_temperature()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/teste01.py:56)

---
