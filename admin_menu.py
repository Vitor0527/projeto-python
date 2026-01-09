from utils import read_json, save_json
from datetime import datetime
from typing import List, Dict, Tuple

## FORMATO DA DATA (igual ao usado no menu do cliente)
DATE_FMT = "%Y-%m-%d"


## ---------- FUNÇÕES DE LEITURA/ESCRITA DE FICHEIROS ----------

## Lê definições gerais como dicionário
def load_definitions() -> Dict:
    data = read_json("data/settings.json")
    if isinstance(data, list) and data:
        return data[0]
    else:
        return {}


## Guarda definições gerais
def save_definitions(defs: Dict) -> None:
    save_json("data/settings.json", [defs])


## Lê classes como lista
def load_classes() -> List[Dict]:
    classes = read_json("data/classes.json")
    if isinstance(classes, list):
        return classes
    else:
        return[]


## Guarda classes
def save_classes(classes: List[Dict]) -> None:
    save_json("data/classes.json", classes)


## Lê viaturas como lista
def load_vehicles() -> List[Dict]:
    vehicles = read_json("data/vehicles.json")
    if isinstance(vehicles, list):
        return vehicles
    else:
        return[]

## Guarda viaturas
def save_vehicles(vehicles: List[Dict]) -> None:
    save_json("data/vehicles.json", vehicles)


## Lê reservas como lista
def load_bookings() -> List[Dict]:
    bookings = read_json("data/bookings.json")
    if isinstance(bookings, list):
        return bookings
    else:
        return[]


## ---------- FUNÇÕES AUXILIARES DE DATAS ----------

## Converte string para datetime usando o formato referido antes
def parse_date(value: str) -> datetime:
    return datetime.strptime(value, DATE_FMT)


## Lê uma data do utilizador com validação de formato
def input_data(mensagem: str) -> datetime:
    while True:
        valor = input(mensagem).strip()
        try:
            return parse_date(valor)
        except ValueError:
            print("Data inválida. Use o formato YYYY-MM-DD.")


## Calcula nº de dias de interseção entre dois intervalos [ini, fim)
def dias_intersecao(ini1: datetime, fim1: datetime, ini2: datetime, fim2: datetime) -> int:
    inicio = max(ini1, ini2)
    fim = min(fim1, fim2)
    if fim <= inicio:
        return 0
    return (fim - inicio).days


## ---------- DEFINIÇÕES GERAIS ----------

## Editar max_dias_reserva e tabela de descontos
def gerir_definicoes() -> None:
    defs = load_definitions()
    if not defs:
        defs = {
            "max_dias_reserva": 7,
            "descontos": {
                "ate_3_dias": 0,
                "de_4_a_7_dias": 0,
                "mais_de_7_dias": 0,
            },
        }

    print("\n------ Definições Gerais ------")
    print(f"Max dias reserva atual: {defs.get('max_dias_reserva')}")
    descontos = defs.get("descontos", {})
    print("Descontos atuais (%):")
    print(f"  Até 3 dias: {descontos.get('ate_3_dias', 0)}%")
    print(f"  4 a 7 dias: {descontos.get('de_4_a_7_dias', 0)}%")
    print(f"  Mais de 7 dias: {descontos.get('mais_de_7_dias', 0)}%")

    ## Ler novos valores (ENTER para manter)
    novo_max = input("Novo max_dias_reserva (ENTER para manter): ").strip()
    if novo_max:
        try:
            defs["max_dias_reserva"] = int(novo_max)
        except ValueError:
            print("Valor inválido, mantém-se o anterior.")

    for chave, texto in [
        ("ate_3_dias", "Novo desconto até 3 dias (%)"),
        ("de_4_a_7_dias", "Novo desconto 4-7 dias (%)"),
        ("mais_de_7_dias", "Novo desconto >7 dias (%)"),
    ]:
        atual = descontos.get(chave, 0)
        valor = input(f"{texto} [atual {atual}] (ENTER para manter): ").strip()
        if valor:
            try:
                descontos[chave] = float(valor)
            except ValueError:
                print("Valor inválido, mantém-se o anterior.")

    defs["descontos"] = descontos
    save_definitions(defs)
    print("Definições atualizadas e gravadas em settings.json.\n")


## ---------- GESTÃO DE CLASSES ----------

## Lista classes (id, nome, descrição, preco_diario)
def listar_classes(classes: List[Dict]) -> None:
    print("\n------ Lista de Classes ------")
    if not classes:
        print("Não existem classes definidas.")
        return
    for c in classes:
        print(
            f"ID {c.get('id')} | {c.get('nome')} - {c.get('descrição')} "
            f"| {c.get('preco_diario')} €/dia"
        )


## Cria nova classe garantindo unicidade do id
def criar_classe() -> None:
    classes = load_classes()
    listar_classes(classes)

    try:
        novo_id = int(input("\nID da nova classe: ").strip())
    except ValueError:
        print("ID inválido.")
        return

    ## Validar unicidade do ID
    if any(str(c.get("id")) == str(novo_id) for c in classes):
        print("Já existe uma classe com esse ID.")
        return

    nome = input("Nome da classe: ").strip()
    descricao = input("Descrição: ").strip()
    preco_txt = input("Preço diário (€): ").strip()

    ## Validar campos obrigatórios
    if not nome or not descricao or not preco_txt:
        print("Todos os campos são obrigatórios.")
        return

    try:
        preco = float(preco_txt)
    except ValueError:
        print("Preço inválido.")
        return

    nova = {
        "id": novo_id,
        "nome": nome,
        "descrição": descricao,
        "preco_diario": preco,
    }
    classes.append(nova)
    save_classes(classes)
    print("Classe criada com sucesso.\n")


## Edita uma classe existente
def editar_classe() -> None:
    classes = load_classes()
    if not classes:
        print("Não existem classes para editar.")
        return

    listar_classes(classes)
    id_txt = input("\nID da classe a editar: ").strip()
    classe = next((c for c in classes if str(c.get("id")) == id_txt), None)
    if not classe:
        print("Classe não encontrada.")
        return

    print("ENTER para manter o valor atual.")
    nome = input(f"Nome [{classe.get('nome')}]: ").strip() or classe.get("nome")
    descricao = (
        input(f"Descrição [{classe.get('descrição')}]: ").strip()
        or classe.get("descrição")
    )
    preco_txt = input(f"Preço diário [{classe.get('preco_diario')}]: ").strip()

    if preco_txt:
        try:
            preco = float(preco_txt)
        except ValueError:
            print("Preço inválido, mantém-se o anterior.")
            preco = classe.get("preco_diario")
    else:
        preco = classe.get("preco_diario")

    ## Atualizar valores
    classe["nome"] = nome
    classe["descrição"] = descricao
    classe["preco_diario"] = preco

    save_classes(classes)
    print("Classe atualizada com sucesso.\n")


## Remove uma classe
def remover_classe() -> None:
    classes = load_classes()
    if not classes:
        print("Não existem classes para remover.")
        return

    listar_classes(classes)
    id_txt = input("\nID da classe a remover: ").strip()
    nova_lista = [c for c in classes if str(c.get("id")) != id_txt]

    if len(nova_lista) == len(classes):
        print("Classe não encontrada.")
        return

    save_classes(nova_lista)
    print("Classe removida com sucesso.\n")


## Menu de gestão de classes
def menu_classes() -> None:
    while True:
        print("\n------ Gestão de Classes ------")
        print("1. Listar classes")
        print("2. Criar classe")
        print("3. Editar classe")
        print("4. Remover classe")
        print("5. Voltar")
        op = input("Opção: ").strip()

        if op == "1":
            listar_classes(load_classes())
        elif op == "2":
            criar_classe()
        elif op == "3":
            editar_classe()
        elif op == "4":
            remover_classe()
        elif op == "5":
            break
        else:
            print("Opção inválida.")


## ---------- GESTÃO DE FROTA ----------

## Lista viaturas (matricula, marca, modelo, id_classe, estado)
def listar_viaturas(vehicles: List[Dict]) -> None:
    print("\n------ Frota de Viaturas ------")
    if not vehicles:
        print("Não existem viaturas.")
        return
    for v in vehicles:
        print(
            f"{v.get('matricula')} | {v.get('marca')} {v.get('modelo')} "
            f"| classe {v.get('id_classe')} | estado: {v.get('estado')}"
        )


## Verifica se existe classe com dado id
def existe_classe(id_classe, classes: List[Dict]) -> bool:
    return any(str(c.get("id")) == str(id_classe) for c in classes)


## Adiciona nova viatura
def adicionar_viatura() -> None:
    vehicles = load_vehicles()
    classes = load_classes()

    listar_viaturas(vehicles)

    matricula = input("\nMatrícula: ").strip().upper()
    ## Validar unicidade da matrícula
    if any(v.get("matricula") == matricula for v in vehicles):
        print("Já existe uma viatura com essa matrícula.")
        return

    marca = input("Marca: ").strip()
    modelo = input("Modelo: ").strip()
    id_txt = input("ID da classe: ").strip()
    estado = input("Estado (ativo/inativo): ").strip().lower() or "ativo"

    if not matricula or not marca or not modelo or not id_txt:
        print("Todos os campos são obrigatórios.")
        return

    try:
        id_classe = int(id_txt)
    except ValueError:
        print("ID da classe inválido.")
        return

    ## Validar existência da classe
    if not existe_classe(id_classe, classes):
        print("Não existe nenhuma classe com esse ID.")
        return

    if estado not in ("ativo", "inativo"):
        print("Estado inválido, será considerado 'ativo'.")
        estado = "ativo"

    nova = {
        "matricula": matricula,
        "marca": marca,
        "modelo": modelo,
        "id_classe": id_classe,
        "estado": estado,
    }
    vehicles.append(nova)
    save_vehicles(vehicles)
    print("Viatura adicionada com sucesso.\n")


## Edita uma viatura
def editar_viatura() -> None:
    vehicles = load_vehicles()
    if not vehicles:
        print("Não existem viaturas para editar.")
        return

    classes = load_classes()
    listar_viaturas(vehicles)

    mat = input("\nMatrícula da viatura a editar: ").strip().upper()
    v = next((x for x in vehicles if x.get("matricula") == mat), None)
    if not v:
        print("Viatura não encontrada.")
        return

    print("ENTER para manter o valor atual.")
    marca = input(f"Marca [{v.get('marca')}]: ").strip() or v.get("marca")
    modelo = input(f"Modelo [{v.get('modelo')}]: ").strip() or v.get("modelo")
    id_txt = input(f"ID classe [{v.get('id_classe')}]: ").strip()
    estado = input(f"Estado (ativo/inativo) [{v.get('estado')}]: ").strip() or v.get(
        "estado"
    )

    if id_txt:
        try:
            id_classe = int(id_txt)
        except ValueError:
            print("ID de classe inválido, mantém-se o anterior.")
            id_classe = v.get("id_classe")
        else:
            if not existe_classe(id_classe, classes):
                print("Classe inexistente, mantém-se o anterior.")
                id_classe = v.get("id_classe")
    else:
        id_classe = v.get("id_classe")

    if estado not in ("ativo", "inativo"):
        print("Estado inválido, mantém-se o anterior.")
        estado = v.get("estado")

    ## Atualizar
    v["marca"] = marca
    v["modelo"] = modelo
    v["id_classe"] = id_classe
    v["estado"] = estado

    save_vehicles(vehicles)
    print("Viatura atualizada com sucesso.\n")


## Remove uma viatura
def remover_viatura() -> None:
    vehicles = load_vehicles()
    if not vehicles:
        print("Não existem viaturas para remover.")
        return

    listar_viaturas(vehicles)
    mat = input("\nMatrícula da viatura a remover: ").strip().upper()
    nova_lista = [v for v in vehicles if v.get("matricula") != mat]

    if len(nova_lista) == len(vehicles):
        print("Viatura não encontrada.")
        return

    save_vehicles(nova_lista)
    print("Viatura removida com sucesso.\n")


## Menu de gestão de frota
def menu_frota() -> None:
    while True:
        print("\n------ Gestão de Frota ------")
        print("1. Listar viaturas")
        print("2. Adicionar viatura")
        print("3. Editar viatura")
        print("4. Remover viatura")
        print("5. Voltar")
        op = input("Opção: ").strip()

        if op == "1":
            listar_viaturas(load_vehicles())
        elif op == "2":
            adicionar_viatura()
        elif op == "3":
            editar_viatura()
        elif op == "4":
            remover_viatura()
        elif op == "5":
            break
        else:
            print("Opção inválida.")


## ---------- EXTRATO DIÁRIO ----------

## Mostra reservas de uma determinada data e resumo
def extrato_diario() -> None:
    bookings = load_bookings()
    if not bookings:
        print("Não existem reservas.")
        return

    data = input_data("Data para extrato diário (YYYY-MM-DD): ")
    vehicles = load_vehicles()
    classes = load_classes()

    ## Mapa matricula -> id_classe
    mapa_viaturas = {v.get("matricula"): v.get("id_classe") for v in vehicles}

    print(f"\n------ Extrato do dia {data.strftime(DATE_FMT)} ------")
    selecionadas = []
    total = 0.0
    total_dias = 0
    por_classe = {}

    for b in bookings:
        try:
            ini = parse_date(b.get("data_inicio"))
            fim = parse_date(b.get("data_fim"))
        except Exception:
            continue

        ## Verificar se a reserva inicia ou ocorre nessa data
        ocorre = ini <= data < fim
        if not ocorre:
            continue

        selecionadas.append(b)
        valor = float(b.get("total", 0))
        dias = int(b.get("dias", 0))
        total += valor
        total_dias += dias

        id_classe = mapa_viaturas.get(b.get("matricula"))
        if id_classe is not None:
            por_classe[id_classe] = por_classe.get(id_classe, 0) + valor

    if not selecionadas:
        print("Não existem reservas para essa data.")
        return

    for i, b in enumerate(selecionadas, 1):
        print(
            f"{i}. {b.get('email')} | {b.get('matricula')} | "
            f"{b.get('data_inicio')} -> {b.get('data_fim')} | "
            f"{b.get('dias')} dias | total {b.get('total')}€"
        )

    print("\nResumo do dia:")
    print(f"  Total faturado: {total}€")
    print(f"  Nº de reservas: {len(selecionadas)}")
    print(f"  Dias totais alugados: {total_dias}")

    ## Distribuição por classe (usar nome se existir)
    if por_classe:
        print("  Distribuição por classe:")
        for id_classe, valor in por_classe.items():
            nome = next(
                (c.get("nome") for c in classes if str(c.get("id")) == str(id_classe)),
                f"Classe {id_classe}",
            )
            print(f"    {nome}: {valor}€")


## ---------- ESTATÍSTICAS ----------

## Calcula e mostra estatísticas globais, por classe e por viatura
def estatisticas() -> None:
    bookings = load_bookings()
    if not bookings:
        print("Não existem reservas.")
        return

    print("\n------ Estatísticas ------")
    print("Indique o intervalo de datas para análise.")
    ini = input_data("Data início (YYYY-MM-DD): ")
    fim = input_data("Data fim (YYYY-MM-DD): ")

    if fim <= ini:
        print("Data fim deve ser posterior à data início.")
        return

    vehicles = load_vehicles()
    classes = load_classes()
    periodo_dias = (fim - ini).days

    ## Mapas auxiliares
    mapa_viaturas = {v.get("matricula"): v for v in vehicles}
    mapa_classe_por_mat = {v.get("matricula"): v.get("id_classe") for v in vehicles}

    total_faturado = 0.0
    num_reservas = 0
    dias_alugados_total = 0

    ## Acumuladores por classe e por viatura
    por_classe = {}  # id_classe -> dict
    por_viatura = {}  # matricula -> dict

    for b in bookings:
        try:
            b_ini = parse_date(b.get("data_inicio"))
            b_fim = parse_date(b.get("data_fim"))
        except Exception:
            continue

        ## Verificar se há interseção com o período escolhido
        dias_int = dias_intersecao(b_ini, b_fim, ini, fim)
        if dias_int <= 0:
            continue

        num_reservas += 1
        valor = float(b.get("total", 0))
        total_faturado += valor
        dias_alugados_total += dias_int

        mat = b.get("matricula")
        id_classe = mapa_classe_por_mat.get(mat)

        ## Por classe
        if id_classe is not None:
            dados = por_classe.setdefault(
                id_classe, {"total": 0.0, "reservas": 0, "dias": 0}
            )
            dados["total"] += valor
            dados["reservas"] += 1
            dados["dias"] += dias_int

        ## Por viatura
        dados_v = por_viatura.setdefault(
            mat, {"total": 0.0, "reservas": 0, "dias": 0}
        )
        dados_v["total"] += valor
        dados_v["reservas"] += 1
        dados_v["dias"] += dias_int

    if num_reservas == 0:
        print("Não existem reservas no intervalo indicado.")
        return

    ## Estatísticas globais
    preco_medio = total_faturado / num_reservas if num_reservas else 0
    print("\n--- Globais ---")
    print(f"Total faturado: {total_faturado}€")
    print(f"Nº de reservas: {num_reservas}")
    print(f"Dias alugados: {dias_alugados_total}")
    print(f"Preço médio por reserva: {preco_medio:.2f}€")

    ## Estatísticas por classe
    print("\n--- Por classe ---")
    for id_classe, dados in por_classe.items():
        nome = next(
            (c.get("nome") for c in classes if str(c.get("id")) == str(id_classe)),
            f"Classe {id_classe}",
        )
        dias = dados["dias"]
        preco_medio_dia = dados["total"] / dias if dias else 0
        print(
            f"{nome}: total {dados['total']}€ | reservas {dados['reservas']} | "
            f"dias alugados {dias} | preço médio efetivo/dia {preco_medio_dia:.2f}€"
        )

    ## Estatísticas por viatura
    print("\n--- Por viatura (matrícula) ---")
    for mat, dados in por_viatura.items():
        info = mapa_viaturas.get(mat, {})
        print(
            f"{mat} ({info.get('marca','')} {info.get('modelo','')}): "
            f"reservas {dados['reservas']} | dias alugados {dados['dias']} | "
            f"total faturado {dados['total']}€ | "
        )


## ---------- MENU PRINCIPAL DO ADMINISTRADOR ----------

## Mostra o menu do administrador
def menu_admin(current_user=None):
    while True:
        print("\n-------- Menu Administrador --------")
        print("1. Definições gerais")
        print("2. Gestão de classes")
        print("3. Gestão de frota")
        print("4. Extrato diário")
        print("5. Estatísticas")
        print("6. Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            gerir_definicoes()
        elif escolha == "2":
            menu_classes()
        elif escolha == "3":
            menu_frota()
        elif escolha == "4":
            extrato_diario()
        elif escolha == "5":
            estatisticas()
        elif escolha == "6":
            print("A sair do menu de administrador...")
            break
        else:
            print("Opção inválida.\n")