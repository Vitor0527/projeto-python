from utils import read_json, save_json
from datetime import datetime
from typing import List, Dict, Tuple

## FORMATO DA DATA
DATE_FMT = "%Y-%m-%d"

## Lê definições gerais como dicionário
def load_definitions() -> Dict:
    data = read_json("data/settings.json")
    return data[0]

## Lê classes como uma lista
def load_classes() -> List[Dict]:
    classes = read_json("data/classes.json")
    return classes if isinstance(classes, list) else []

## Lê veiculos como uma lista
def load_vehicles() -> List[Dict]:
    vehicles = read_json("data/vehicles.json")
    return vehicles if isinstance(vehicles, list) else []

## Lê historico como uma lista
def load_bookings() -> List[Dict]:
    bookings = read_json("data/bookings.json")
    return bookings if isinstance(bookings, list) else []

## Salvar historico
def save_bookings(bookings: List[Dict]) -> None:
    save_json("data/bookings.json", bookings)

## Converte string para datetime usando o formato referido antes
def parse_date(value: str) -> datetime:
    return datetime.strptime(value, DATE_FMT)

## Validar se a data está correta (formato, se o fim da data ser posterior ao inicio e se a reserva exceder o maximo de dias)
def validar_intervalo(data_inicio: str, data_fim: str, max_dias: int) -> Tuple[bool, str, int]:
    try:
        inicio = parse_date(data_inicio)
        fim = parse_date(data_fim)
    except ValueError:
        return False, "Datas devem estar no formato YYYY-MM-DD.", 0

    if fim <= inicio:
        return False, "data_fim deve ser posterior a data_inicio.", 0

    dias = (fim - inicio).days
    if dias > max_dias:
        return False, f"Reserva excede o máximo de {max_dias} dias.", 0
    return True, "", dias

## Verifica se a data enviada sobrepoe a que já esta reservada
def esta_disponivel(matricula: str, data_inicio: str, data_fim: str, bookings: List[Dict]) -> bool:
    try:
        novo_inicio = parse_date(data_inicio)
        novo_fim = parse_date(data_fim)
    except ValueError:
        return False

    for b in bookings:
        if b.get("matricula") != matricula:
            continue
        # intervalo [inicio, fim)
        try:
            ini = parse_date(b["data_inicio"])
            fim = parse_date(b["data_fim"])
        except Exception:
            continue
        sobrepoe = not (novo_fim <= ini or novo_inicio >= fim)
        if sobrepoe:
            return False
    return True

## Obtem o preço diario
def obter_preco_diario(id_classe, classes: List[Dict]) -> float:
    for cls in classes:
        if str(cls.get("id")) == str(id_classe):
            return float(cls.get("preco_diario", 0))
    return 0.0

## Calcula o preço com descontos
def calcular_preco(dias: int, preco_diario: float, defs: Dict) -> Tuple[float, float]:
    descontos = defs.get("descontos", {})
    if dias <= 3:
        desconto = descontos.get("ate_3_dias", 0)
    elif dias <= 7:
        desconto = descontos.get("de_4_a_7_dias", 10)
    else:
        desconto = descontos.get("mais_de_7_dias", 20)
    fator = 1 - desconto / 100
    total = round(dias * preco_diario * fator, 2)
    return desconto, total

## Mostra os carros disponíveis
def mostrar_carros(carros: List[Dict]) -> None:
    ativos = [c for c in carros if c.get("estado") == "ativo"]
    print("\n--------Carros Disponíveis-------")
    if not ativos:
        print("Não temos carros disponíveis.")
        return
    for c in ativos:
        print(f"{c['matricula']} - {c['marca']} {c['modelo']} (classe {c.get('id_classe')})")

## Reserva a viatura e atualiza bookings
def reservar_viatura(current_user: Dict, carros: List[Dict], classes: Dict, defs: Dict, bookings: List[Dict]) -> List[Dict]:

    ## Se não tiver ativos
    ativos = [c for c in carros if c.get("estado") == "ativo"]
    if not ativos:
        print("Não há viaturas ativas para reservar.\n")
        return bookings

    ## Mostra os carros para puder reservar
    mostrar_carros(carros)
    matricula = input("\nMatrícula a reservar: ").strip()
    viatura = next((c for c in ativos if c.get("matricula") == matricula), None)

    ## Se não for ativo ou não for encontrado
    if not viatura:
        print("Matrícula não encontrada ou inativa.\n")
        return bookings

    ## Inserir datas
    data_inicio = input("Data de início (YYYY-MM-DD): ").strip()
    data_fim = input("Data de fim (YYYY-MM-DD): ").strip()

    ## Se passar do maximo de dias de reserva
    ok, msg, dias = validar_intervalo(data_inicio, data_fim, defs.get("max_dias_reserva"))
    if not ok:
        print(f"Erro: {msg}\n")
        return bookings

    ## Se não tiver disponivel nesse período
    if not esta_disponivel(matricula, data_inicio, data_fim, bookings):
        print("Viatura indisponível nesse período.\n")
        return bookings

    preco_diario = obter_preco_diario(viatura.get("id_classe"), classes)
    desconto, total = calcular_preco(dias, preco_diario, defs)

    reserva = {
        "email": current_user.get("email"),
        "matricula": matricula,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "dias": dias,
        "preco_diario": preco_diario,
        "desconto": desconto,
        "total": total,
    }
    bookings.append(reserva)

    # Manter histórico ordenado por data_inicio e salvar
    bookings = sorted(bookings, key=lambda b: b.get("data_inicio", ""))
    save_bookings(bookings)
    print(f"Reserva criada. Total: {total}€ (desconto {desconto}%).\n")
    return bookings

## Ver historico de reservas
def ver_historico(bookings: List[Dict], current_user: Dict) -> None:
    historico = [b for b in bookings if b.get("email") == current_user.get("email")]
    print("\n-----Histórico de Reservas-----")
    if not historico:
        print("Ainda não tem reservas.")
        return
    for i, b in enumerate(historico, 1):
        print(
            f"{i}. {b['matricula']} | {b['data_inicio']} -> {b['data_fim']} | "
            f"{b['dias']} dias | total {b['total']}€"
        )

## Ver o menu do cliente
def menu_client(current_user=None):
    carros = load_vehicles()
    classes = load_classes()
    defs = load_definitions()
    bookings = load_bookings()

    while True:
        print("\n--------Menu Cliente--------")
        print("1. Ver carros disponíveis")
        print("2. Efetuar reserva")
        print("3. Ver histórico de reservas")
        print("4. Sair")
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "1":
            mostrar_carros(carros)
        elif escolha == "2":
            bookings = reservar_viatura(current_user or {}, carros, classes, defs, bookings)
        elif escolha == "3":
            ver_historico(bookings, current_user or {})
        elif escolha == "4":
            print("Saindo...")
            break
        else:
            print("Opção inválida.\n")
