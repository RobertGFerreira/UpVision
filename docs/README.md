# Documentação e Governança do UpVision

Este diretório contém a documentação técnica aprofundada, manuais operacionais e políticas corporativas do ecossistema **UpVision**.

---

## Índice de Documentos

1. **[Arquitetura Detalhada](arquitetura.md)**: Topologia do sistema, camadas desacopladas, concorrência com threads, fila thread-safe e ciclo de vida da interface Tkinter.
2. **[Catálogo e Modelos de IA](modelos_ia.md)**: Detalhes das redes neurais Real-ESRGAN (`RRDBNet`), precisão mista FP16 (half) para GPU CUDA, download seguro e integridade de pesos.
3. **[Guia de Execução e Troubleshooting](guia_execucao.md)**: Instruções completas para execução automatizada com `run.bat` ou manual, diagnóstico de GPU e resolução de erros comuns.
4. **[Política de Commits](COMMIT_POLICY.md)**: Regras corporativas para mensagens de commit (Conventional Commits), atomicidade e exigência de autorização formal.
5. **[Segurança e Operação Crítica](seguranca-operacao.md)**: Políticas de proteção de dados locais (Zero-Data Leakage), isolamento de checkpoints e sanitização de caminhos.

---

> 🔒 **Propriedade Confidencial**: UpVision é um software comercial privado de Robert Ferreira. Todos os direitos reservados.
