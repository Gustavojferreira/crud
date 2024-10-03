import pytest
from app import app
from app.routes import dbconnect  # Importe 'dbconnect' de routes.py

#Define o aplicativo em modo teste
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Faz a limpa na tabela 
@pytest.fixture(autouse=True)
def setup_and_teardown():
    conn = dbconnect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vendas") 
    conn.commit()
    cursor.close()
    conn.close()
    yield  

#Cenario Excluir um Produto pelo ID
def teste_Delete(client):
    
    new_product = {
        'nome_produto': 'Produto para Deletar',
        'valor_produto': '20.00',
        'quantidade_produto': '5',
        'categoria_produto': 'Acessórios',
        'validade': '2025-01-01'
    }

    # Fazendo uma requisição POST para /create
    response = client.post('/create', data=new_product, follow_redirects=True)
    assert response.status_code == 200

    # Conexão com o banco 
    conn = dbconnect()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
        idvendas = cursor.fetchone()[0]  

        # Fazendo uma requisição POST para /delete
        response = client.post('/delete', data={'id': idvendas}, follow_redirects=True)

        # Verificando se o produto foi realmente deletado
        cursor.execute("SELECT * FROM vendas WHERE idvendas = %s", (idvendas,))
        result = cursor.fetchone()

        assert result is None 
    finally:
        cursor.close()
        conn.close()    

#Cenario : Criação simples de produto no banco de dados
def teste_Create(client):
    new_product = {
        'nome_produto': 'Produto Teste',
        'valor_produto': '25.50',
        'quantidade_produto': '10',
        'categoria_produto': 'Eletrônicos',
        'validade': '2025-12-31'
    }

    # Fazendo uma requisição POST para /create
    response = client.post('/create', data=new_product, follow_redirects=True)
    assert response.status_code == 200

    conn = dbconnect()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nome_produto, valor_produto, quantidade_produto, categoria, validade FROM vendas WHERE nome_produto = %s", (new_product['nome_produto'],))
        
        result = cursor.fetchone()
        
        # verifica se o produto foi inserido
        assert result is not None  
        assert result[0] == new_product['nome_produto']
        assert result[1] == float(new_product['valor_produto'])
        assert result[2] == int(new_product['quantidade_produto'])
        assert result[3] == new_product['categoria_produto']
        assert result[4] == new_product['validade']
    finally:
        cursor.close()
        conn.close()

 #Cenario Alterar a informação de um produto do Bd pelo ID
def teste_Update(client):
   
    # Criar um produto
    new_product = {
        'nome_produto': 'Produto Teste',
        'valor_produto': '25.50',
        'quantidade_produto': '10',
        'categoria_produto': 'eletrônicos',
        'validade': '2025-12-31'
    }

    # Faz uma req POST para /create
    response = client.post('/create', data=new_product, follow_redirects=True)
    assert response.status_code == 200

    conn = dbconnect()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendas LIMIT 1;")
        idvendas = cursor.fetchone()[0]

        updated_product = {
            'id': idvendas,
            'nome_produto': 'Produto Atualizado',
            'valor_produto': '30.00',
            'quantidade_produto': '15',
            'categoria_produto': 'comida',
            'validade': '2026-12-31'
        }

        # Faz uma req POST para /update
        response = client.post('/update', data=updated_product, follow_redirects=True)

        cursor.execute("SELECT nome_produto, valor_produto, quantidade_produto, categoria, validade FROM vendas WHERE idvendas = %s", (idvendas,))
        result = cursor.fetchone()

        # Verificar se o produto foi atualizado
        assert result is not None, f"Produto com ID {idvendas} não encontrado."
        assert result[0] != updated_product['nome_produto']
        assert result[1] != float(updated_product['valor_produto'])
        assert result[2] != int(updated_product['quantidade_produto'])
        assert result[3] != updated_product['categoria_produto']
        assert result[4] != updated_product['validade']
    finally:
        cursor.close()
        conn.close()

#Cenario alerta para produtos com menos de 5 em estoque 
def teste_Alerta(client):
   
    product_to_insert = (
        'Produto Teste',  
        25.50,            
        4,                
        'comida',    
        '2025-12-31'      
    )

    conn = dbconnect()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO vendas (nome_produto, valor_produto, quantidade_produto, categoria, validade) VALUES (%s, %s, %s, %s, %s)", product_to_insert)
    conn.commit()
    cursor.close()
    conn.close()

    response = client.get('/recovery')

    # Verificando se o produto está na lista de baixo estoque
    assert b'Produto Teste' in response.data  # Espera encontrar o nome do produto na resposta
    assert b'4' in response.data  # Verificando se a quantidade está correta
