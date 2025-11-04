## Requisitos de Negócio: Fluxo de Cadastro CompraJá! (CNPJ / CPF)

### 1. Visão Geral
Este documento detalha os requisitos funcionais para o fluxo de cadastro de novos usuários no sistema web "CompraJá!". O fluxo deve permitir o cadastro de Pessoas Jurídicas (via CNPJ) e Pessoas Físicas (via CPF).


#### Pilha de Tecnologia (Informada):

- Backend: Python (FastAPI)

- Frontend: JinjaTemplates + HTMX

### 2. Fluxo Geral de Cadastro
O fluxo se inicia em uma página de seleção única, onde o usuário opta pelo tipo de cadastro.

Página 0: Seleção de Tipo de Cadastro

Objetivo: Permitir ao usuário escolher entre cadastro empresarial ou pessoal.

#### Componentes:

- Botão/Caixa de seleção: "CNPJ".

- Botão/Caixa de seleção: "CPF".


- Lógica: Ao clicar em uma das opções, o usuário é direcionado para o formulário correspondente.

#### Validação (Nesta Página):

- O documento sugere uma forma de validação nesta página inicial.

- Opções mencionadas: "um código por e-mail" OU "aquele botão 'Não sou robô'".

- Nota do Arquiteto: É necessário definir qual método será implementado. As etapas seguintes (CNPJ e CPF) também solicitam uma confirmação "Não sou robô" no final.

### 3. Fluxo 1: Cadastro CNPJ (Pessoa Jurídica)
Processo dividido em duas etapas.

#### 3.1. CNPJ - Etapa 1: Dados do Negócio e Contato 
Campos do Formulário:

- qual_seu_negocio


- - Label: Qual o seu negócio? 

- - Tipo: Seleção (Dropdown/Lista)

- - Opções: Academia, adega, bar, bomboniere, cantina, clube esportivo, condomínio, confeitaria, doceria, dogueiro, escola, food service, hotel, instituição religiosa, lanchonete, mercearia, mini mercado, padaria, pastelaria, pizzaria, restaurante, outros.

- - Obrigatório: Sim.

- cnpj


- - Label: CNPJ? 

- - Tipo: Texto (Aplicar máscara e validação de CNPJ)

- - Obrigatório: Sim.

- razao_social


- - Label: Razão Social? 

- - Tipo: Texto

- - Obrigatório: Sim.

- seu_nome


- - Label: Seu nome? 

- - Tipo: Texto

- - Obrigatório: Sim.

- sua_funcao


- - Label: Sua função na empresa? 

- - Tipo: Seleção (Dropdown/Lista)

- - Opções: Proprietário, Gerente, estoquista. (Nota: expandir opções?)

- - Obrigatório: Sim.

- email


- - Label: E-mail

- - Tipo: Texto (Validação de e-mail)

- - Obrigatório: Sim.

- celular


- - Label: Celular 

- - Tipo: Texto (Aplicar máscara de telefone)

- - Obrigatório: Sim.

- Termos e Comunicações:


- - Checkbox (Obrigatório): Concordar com os termos da "Política de Privacidade".


- - Pendência: O documento de Política de Privacidade ainda será desenvolvido.


- - Checkbox (Opcional): "Receber e-mails com promoção e divulgação de material desta empresa e seus parceiros".

- Navegação:

- - Botão "voltar página".

- - Botão "avançar".

#### 3.2. CNPJ - Etapa 2: Endereço e Finalização 
Campos do Formulário:

- cep


- - Label: CEP

- - Tipo: Texto (Aplicar máscara).

- - Nota do Arquiteto: Recomenda-se implementar auto-preenchimento dos campos de endereço via HTMX (htmx-trigger="blur" no campo CEP).

- endereco


- - Label: Endereço

- - Tipo: Texto.

- bairro


- - Label: Bairro

- - Tipo: Texto.

- cidade


- - Label: Cidade? 

- - Tipo: Texto.

- estado


- - Label: Estado? 

- - Tipo: Dropdown de UFs.

- Validação e Submissão:


- - Validação: "Confirmar que não é um robô" (Ex: reCAPTCHA).


- Ação: Botão "finalizar cadastro".

### 4. Fluxo 2: Cadastro CPF (Pessoa Física)
Processo também dividido em duas etapas.

#### 4.1. CPF - Etapa 1: Dados Pessoais e Perfil 
Campos do Formulário:

- perfil_compra


- - Label: Você compra para: 

- - Tipo: Seleção (Radio Button)

- - Opções:

- - - Sua casa

- - - Seu negócio

- - - Para ambos

- - Obrigatório: Sim.

- qual_negocio_cpf (Campo Condicional)


- - Lógica: Deve aparecer se perfil_compra for "Seu negócio".

- - Label: Qual o negócio dele?  (Sugestão: "Qual o seu negócio?")

- - Tipo: Texto.

- cpf


- - Label: CPF

- - Tipo: Texto (Aplicar máscara e validação de CPF)

- - Obrigatório: Sim.

- nome_completo


- - Label: Nome completo

- - Tipo: Texto

- - Obrigatório: Sim.

- email


- - Label: E-mail

- - Tipo: Texto (Validação de e-mail)

- - Obrigatório: Sim.

- genero


- - Label: Gênero? 

- - Tipo: Seleção (Dropdown/Lista)

- - Opções: Feminino, masculino, outros, não quero me identificar.

- - Obrigatório: Sim.

- celular


- - Label: Celular

- - Tipo: Texto (Aplicar máscara de telefone)

- - Obrigatório: Sim.

- Termos e Comunicações:


- - Checkbox (Obrigatório): Concordar com os termos da "Política de Privacidade".


- - Pendência: O documento de Política de Privacidade ainda será desenvolvido.


- - Checkbox (Opcional): "Receber e-mails com promoção e divulgação de material da CompraJá e seus parceiros".

- Navegação:

- - Botão "voltar página".

- - Botão "avançar".

#### 4.2. CPF - Etapa 2: Dados Adicionais e Endereço 
Campos do Formulário:

- data_nascimento


- - Label: Data de nascimento

- - Tipo: Data (Date picker).

- cep


- - Label: CEP? 

- - Tipo: Texto (Aplicar máscara).

- - Nota do Arquiteto: Reutilizar o componente de auto-preenchimento de endereço (HTMX).

- endereco


- - Label: Endereço

- - Tipo: Texto.

- bairro


- - Label: Bairro

- - Tipo: Texto.

- cidade


- - Label: Cidade

- - Tipo: Texto.

- estado


- - Label: Estado

- - Tipo: Dropdown de UFs.

- Validação e Submissão:


- - Validação: "Confirmar que não é um robô" (Ex: reCAPTCHA).


- Ação: Botão "finalizar cadastro".

### 5. Notas para Arquitetura

- Componentes Reutilizáveis: O formulário de endereço e o bloco de consentimento (Privacidade e Marketing)  são idênticos em ambos os fluxos e devem ser criados como componentes Jinja/HTMX reutilizáveis.



- Fluxo HTMX: A natureza de "2 etapas"  dos formulários se alinha bem com o HTMX para validação da Etapa 1 e carregamento da Etapa 2 sem um full page reload. O botão "avançar"  pode disparar um hx-post para validar e retornar o fragmento da Etapa 2.


- Validação:

- - Frontend: Máscaras (CPF/CNPJ/CEP/Celular) e validação de tipo (e-mail, data).


- - Backend (FastAPI): Validação robusta (Pydantic models) para todos os campos obrigatórios, formato de CPF/CNPJ, e unicidade (E-mail, CPF, CNPJ).


- - Anti-Bot: Definir a implementação do "Não sou robô" (ex: Google reCAPTCHA) e o local exato da validação inicial.



- Consulta Externa: A funcionalidade de auto-preenchimento de CEP  exigirá uma integração com uma API externa (ex: ViaCEP). Isso pode ser tratado no backend (FastAPI) com um endpoint dedicado que o HTMX possa consultar.