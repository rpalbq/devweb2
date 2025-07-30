# 🎼 Registra.Mood🎶

##  Visão Geral do Projeto

O **Registra.Mood** é uma plataforma para ajudar indivíduos no acompanhamento de seu bem-estar emocional e mental. Através de uma interface intuitiva, usuários podem registrar seus estados de humor diariamente, associá-los a músicas e obter insights valiosos sobre sua jornada emocional.

Este projeto se destaca por sua **arquitetura de microsserviços**, construída com **Flask** para as APIs e **MongoDB** como banco de dados NoSQL. A orquestração via **Docker Compose** garante um ambiente de desenvolvimento e implantação coeso e eficiente.

## 🚀 Funcionalidades Principais

O Registra.Mood oferece um conjunto abrangente de funcionalidades, adaptadas para diferentes perfis de usuário:

### Para **Pacientes** 🧘‍♀️

* **Registro de Humor Diário:** Uma forma simples e visual de registrar seu estado emocional (via emojis) e adicionar comentários detalhados.
* **Associação Musical:** Conecte suas emoções a músicas específicas, criando uma trilha sonora para sua jornada de bem-estar.
* **Acompanhamento Pessoal:** Obtenha uma visão geral da sua evolução emocional ao longo do tempo.

### Para **Profissionais** 🧑‍⚕️

* **Acesso à Base de Pacientes:** Profissionais cadastrados têm acesso a uma lista de seus pacientes e podem visualizar seus registros.
* **Geração de Relatórios Abrangentes:**
    * **Relatórios em HTML:** Visualize no navegador um relatório interativo e detalhado do humor do paciente.
    * **Relatórios em PDF:** Baixe relatórios profissionais em formato PDF.
* **Análise de Tendências:** Ferramentas para identificar padrões e tendências nos estados emocionais dos pacientes, auxiliando no processo terapêutico.
* **Dashboard Profissional:** Uma área dedicada para gerenciar pacientes e acessar as funcionalidades de relatório de forma centralizada.

## 🏗️ Arquitetura de Microsserviços Detalhada

O Registra.Mood é composto por serviços desacoplados que comunicam entre si e com o banco de dados, orquestrados pelo Docker Compose.

### 1. **`app-main` (Serviço Principal)**
* **Tecnologia:** Flask (Python)
* **Função:** Este é o "coração" da aplicação. Ele serve a **interface do usuário (frontend)**, composta por HTML, CSS e JavaScript, e expõe as **APIs principais** para:
    * Autenticação e gerenciamento de **usuários** (cadastro, login, logout, diferenciando entre `paciente` e `profissional`).
    * Gerenciamento de **músicas** (cadastro, listagem).
    * Registro e consulta de **humores**.
    * Comunicação com o `report-service` para solicitar relatórios.
* **Interação com MongoDB:** Responsável pela persistência de dados de usuários, músicas e humores.

### 2. **`report-service` (Microsserviço de Relatórios e Análises)**
* **Tecnologia:** Flask (Python), ReportLab (para PDFs)
* **Função:** Um microsserviço especializado na **geração dinâmica de relatórios**. Recebe requisições do `app-main` (ou diretamente para testes) e:
    * Coleta dados de humor e usuário do MongoDB.
    * Processa esses dados para gerar **estatísticas e análises**.
    * Cria relatórios detalhados em **HTML** (visualizáveis no navegador).
    * Gera **documentos PDF** profissionais com os dados de humor, prontos para download.
* **Interação com MongoDB:** Consulta dados de usuários e humores para a elaboração dos relatórios.

### 3. **`mongo` (Banco de Dados MongoDB)**
* **Tecnologia:** MongoDB 
* **Função:** O repositório central de dados. Armazena de forma flexível:
    * Informações de **usuários** (pacientes e profissionais).
    * Registros de **humor** de cada paciente.
    * Detalhes das **músicas** cadastradas.

### 4. **`mongo-express` (Interface de Gerenciamento do MongoDB)**
* **Tecnologia:** mongo-express
* **Função:** Uma ferramenta web leve e amigável para **administrar e visualizar o banco de dados MongoDB**. Perfeito para inspeção durante o desenvolvimento e depuração.

## ⚙️ Como Rodar o Projeto (com Docker Compose)

Para colocar o Registra.Mood em funcionamento em sua máquina, você precisará ter o **Docker** e o **Docker Compose** instalados.

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/rpalbq/devweb2.git](https://github.com/rpalbq/devweb2.git)
    cd devweb2
    ```

2.  **Construa as Imagens e Inicie os Serviços:**
    No diretório raiz do projeto (onde o arquivo `docker-compose.yml` está localizado), execute o seguinte comando:
    ```bash
    docker-compose up --build
    ```
    Este comando irá:
    * Construir as imagens Docker personalizadas para o `app-main` e o `report-service` (com base nos `Dockerfile`s presentes em seus respectivos diretórios).
    * Baixar as imagens oficiais do `mongo` e `mongo-express` do Docker Hub.
    * Criar e iniciar todos os contêineres definidos no `docker-compose.yml` em uma rede isolada.

3.  **Acesse a Aplicação:**
    Uma vez que todos os serviços estejam em execução, você pode acessá-los através do seu navegador:
    * **Aplicação Principal (Registra.Mood):** `http://localhost:8080`
    * **Serviço de Relatórios (Endpoints de API):** `http://localhost:8081` (Para visualização direta de relatórios HTML, use `http://localhost:8081/report/<ID_DO_PACIENTE>` - o ID do paciente pode ser obtido via a API principal).
  

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído com as seguintes tecnologias:

* **Backend:** Python, Flask 
* **Banco de Dados:** MongoDB 
* **Orquestração de Contêineres:** Docker e Docker Compose 
* **Frontend:** HTML5, CSS3, JavaScript 
* **Geração de PDF:** ReportLab (

