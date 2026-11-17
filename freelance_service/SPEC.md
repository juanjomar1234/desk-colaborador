# Spec — MVP «Contratación freelance»

## 1. Descubrimiento

**Orden del CEO:** «Quiero contratar a un freelance para el proyecto».

**Problema:** hoy no existe en Desk Colaborador ningún flujo para publicar un encargo,
recibir propuestas de freelancers, compararlas y formalizar la contratación. Se hace por
email/hojas sueltas, sin trazabilidad ni criterio homogéneo.

**Usuarios:**

| Rol | Necesidad |
|---|---|
| CEO / responsable de proyecto | Publicar el encargo, comparar propuestas, contratar y seguir el contrato. |
| Freelance (externo) | Ver el encargo y enviar su propuesta (precio, plazo, enfoque) sin crear cuenta. |

**Supuestos del MVP:**
- Un proyecto se adjudica a **un único** freelance.
- El freelance se identifica por email (sin login); si repite email, se actualiza su ficha.
- Moneda única: EUR. Sin pagos online ni firma electrónica (fuera de alcance).
- El acceso al panel lo protege la capa de despliegue (staging tras login de la organización);
  la integración con `auth_service` (JWT) queda para la siguiente iteración.

## 2. Historias de usuario y criterios de aceptación

1. **Publicar proyecto.** Como responsable, publico título, descripción, habilidades,
   presupuesto (mín./máx.) y fecha límite.
   - Título, descripción y presupuesto máximo son obligatorios; mín. ≤ máx.; fecha `AAAA-MM-DD`.
   - Las habilidades se normalizan (minúsculas, sin duplicados).
2. **Recibir propuestas.** Como freelance, desde un enlace público envío nombre, email,
   habilidades, tarifa, portfolio, importe, plazo y mensaje.
   - Solo si el proyecto está `abierto`. Una propuesta por freelance y proyecto (409 si repite).
3. **Comparar.** Como responsable, veo las propuestas ordenadas por: % de encaje de
   habilidades ↓, dentro de presupuesto primero, importe ↑. Se marcan las que exceden presupuesto.
4. **Preseleccionar / rechazar.** Puedo mover propuestas entre `pendiente`,
   `preseleccionada` y `rechazada` mientras el proyecto esté abierto.
5. **Contratar.** Al contratar una propuesta: pasa a `aceptada`, el resto a `rechazada`,
   el proyecto a `contratado` y se crea un **contrato** `activo` con importe y fecha de inicio.
   No se puede contratar una propuesta rechazada ni un proyecto ya adjudicado/cerrado.
6. **Seguimiento.** Listado de contratos; al marcarlo `finalizado`, el proyecto pasa a `cerrado`.
7. **Cerrar sin contratar.** Cierra el proyecto y rechaza las propuestas abiertas.
8. **KPIs.** Proyectos abiertos, propuestas, pendientes, contratos activos y presupuesto comprometido.

## 3. Modelo de datos

```
Project(id, title, description, skills, budget_min, budget_max, deadline, status[abierto|contratado|cerrado])
Freelancer(id, name, email UNIQUE, skills, hourly_rate, portfolio_url)
Proposal(id, project_id, freelancer_id, amount, days, message, status[pendiente|preseleccionada|rechazada|aceptada])
         UNIQUE(project_id, freelancer_id)
Contract(id, project_id UNIQUE, proposal_id, amount, start_date, status[activo|finalizado])
```

## 4. Fuera de alcance (siguientes iteraciones)
- Login con `auth_service` y permisos por rol.
- Notificaciones por email al freelance (recepción, preselección, adjudicación).
- Hitos de pago, facturas y firma de contrato.
- Adjuntos (CV, portfolio en PDF).
