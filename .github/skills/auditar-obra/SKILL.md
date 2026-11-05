---
name: auditar-obra
description: Auditar licença e condições de uso de uma obra ou curso individual, distinguindo política geral de exceções por componente antes de qualquer republicação ou uso em IA.
license: MIT
---

# Auditoria por obra

1. Confirmar a identidade da obra e sua URL canônica no site institucional.
2. Localizar a página oficial com termos/licença; guardar URL e data.
3. Distinguir **política geral do portal**, **licença da obra** e **licenças de elementos externos**.
4. Conferir exigências de atribuição, restrição não comercial, share-alike, autorização para IA, exceções para imagens, downloads, anexos.
5. Registrar o estado em `src/engmec/data/direitos.json`, marcando política geral ou licença de obra, sem declarar todos os assets revisados.
6. Padrão conservador: L0 (metadados e links). L1/L2 só com documentação de direitos e revisão jurídica quando necessária.
7. Acrescentar nota em `docs/governanca/auditoria-obras.md`; executar `engmec validar` e testes.
8. Nunca copiar a obra para justificar um status de auditoria; metadados suficientes e evidência primária são preferíveis.

**Aceite:** ID único, fonte primária, revisão datada, proibições explícitas e decisão de reuso.
