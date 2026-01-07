# Odoo Blockchain Certificación de Cursos

**Nombre Técnico**: `odoo_certificacion_cursos`  
**Dependencias**: `odoo_blockchain_core`, `website_slides`, `sale`, `survey`

Este módulo extiende la funcionalidad de eLearning de Odoo para permitir la **Certificación Notarizada en Blockchain** de los diplomas de cursos.

---

## 🚀 Características Principales

1.  **Certificación de PDF**: No se certifican datos sueltos, sino el **Archivo PDF (Diploma)** exacto que se genera al aprobar. Esto garantiza que el diseño y contenido visual del diploma es inmutable.
2.  **Monetización (Upsell)**: Permite vender el mismo curso con o sin certificación blockchain usando **Variantes de Producto**.
3.  **Registro Automático**: Si el alumno tiene derecho (compró la variante correcta), el diploma se envía a la blockchain automáticamente al aprobar.
4.  **Revocación Integrada**: Permite al gestor revocar un certificado desde la propia encuesta si hubo errores o fraude.

---

## ⚙️ Guía de Configuración

### 1. Configurar Producto (eCommerce)

Para cobrar un extra por la certificación:

1.  Vaya a **Sitio Web > eCommerce > Productos**.
2.  Cree o edite el producto asociado a su Curso.
3.  Añada un **Atributo** (ej. "Tipo de Certificado") con dos valores: "Estándar" y "Blockchain".
4.  En "Valores Extra de Precio", asigne el coste adicional a la opción "Blockchain".

> **Importante**: El sistema busca la cadena de texto "Blockchain" (insensible a mayúsculas) en el nombre de la variante seleccionada para activar el derecho.

### 2. Configurar Curso

1.  Vaya a **eLearning > Cursos**.
2.  Seleccione su curso.
3.  Marque la casilla **"Blockchain Certification Active"**.

### 3. Configurar Certificación

El curso debe tener una certificación (Encuesta) asociada en sus contenidos.

1.  Asegúrese de que el contenido tipo "Certificación" tiene una plantilla de diploma PDF configurada.

---

## 🔄 Flujo de Uso

1.  **Compra**: El alumno selecciona "Tipo: Blockchain" en la tienda y paga.
2.  **Derechos**: El sistema marca la inscripción (`slide.channel.partner`) con `Entitled to Blockchain Cert = True`.
3.  **Examen**: El alumno aprueba la certificación.
4.  **Generación**: Odoo genera el PDF del diploma y lo adjunta.
5.  **Hashing**: El módulo calcula el SHA-256 del archivo PDF.
6.  **Cola**: Se crea una petición de registro en `Blockchain Core`.
7.  **Confirmación**: Unos minutos después, el Chatter de la encuesta muestra "Document CONFIRMED on Blockchain".

---

## 🛡️ Revocación

Si necesita invalidar un diploma:

1.  Vaya a **Encuestas > Participaciones**.
2.  Entre en la participación del alumno.
3.  Pulse el botón rojo **"Revoke Blockchain Cert"**.
4.  El estado pasará a `Revocation Pending` -> `Revoked` tras confirmación en red.
