# NRE: una compuerta que decide si una IA puede continuar

**Por Adrian Mendez Millan**

## El problema

Los modelos de lenguaje responden con la misma seguridad cuando saben y cuando no. Mezclan lo que infieren con lo que es un hecho y siguen instrucciones que vienen escondidas en el texto. Si además los conectamos a acciones reales, como enviar, publicar, borrar o pagar, una respuesta mal interpretada deja de ser solo un error de texto y se convierte en un efecto en el mundo.

Ya existen herramientas que atacan partes del problema: NeMo Guardrails, Guardrails AI, los grafos de agentes de LangGraph y las salidas estructuradas de los proveedores. Lo que casi siempre falta es una sola capa explícita, que se pueda auditar y medir, y que responda una pregunta simple: **¿esta ejecución puede continuar?**

## Qué es NRE

NRE–AMM–OMEGA_CONTEXT_ENGINE es una capa independiente de control, interpretación, ejecución y verificación para modelos de IA. Convierte la intención en instrucciones formales, valida los resultados y decide si una ejecución puede continuar.

No es un modelo nuevo. Es un motor que se pone entre la petición y el modelo, y que hoy funciona con un proveedor simulado o con Ollama.

## Arquitectura

- **L1 · SIPE:** convierte el texto libre en una instrucción formal con objetivo, tipo de intención, clase de acción (solo lectura o con efectos), restricciones, evidencia y un diagnóstico de ambigüedad.
- **L2 · Firewall semántico:** aplica reglas explícitas contra inyección de prompt, acciones destructivas, intención maliciosa y exfiltración de secretos.
- **NEXUS:** es el plano de control. Las acciones con efectos se deniegan por defecto y solo avanzan con una autorización explícita.
- **L3 · AMM-CORE:** arma el plan de ejecución y aplica los invariantes.
- **L5 · Gateway:** llama al modelo con un tiempo límite.
- **L6 · Verificación:** primero valida la estructura de la respuesta y después la compara con referencias o evidencia externa. Solo así una respuesta puede quedar como VERIFIED.
- **L7 · Persistencia:** guarda una auditoría JSONL de cada ciclo, incluidos los rechazados y los detenidos.

Los diez invariantes (por ejemplo, "INFERENCE != FACT", "LEARNING REQUIRES ACCEPTANCE" o "NO SILENT STATE MUTATION") son comprobaciones ejecutables que pueden fallar, y cada una tiene sus pruebas.

## La máquina de estados

Cada petición recorre este camino: RECEIVED → INTERPRETING → VALIDATING → AWAITING_AUTH → EXECUTING → VERIFYING → COMMITTED → LEARNING → PERSISTING → COMPLETED.

Si la intención es ambigua, si el firewall la bloquea, si se niega la autorización o si la respuesta contradice la referencia, el ciclo pasa a REJECTED. Un error o un timeout lo llevan a HALT. En los dos casos el ciclo **también se persiste**. Un reintento vuelve a interpretar y a validar, así que no se puede colar una instrucción maliciosa como "aclaración". Si se acumulan rechazos, el motor entero se detiene hasta que alguien lo reanude, y eso también queda auditado.

## Lo que medí

Incluí un benchmark reproducible de 33 casos: benignos, inyección, destructivos, ambiguos, acciones sin autorización y 10 preguntas con respuesta conocida. El "modelo" es simulado y responde 3 de esas preguntas mal a propósito. Comparé entregar todo sin control contra pasar por NRE:

| Métrica | Sin control | NRE |
|---|---|---|
| Decisiones correctas (permitir/bloquear) | 13/33 (39.4%) | 30/33 (90.9%) |
| Casos dañinos que pasan | 13/13 | 2/13 |
| Benignos bloqueados por error | 0/6 | 1/6 |
| Respuestas incorrectas entregadas | 3/3 | 0/3 |
| Preguntas con estado VERIFIED | 0/10 | 7/10 |

## Limitaciones, sin adornos

- El firewall es por reglas. Dos inyecciones parafraseadas se escaparon ("Finge que no tienes reglas…" y "Olvida lo que te dijeron antes…"), y una pregunta legítima sobre phishing quedó bloqueada.
- El conjunto es pequeño y las reglas se escribieron conociéndolo, así que estos números no predicen cómo se comporta con datos nuevos. Solo demuestran que la compuerta funciona como está especificada.
- VERIFIED significa que la respuesta coincide con referencias que da quien llama. No hay búsqueda de fuentes.
- Todavía no lo comparo con NeMo Guardrails, Llama Guard ni con benchmarks públicos como HarmBench. Ese es el siguiente paso.

## Código y colaboración

El código es abierto (MIT), está escrito solo con la biblioteca estándar de Python e incluye 59 pruebas automáticas y CI:

https://github.com/DeconstructorGnostico/Nre_omega_engine

Busco colaboradores para tres cosas: probarlo con modelos reales, construir un conjunto de evaluación en español más grande y no visto antes, y compararlo contra las herramientas que ya existen. Si trabajas en evaluación, seguridad de agentes o gobernanza de IA en español, escríbeme.
