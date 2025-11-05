# Como Contribuir

Agradecemos o seu interesse em contribuir! Para manter o projeto organizado, seguimos algumas diretrizes simples baseadas no nosso Plano de Execução.

## Padrão de Commits

Este projeto utiliza o padrão **[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)**.

**Exemplos:**
- `feat: Adiciona endpoint de criação de tarefas`
- `fix: Corrige bug de paginação`
- `docs: Atualiza README com instruções`
- `chore: Configura pipeline de CI`
- `test: Adiciona testes para o serviço de usuário`

## Fluxo de Contribuição (Git Flow)

1.  **Branch Principal:** A branch `main` é protegida e reflete a versão em produção.
2.  **Branch de Integração:** A branch `develop` é a nossa base de integração. **Todo o trabalho deve ser direcionado a ela.**
3.  **Seu Trabalho:**
    - Crie sua branch a partir da `develop` (ex: `git checkout -b feat/minha-nova-feature develop`).
    - Faça seus commits (seguindo o padrão acima).
    - Envie um **Pull Request (PR)** da sua branch (`feat/minha-nova-feature`) para a `develop`.