#!/usr/bin/env python3
"""
Testes de INTEGRAÇÃO — Módulo Carrinho (SQLite :memory:)
Aula 11 — Teste de Software (2026.1) | UniCode UniEvangelica

=======================================================================
⚠️  POR QUE ESTE ARQUIVO É DIFERENTE DE test_pagamentos.py?
=======================================================================

  test_pagamentos.py       →  TESTE UNITÁRIO
  ─────────────────────       ─────────────────────────────────────────
  • Testa funções puras       • Sem banco de dados real
  • Usa Stubs/Mocks            • Sem rede, sem arquivo externo
  • Rápido: < 1ms por teste   • Isola a LÓGICA de negócio

  test_carrinho_integracao.py →  TESTE DE INTEGRAÇÃO
  ────────────────────────────   ──────────────────────────────────────
  • Testa módulo + banco real  • SQLite real (em memória)
  • Sem Mocks — toca o banco!  • Verifica PERSISTÊNCIA dos dados
  • Um pouco mais lento        • Isola via fixture (banco novo p/ cada teste)

=======================================================================
"""

import sqlite3
import pytest
import sys
import os

# Garante que o pacote 'app' é encontrado independente de onde o aluno rodar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.carrinho_db import (
    criar_tabela,
    adicionar_item,
    listar_itens,
    calcular_total,
    limpar_carrinho,
)


# =====================================================================
# FIXTURE — Banco de dados isolado por teste
# =====================================================================

@pytest.fixture
def db():
    """
    Fixture que entrega uma conexão SQLite ':memory:' com a tabela
    'carrinho' já criada.

    O banco EM MEMÓRIA é:
      ✅ Criado do zero antes de cada teste (setup)
      ✅ Destruído automaticamente ao fim de cada teste (teardown)
      ✅ Completamente isolado — um teste não suja o outro
    """
    conn = sqlite3.connect(":memory:")   # banco vive apenas na RAM
    criar_tabela(conn)                   # cria a estrutura da tabela
    yield conn                           # entrega para o teste
    conn.close()                         # teardown: banco destruído aqui


# =====================================================================
# GRUPO 1 — Testes de Inserção e Persistência
# =====================================================================

def test_item_persiste_no_banco(db):

    #Arrange
    adicionar_item(db, "Café bão", 250.95, 2)

    #Act
    itens = listar_itens(db)

    #Assert
    assert len(itens) == 1
    assert itens[0]["nome"] == "Café bão"
    assert itens[0]["preco"] == 250.95
    assert itens[0]["quantidade"] == 2

    pass

def test_multiplos_itens_persistem(db):
    
    #arrange
    adicionar_item(db, "Arroz cristal", 25.99, 30)
    adicionar_item(db, "Feijão preto", 8.87, 54)
    adicionar_item(db, "Presunto fatiado", 19.99, 1)

    #Act
    itens = listar_itens(db)

    #Assert
    assert len(itens) == 3

    pass

def test_preco_negativo_lanca_value_error(db):
    """
    Assert: ValueError deve ser lançado
    Dica: use pytest.raises(ValueError)
    """
    
    with pytest.raises(ValueError, match="Preço não pode ser negativo"):
        adicionar_item(db, "Produto Inválido", -10.00, 1)

    pass


# =====================================================================
# GRUPO 2 — Testes de Cálculo de Total
# =====================================================================

def test_carrinho_vazio_retorna_zero(db):
    """
    Arrange: banco vazio (nenhum insert)
    Act + Assert: calcular_total retorna 0.0
    """
    
    assert calcular_total(db) == 0.0

    pass

def test_total_considera_quantidade(db):
    """
    Arrange: insere 3 unidades de R$ 50,00
    Assert: total == 150.0  (preco × quantidade)
    """
    
    adicionar_item(db, "Sal de parrilha", 29.95, 3)

    assert calcular_total(db) == 89.85

    pass

def test_total_multiplos_itens(db):
    """
    Arrange: 3 itens com preços e quantidades diferentes
    Assert: total == soma correta
    """
    
    #Arrange
    adicionar_item(db, "Macã", 10.00, 2) 
    adicionar_item(db, "Banana", 5.00, 3)  
    adicionar_item(db, "Melão", 50.00, 1) 

    #Assert
    assert calcular_total(db) == 85.0

    pass


# =====================================================================
# GRUPO 3 — Testes de Limpeza do Carrinho
# =====================================================================

def test_limpar_remove_todos_os_itens(db):
    """
    Arrange: adiciona 2 itens
    Act: limpa o carrinho
    Assert: listar_itens retorna [] e total retorna 0.0
    """
    
    adicionar_item(db, "Abacate", 10.00, 1)
    adicionar_item(db, "Pera", 99.99, 1)

    linhas = limpar_carrinho(db)

    assert linhas == 2
    assert listar_itens(db) == []
    assert calcular_total(db) == 0

    pass

def test_pode_adicionar_apos_limpar(db):
    """
    Arrange: adiciona, limpa, adiciona de novo
    Assert: somente o último item existe
    """
    
    #Arrange
    adicionar_item(db, "suco", 500.00, 1)
    limpar_carrinho(db)
    adicionar_item(db, "vinho", 100.00, 1)

    #Act
    itens = listar_itens(db)

    #Assert
    assert len(itens) == 1
    assert itens[0]["nome"] == "vinho"
    assert calcular_total(db) == 100.00

    pass