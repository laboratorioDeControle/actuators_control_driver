#!/usr/bin/env python3
import serial

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
print("Receptor iniciado. Aguardando comandos...")

try:
    while True:
        linha = ser.readline().decode('utf-8').strip()
        if linha:
            try:
                angulo_str, velocidade_str = linha.split(",")
                angulo = int(angulo_str)
                velocidade = float(velocidade_str)
                print(f"Recebido: Ângulo={angulo}, Velocidade={velocidade}")
            except ValueError:
                print("Mensagem inválida:", linha)

except KeyboardInterrupt:
    print("\nEncerrando receptor.")
    ser.close()
