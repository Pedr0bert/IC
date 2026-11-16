"""
Blueprint para controle e exibição no Thorlabs EXULUS-HD2
Compatível com Python 3.10+ (64-bit)
"""

import sys
import os
import time
import numpy as np

# Adiciona ao sys.path os caminhos dos módulos fornecidos pelo SDK da Thorlabs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "Thorlabs_EXULUS-HDx_Control"))
sys.path.append(os.path.join(BASE_DIR, "Thorlabs_EXULUS_Display"))
sys.path.append(os.path.join(BASE_DIR, "Thorlabs_EXULUS_CGHCalculate"))

from EXULUS_HDx_COMMAND_LIB import EXULUS_HDx_Control
from Thorlabs_EXULUS_Display import Display

# Parâmetros específicos do EXULUS-HD2
SLM_WIDTH = 1920
SLM_HEIGHT = 1200
SLM_PIXEL_PITCH_M = 8.0e-6   # 8 um
WAVELENGTH_M = 633e-9        # 633 nm (laser He-Ne / calibração padrão)
BAUD_RATE = 38400
TIMEOUT_S = 3


def setup_hardware():
    """Localiza e inicializa os parâmetros de hardware do EXULUS-HD2 via USB."""
    print("[1] Procurando dispositivos EXULUS-HD2 na USB...")
    devices = EXULUS_HDx_Control.list_devices()
    
    if not devices:
        print("  -> Nenhum dispositivo USB encontrado. Verifique alimentação e cabo USB.")
        return None, None

    serial_num, device_type = devices[0]
    print(f"  -> Dispositivo encontrado: Modelo: {device_type}, Serial: {serial_num}")

    hdx = EXULUS_HDx_Control()
    ret = hdx.open(serial_num, BAUD_RATE, TIMEOUT_S)
    if ret < 0:
        raise RuntimeError(f"Falha ao abrir dispositivo {serial_num}")

    # Verificar comunicação (0x06 = ACK)
    ack = [0]
    hdx.check_communication(ack)
    print(f"  -> Comunicação USB: {'OK (0x06)' if ack[0] == 0x06 else hex(ack[0])}")

    # Configurar orientação (sem flip horizontal ou vertical)
    hdx.set_screen_horizontal_flip(0)
    hdx.set_screen_vertical_flip(0)

    # Definir modulação de fase: 0x00 = Full Wave (2pi), 0x01 = Half Wave (pi)
    hdx.set_phase_stroke_mode(0x00)
    print("  -> Phase Stroke Mode: Full Wave (2*pi em 633 nm)")

    return hdx, serial_num


def create_sample_phase_mask(pattern_type="blazed_grating"):
    """
    Gera uma máscara de fase em escala de cinza (0 a 255) 1920x1200.
    
    Exemplos:
    - 'blazed_grating': Grade de difração blazed para deflexão de feixe
    - 'flat': Fase constante (0 a 255)
    """
    x = np.arange(SLM_WIDTH)
    y = np.arange(SLM_HEIGHT)
    xx, yy = np.meshgrid(x, y)

    if pattern_type == "blazed_grating":
        # Período da grade de difração em pixels (ex: 32 pixels)
        period = 32
        phase_raw = (xx % period) / period * 255
        gray_image = phase_raw.astype(np.uint8)

    elif pattern_type == "flat":
        # Nível uniforme de cinza (ex: meio curso = 128)
        gray_image = np.full((SLM_HEIGHT, SLM_WIDTH), 128, dtype=np.uint8)

    else:
        raise ValueError(f"Padrão desconhecido: {pattern_type}")

    return gray_image


def convert_gray_to_bgra(gray_image):
    """
    Converte uma imagem 2D em escala de cinza (uint8) para o formato BGRA
    de 4 canais exigido pela DLL Direct2D do SLM.
    """
    h, w = gray_image.shape
    bgra = np.zeros((h, w, 4), dtype=np.uint8)
    bgra[:, :, 0] = gray_image  # Blue
    bgra[:, :, 1] = gray_image  # Green
    bgra[:, :, 2] = gray_image  # Red
    bgra[:, :, 3] = 255         # Alpha (opaco)
    return bgra


def main():
    hdx = None
    try:
        # 1. Configuração do Hardware via USB
        hdx, serial_no = setup_hardware()

        # 2. Configuração do Display D2D (Saída de Vídeo HDMI)
        with Display() as display_ctrl:
            monitors = display_ctrl.get_display_monitors()
            print(f"[2] Monitores detectados: {len(monitors)}")
            for idx, mon in enumerate(monitors):
                print(f"    Monitor [{idx}]: {mon}")

            if len(monitors) < 2:
                print("AVISO: Menos de 2 monitores detectados. Certifique-se de que o cabo HDMI está conectado "
                      "e o Windows está em modo Estender (Win + P).")
                return

            # O SLM é tipicamente o segundo monitor (índice 1)
            slm_info = str(monitors[1][2])
            adapter_id = [0]
            monitor_id = [0]
            
            found = display_ctrl.get_default_ID(slm_info.encode("utf-8"), adapter_id, monitor_id)
            if not found:
                print("  -> Não foi possível obter IDs padrão para o monitor SLM.")
                return

            print(f"  -> Criando Direct2D Displayer: Adapter={adapter_id[0]}, Monitor={monitor_id[0]}")
            display_ctrl.create_D2D_displayer(adapter_id[0], monitor_id[0])

            # 3. Gerar a máscara e projetar no SLM
            print("[3] Gerando padrão de fase e projetando...")
            phase_gray = create_sample_phase_mask(pattern_type="blazed_grating")
            phase_bgra = convert_gray_to_bgra(phase_gray)

            # Stride = largura * 4 bytes (BGRA)
            stride = SLM_WIDTH * 4
            display_ctrl.display_image(phase_bgra, SLM_WIDTH, SLM_HEIGHT, stride)
            print("  -> Padrão exibido com sucesso no painel!")

            print("[4] Mantendo o padrão no SLM por 10 segundos...")
            time.sleep(10)

    finally:
        # Encerramento seguro da porta serial
        if hdx is not None and getattr(hdx, "hdl", -1) >= 0:
            hdx.close()
            print("[5] Conexão USB com o SLM encerrada.")


if __name__ == "__main__":
    main()
