# 🚀 Guia: Push para GitHub

## Commits Criados ✅

```
9b8a8c5 chore: Estrutura de diretórios do projeto
825af56 build: Dependências do projeto
9bbf92b build: Scripts de verificação e setup
2ebe9ca feat: Implementação dos módulos principais
0ff26d4 docs: Documentação inicial e configuração
```

## Próximos Passos

### 1️⃣ Criar Repositório no GitHub

**Opção A: Via Web Browser (Recomendado para iniciante)**

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `graphrag-interface` (ou outro nome)
   - **Description**: GraphRAG Interface with Streamlit
   - **Public** ou **Private**: Escolha
   - **Add a README**: NÃO marque (já temos)
   - **Add .gitignore**: NÃO marque (já temos)
3. Clique: **Create repository**
4. Copie a URL mostrada (ex: `https://github.com/seu-usuario/graphrag-interface.git`)

**Opção B: Via GitHub CLI**

```powershell
# Instalar: https://cli.github.com/
gh repo create graphrag-interface --public --source=. --remote=origin --push
```

### 2️⃣ Configurar Remote e Fazer Push

Se usou a Opção A:

```powershell
cd c:\Users\Felipe\Desktop\meu_projeto

# Adicionar remote (substitua pelo seu)
git remote add origin https://github.com/SEU-USUARIO/SEU-REPO.git

# Renomear branch master para main (opcional, GitHub padrão)
git branch -M main

# Fazer push
git push -u origin main
```

### 3️⃣ Autenticação GitHub

**Opção 1: Token de Acesso Pessoal (PAT) - Recomendado**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click: **Generate new token (classic)**
3. Selecione escopos: `repo` (acesso completo a repositórios)
4. Copie o token
5. No terminal, quando pedir senha:
   ```
   Username: seu-usuario-github
   Password: cole-o-token-aqui
   ```

**Opção 2: SSH (Mais seguro)**

```powershell
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@example.com"

# Adicionar ao SSH agent
ssh-agent
ssh-add ~/.ssh/id_ed25519

# Adicionar chave pública ao GitHub
cat ~/.ssh/id_ed25519.pub
# Copie e adicione em: GitHub → Settings → SSH Keys

# Use SSH URL ao adicionar remote
git remote add origin git@github.com:SEU-USUARIO/SEU-REPO.git
```

### 4️⃣ Exemplo Completo (PAT)

```powershell
cd c:\Users\Felipe\Desktop\meu_projeto

# Configurar remote
git remote add origin https://github.com/felipedeveloper/graphrag-interface.git

# Verificar
git remote -v

# Fazer push
git push -u origin master
# OU se renomeou para main:
git branch -M main
git push -u origin main
```

Quando pediri credenciais:
- **Username**: seu-usuario-github
- **Password**: seu-token-pessoal

### 5️⃣ Verificar Status

```powershell
# Ver branches remotos
git branch -v

# Ver histórico com remote
git log --oneline --all --decorate
```

## Pronto! 🎉

Seu repositório estará no GitHub com todos os 5 commits:

```
✅ docs: Documentação inicial e configuração
✅ feat: Implementação dos módulos principais
✅ build: Scripts de verificação e setup
✅ build: Dependências do projeto
✅ chore: Estrutura de diretórios do projeto
```

## Próximos Commits Futuros

```powershell
# Fazer alterações
git add .
git commit -m "tipo: mensagem descritiva"

# Fazer push
git push
```

## Tipos de Commit (Conventional Commits)

- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Documentação
- **style**: Formatação
- **refactor**: Refatoração
- **test**: Testes
- **chore**: Manutenção
- **build**: Build/Dependências

---

**Precisa de ajuda?** Consulte:
- https://docs.github.com/en/get-started/quickstart/create-a-repo
- https://docs.github.com/en/authentication/connecting-to-github-with-ssh
