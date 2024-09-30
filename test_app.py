import pytest
from app import app
from app.routes import dbconnect  # Importe 'dbconnect' de routes.py


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Faz o rapa na tabela
    conn = dbconnect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vendas") 
    conn.commit()
    cursor.close()
    conn.close()
    yield  


def teste_Create(client):
    new_product = {
        'nome_produto': 'Produto Teste',
        'valor_produto': '25.50',
        'quantidade_produto': '10',
        'categoria_produto': 'Eletrônicos',
        'validade': '2025-12-31'
    }

    # Fazendo uma requisição POST para a rota /create
    response = client.post('/create', data=new_product, follow_redirects=True)
    assert response.status_code == 200

    # Conexão com o banco
    conn = dbconnect()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nome_produto, valor_produto, quantidade_produto, categoria, validade FROM vendas WHERE nome_produto = %s", (new_product['nome_produto'],))
        
        result = cursor.fetchone()
        
        # Verificar se o produto foi inserido corretamente
        assert result is not None  
        assert result[0] == new_product['nome_produto']
        assert result[1] == float(new_product['valor_produto'])
        assert result[2] == int(new_product['quantidade_produto'])
        assert result[3] == new_product['categoria_produto']
        assert result[4] == new_product['validade']
    finally:
        cursor.close()
        conn.close()


def teste_Update(client):
    # Criar um produto para garantir que temos algo para atualizar
    new_product = {
        'nome_produto': 'Produto Teste',
        'valor_produto': '25.50',
        'quantidade_produto': '10',
        'categoria_produto': 'Eletrônicos',
        'validade': '2025-12-31'
    }

    # Fazendo uma requisição POST para a rota /create
    response = client.post('/create', data=new_product, follow_redirects=True)
    assert response.status_code == 200

    # Conexão com o banco para obter o ID do produto inserido
    conn = dbconnect()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendas LIMIT 1;")
        idvendas = cursor.fetchone()[0]  # Obtém o ID do último produto inserido

        # Dados atualizados do produto
        updated_product = {
            'id': idvendas,
            'nome_produto': 'Produto Atualizado',
            'valor_produto': '30.00',
            'quantidade_produto': '15',
            'categoria_produto': 'Eletrônico',
            'validade': '2026-12-31'
        }

        # Fazendo uma requisição POST para a rota /update
        response = client.post('/update', data=updated_product, follow_redirects=True)

        # Verifique se a resposta foi bem-sucedida
        assert response.status_code == 200

        # Verificando se o produto foi atualizado corretamente
        cursor.execute("SELECT nome_produto, valor_produto, quantidade_produto, categoria, validade FROM vendas WHERE idvendas = %s", (idvendas,))
        result = cursor.fetchone()

        # Verificar se o produto foi atualizado corretamente
        assert result is not None, f"Produto com ID {idvendas} não encontrado."
        assert result[0] != updated_product['nome_produto']
        assert result[1] != float(updated_product['valor_produto'])
        assert result[2] != int(updated_product['quantidade_produto'])
        assert result[3] != updated_product['categoria_produto']
        assert result[4] != updated_product['validade']
    finally:
        cursor.close()
        conn.close()
