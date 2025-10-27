PES_PARA_CM = 30.48
LIBRAS_PARA_G = 453.592
JARDAS_PARA_M = 0.9144

def converter_altura(valor, unidade):
    if unidade.lower() in ['pés', 'pes', 'foot', 'feet', 'ft']:
        return valor * PES_PARA_CM
    return valor 

def converter_peso(valor, unidade):
    if unidade.lower() in ['libras', 'pounds', 'lb', 'lbs']:
        return valor * LIBRAS_PARA_G
    return valor

def converter_precisao(valor, unidade):
    if unidade.lower() in ['jardas', 'yards', 'yd']:
        return valor * JARDAS_PARA_M
    return valor