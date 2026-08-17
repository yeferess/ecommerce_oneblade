

```
# Casos de Prueba - OneBlade Ecommerce

## Objetivo

Documentar las pruebas realizadas sobre las funcionalidades principales
del sistema.

## Resumen

| ID | Funcionalidad | Resultado |
|---|---|---|
| TC-001 | Agregar producto al carrito | PASÓ |
| TC-002 | Registro válido | PASÓ |
| TC-003 | Registro inválido | PASÓ |
| TC-004 | Inicio de sesión válido | PASÓ |
| TC-005 | Inicio de sesión inválido | PASÓ |

---

## TC-001 - Agregar producto al carrito

### Objetivo

Verificar que un producto pueda agregarse correctamente al carrito.

### Datos de prueba

- Usuario: yefer
- Producto: WMARK 133
- Precio: 150000
- Stock: 10
- Cantidad: 1

### Acción

Se ejecuta el método `add_product()` de la orden.

### Resultado esperado

- Se agrega un producto a la orden.
- La cantidad es 1.
- El producto corresponde al seleccionado.
- El precio corresponde al producto.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/orders/tests.py`

Método:

`OrderTestCase.test_add_new_product_to_cart`

---

## TC-002 - Registro de usuario válido

### Objetivo

Verificar que un usuario pueda registrarse utilizando datos válidos.

### Datos de prueba

- Usuario: yefer
- Email: yefer@test.com
- Contraseña: UnaClaveSegura123!

### Acción

Se envía una petición POST al endpoint de registro.

### Resultado esperado

- El usuario es creado.
- El usuario queda autenticado.
- El sistema redirige al inicio.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/users/tests.py`

Método:

`UserTestCase.test_register_user`

---

## TC-003 - Registro de usuario inválido

### Objetivo

Verificar que el sistema maneje correctamente datos inválidos
durante el registro.

### Datos de prueba

- Usuario: vacío
- Email: correo-invalido
- Contraseña: 123
- Confirmación: 456

### Acción

Se envía una petición POST con datos inválidos.

### Resultado esperado

El formulario debe volver a mostrarse con los errores correspondientes
y la vista debe devolver una respuesta HTTP válida.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/users/tests.py`

Método:

`UserTestCase.test_register_invalid_form`

---

## TC-004 - Inicio de sesión válido

### Objetivo

Verificar que un usuario pueda iniciar sesión utilizando credenciales
correctas.

### Datos de prueba

- Usuario: yefer
- Contraseña: 12345678

### Acción

Se envía una petición POST al endpoint de inicio de sesión.

### Resultado esperado

- El usuario es autenticado.
- Se crea la sesión.
- El usuario es redirigido al inicio.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/users/tests.py`

Método:

`UserTestCase.test_user_login`

---

## TC-005 - Inicio de sesión inválido

### Objetivo

Verificar que un usuario no pueda iniciar sesión utilizando
credenciales incorrectas.

### Datos de prueba

- Usuario: yefer
- Contraseña correcta: 12345678
- Contraseña enviada: contraseña_incorrecta

### Acción

Se envía una petición POST utilizando una contraseña incorrecta.

### Resultado esperado

- La autenticación debe fallar.
- El usuario no debe quedar autenticado.
- Se debe mostrar nuevamente el formulario de inicio de sesión.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/users/tests.py`

Método:

`UserTestCase.test_user_login_invalid_credentials`

---

## Resultado general

Para ejecutar todas las pruebas se utilizó:

```bash

python manage.py test apps.orders.tests apps.users.tests
Found 5 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....
----------------------------------------------------------------------
Ran 5 tests in 3.242s

OK
Destroying test database for alias 'default'...
(ecommerce_oneblade) 

python manage.py test
Found 5 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....
----------------------------------------------------------------------
Ran 5 tests in 3.501s

OK
Destroying test database for alias 'default'...
(ecommerce_oneblade) 