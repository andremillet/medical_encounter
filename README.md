# Módulo de Encontro Médico

## Descrição

O **Módulo de Encontro Médico** é um componente independente de um sistema de Registro Médico Eletrônico (EMR) projetado para registrar e gerenciar visitas de pacientes de forma eficiente. Desenvolvido com Python e Flask, oferece aos profissionais de saúde uma ferramenta simples e compatível com a HIPAA para documentar detalhes críticos de encontros médicos, garantindo privacidade e autenticidade dos dados.

### Funcionalidades

#### Registro de Visitas de Pacientes
- Captura informações essenciais de um encontro, incluindo:
  - Nome do paciente
  - CPF (identificador brasileiro de 11 dígitos)
  - Anotações (ex.: histórico do paciente ou anamnese)
  - Hipótese diagnóstica
  - Conduta médica (plano de tratamento)
- Os dados são inseridos por meio de um formulário web intuitivo.

#### Segurança dos Dados
- Criptografa todos os dados sensíveis usando uma chave gerenciada pelo aplicativo, atendendo aos padrões da HIPAA para proteção de Informações de Saúde Protegidas (PHI).
- Armazena os dados criptografados em um banco de dados SQLite para um registro confiável e portátil.

#### Autenticação das Ações do Médico
- Exige que o médico assine o encontro com uma chave pessoal, gerando uma assinatura única para o arquivo `.med` criptografado (um relatório de encontro baseado em JSON).
- Isso vincula a autoridade do médico ao registro, assegurando autenticidade e responsabilidade.

#### Confirmação e Acesso
- Após submissão e assinatura, exibe uma prévia descriptografada do arquivo `.med` para revisão imediata pelo médico.
- Oferece um endpoint API (`/api/encounter/<id>`) para recuperar o arquivo `.med` criptografado e a assinatura, permitindo integração com outros módulos EMR.

#### Conduta Médica
- Permite adicionar múltiplas condutas médicas por encontro:
  - **Prescrição de Medicamentos**: Escolha o nome genérico (ex.: amitriptilina), dose e período de administração.
  - **Solicitação de Exames**: Autocompletar opções (ex.: "Ressonância Magnética") com campo para observações.
  - **Referência a Outros Profissionais/Serviços**: Autocompletar opções (ex.: "Cardiologia") com campo para observações.
- As condutas são exibidas em uma lista e podem ser confirmadas com o botão "Commit Conducts", gerando um arquivo `.med`.

#### Lista de Encontros
- Após finalizar um encontro, o usuário é redirecionado para `/encounters`, que lista todos os encontros com opção de baixar o arquivo `.med` associado.
- Inclui um botão "Novo Encontro" para iniciar um novo registro.

### Requisitos
- Python 3.x
- Bibliotecas: `flask`, `cryptography`
- Arquivos JSON simulados (`medications.json`, `exams.json`, `referrals.json`)

### Instalação
1. Clone o repositório: git clone https://github.com/[seu-usuario]/medical-encounter-module.git
   - Navegue até o diretório: cd medical-encounter-module
2. Instale as dependências: pip install flask cryptography
3. Execute o aplicativo: python app.py
4. Acesse `http://localhost:5000/encounter/new` no navegador.

### Estrutura do Projeto
- medical_encounter_module/
  - app.py                # Aplicativo Flask
  - templates/
    - encounter.html    # Formulário de encontro
    - encounters.html   # Lista de encontros
  - static/
    - style.css         # Estilização básica
  - medications.json      # Banco de dados simulado de medicamentos
  - exams.json            # Banco de dados simulado de exames
  - referrals.json        # Banco de dados simulado de referências
  - emr.db                # Banco de dados SQLite (gerado)

### Uso
1. Acesse `/encounter/new` para criar um novo encontro.
2. Preencha os dados do paciente e adicione condutas médicas.
3. Clique em "Commit Conducts" para finalizar, baixe o arquivo `.med` e escolha entre editar ou finalizar.
4. Ao finalizar, veja a lista de encontros em `/encounters` e baixe os arquivos `.med` conforme necessário.

### Conformidade
- **HIPAA**: Dados sensíveis são criptografados antes do armazenamento.
- **FHIR**: O arquivo `.med` é estruturado para facilitar conversão para protocolos FHIR.

### Próximos Passos
- Implementar autenticação de usuário.
- Substituir JSON por tabelas de banco de dados reais.
- Adicionar suporte a edição de encontros antes da finalização.

### Licença
Este projeto é de código aberto sob a licença MIT.

---

**Autor**: André Millet  
**Data**: 10 de Março de 2025
