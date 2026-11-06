import FreeSimpleGUI as sg
import mysql.connector

db = mysql.connector.connect(
    host="localhost", user="root", password="", database="controle_ativos"
)

cursor = db.cursor()

categorias = ["Monitores", "Teclados", "Cabos", "Outros"]
selected_id = None
dados_carregados = []

layout = [
    [sg.Text("Nome:"), sg.Input(key="-NOME-", size=(25, 1))],
    [
        sg.Text("Categoria:"),
        sg.Combo(
            categorias,
            default_value=categorias[0],
            key="-CATEGORIA-",
            readonly=True,
        ),
    ],
    [sg.Text("Quantidade:"), sg.Input(key="-QTD-", size=(10, 1))],
    [sg.Button("Cadastrar"), sg.Button("Atualizar"), sg.Button("Deletar")],
    [
        sg.Table(
            values=[],
            headings=["Nome do Equipamento", "Categoria", "Quantidade"],
            key="-TABELA-",
            enable_events=True,
            num_rows=6,
        )
    ],
]

window = sg.Window("Controle de Ativos", layout, finalize=True)


def atualizar_tabela():
    global dados_carregados
    cursor.execute("SELECT id, nome, categoria, quantidade FROM ativos")
    dados_carregados = cursor.fetchall()
    window["-TABELA-"].update([[r[1], r[2], r[3]] for r in dados_carregados])


atualizar_tabela()

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "-TABELA-" and values["-TABELA-"]:
        item = dados_carregados[values["-TABELA-"][0]]
        selected_id = item[0]
        window["-NOME-"].update(item[1])
        window["-CATEGORIA-"].update(item[2])
        window["-QTD-"].update(str(item[3]))

    if event == "Cadastrar":
        nome, qtd = values["-NOME-"].strip(), values["-QTD-"].strip()

        if not nome or not qtd.isdigit():
            sg.popup(
                "A quantidade deve conter apenas números inteiros não negativos."
            )
            continue

        cursor.execute(
            "INSERT INTO ativos (nome, categoria, quantidade) VALUES (%s, %s,"
            " %s)",
            (nome, values["-CATEGORIA-"], int(qtd)),
        )
        db.commit()
        atualizar_tabela()
        selected_id = None

    if event == "Atualizar":
        qtd = values["-QTD-"].strip()

        if selected_id is None or not qtd.isdigit():
            sg.popup("Selecione um item e digite uma quantidade válida.")
            continue

        cursor.execute(
            "UPDATE ativos SET quantidade = %s WHERE id = %s",
            (int(qtd), selected_id),
        )
        db.commit()
        atualizar_tabela()
        selected_id = None

    if event == "Deletar":
        if selected_id is None:
            sg.popup("Selecione um item na tabela.")
            continue

        cursor.execute("DELETE FROM ativos WHERE id = %s", (selected_id,))
        db.commit()
        atualizar_tabela()
        selected_id = None

cursor.close()
db.close()
window.close()