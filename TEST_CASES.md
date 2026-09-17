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
| TC-006 | Listado de productos excluye agotados | PASÓ |
| TC-007 | Detalle de producto inexistente devuelve 404 | PASÓ |
| TC-008 | Página de inicio carga correctamente | PASÓ |
| TC-009 | Rechazo al agregar producto sin stock suficiente | PASÓ |
| TC-010 | Aplicación de la mejor promoción disponible | PASÓ |
| TC-011 | Confirmación de orden genera número y descuenta stock | PASÓ |
| TC-012 | Acceso restringido a la orden de otro usuario | PASÓ |

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

## TC-006 - Listado de productos excluye agotados

### Objetivo

Verificar que el listado de productos no muestre productos sin stock.

### Datos de prueba

- Producto disponible: stock 5
- Producto agotado: stock 0

### Acción

Se hace `GET` a `products:product_list`.

### Resultado esperado

Solo el producto con stock disponible aparece en el contexto.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/products/tests.py`

Método:

`ProductListViewTestCase.test_excludes_out_of_stock_products`

---

## TC-007 - Detalle de producto inexistente devuelve 404

### Objetivo

Verificar que pedir el detalle de un producto que no existe devuelva
un error 404 en lugar de romper.

### Datos de prueba

- `product_id` inexistente en la base de datos

### Acción

Se hace `GET` a `products:product_detail` con un id inválido.

### Resultado esperado

La respuesta HTTP es 404.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/products/tests.py`

Método:

`ProductDetailViewTestCase.test_returns_404_for_missing_product`

---

## TC-008 - Página de inicio carga correctamente

### Objetivo

Verificar que la página de inicio responda correctamente sin depender
de datos de productos o categorías en la base de datos.

### Datos de prueba

- Ninguno (base de datos vacía de productos/categorías)

### Acción

Se hace `GET` a `core:home` (raíz del sitio).

### Resultado esperado

- La respuesta HTTP es 200.
- Se usa el template `core/home.html`.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/core/tests.py`

Método:

`HomeViewTestCase.test_home_returns_200`

---

## TC-009 - Rechazo al agregar producto sin stock suficiente

### Objetivo

Verificar que no se pueda agregar al carrito una cantidad mayor a la
disponible en inventario.

### Datos de prueba

- Producto con stock: 10
- Cantidad solicitada: 11

### Acción

Se ejecuta el método `add_product()` de la orden con una cantidad
mayor al stock disponible.

### Resultado esperado

Se lanza una `ValidationError` y el producto no se agrega al carrito.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/orders/tests.py`

Método:

`OrderCartFlowTestCase.test_add_product_with_insufficient_stock_raises`

---

## TC-010 - Aplicación de la mejor promoción disponible

### Objetivo

Verificar que, existiendo varias promociones activas, se aplique la
que ofrece el mayor descuento entre las que realmente aplican al
subtotal de la orden.

### Datos de prueba

- Promoción "Baja": descuento fijo de 5
- Promoción "Alta": descuento fijo de 50
- Promoción "Inactiva": descuento fijo de 100, `is_active=False`
- Promoción "MinimoAlto": descuento fijo de 200, compra mínima muy alta
- Subtotal de la orden: 100

### Acción

Se ejecuta `find_best_promotion(subtotal)` sobre la orden.

### Resultado esperado

Se selecciona la promoción "Alta", ignorando la inactiva y la que no
aplica por compra mínima.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/orders/tests.py`

Método:

`OrderCalculationsTestCase.test_find_best_promotion_picks_highest_applicable_discount`

---

## TC-011 - Confirmación de orden genera número y descuenta stock

### Objetivo

Verificar que al confirmar una orden se genere un número de orden
único, se descuente el stock de los productos y la orden pase a
estado "Pendiente de pago".

### Datos de prueba

- Producto con stock: 10, precio: 100
- Cantidad en el carrito: 3

### Acción

Se ejecuta `confirm()` sobre la orden.

### Resultado esperado

- El número de orden sigue el formato `ORD-AAAAMMDD-000001`.
- El stock del producto queda en 7.
- El estado de la orden pasa a "Pendiente de pago".
- Se calculan correctamente `final_subtotal` y `final_total`.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/orders/tests.py`

Método:

`OrderConfirmTestCase.test_confirm_happy_path`

---

## TC-012 - Acceso restringido a la orden de otro usuario

### Objetivo

Verificar que un usuario no pueda ver la página de pago de una orden
que pertenece a otro usuario.

### Datos de prueba

- Usuario A confirma una orden.
- Usuario B intenta ver la página de pago de la orden de A.

### Acción

El usuario B hace `GET` a `orders:pagepay` con el `pk` de la orden
del usuario A.

### Resultado esperado

La respuesta HTTP es 404.

### Resultado obtenido

**PASÓ**

### Prueba automatizada

`apps/orders/tests.py`

Método:

`OrderViewsTestCase.test_payment_page_isolated_per_user`

---

## Resultado general

Para ejecutar todas las pruebas se utilizó:

```bash
python manage.py test
Found 86 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
......................................................................................
----------------------------------------------------------------------
Ran 86 tests in 28.202s

OK
Destroying test database for alias 'default'...
```